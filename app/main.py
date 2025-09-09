# backend/app/main.py
import structlog
import datetime
from typing import Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings
from .core.logging_config import configure_logging
from .core.exceptions import BaseAPIException
from .database.connection import async_engine as engine
from .models.base import Base
from .api.v1.router import api_router
from .middleware.cors import setup_cors
from .middleware.rate_limiting import setup_rate_limiting, limiter
from .middleware.request_logging import RequestLoggingMiddleware
from .schemas.common import HealthCheck, ErrorResponse, ValidationErrorResponse
from .utils.formatters import format_api_response

# Configure logging
configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Meeting Summarizer API", version=settings.VERSION)

    try:
        import app.models
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down Meeting Summarizer API")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Setup middleware
setup_cors(app)
setup_rate_limiting(app)
app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle custom API exceptions"""
    logger.warning(
        "API exception occurred",
        error_code=exc.error_code,
        detail=exc.detail,
        status_code=exc.status_code,
        path=request.url.path
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=format_api_response(
            success=False,
            message=str(exc.detail),
            error_code=exc.error_code
        ),
        headers=exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors safely by sanitizing the error structure so that
    it is always JSON serializable. This avoids crashes when `ctx` or other fields
    contain non-serializable objects (e.g. AssertionError instances).
    """

    # Helper to sanitize arbitrary objects into JSON-serializable values
    def _sanitize_value(v: Any) -> Any:
        # Primitive JSON-serializable types
        if v is None or isinstance(v, (str, int, float, bool)):
            return v
        # Recurse into dicts and lists/tuples/sets
        if isinstance(v, dict):
            return {str(k): _sanitize_value(val) for k, val in v.items()}
        if isinstance(v, (list, tuple, set)):
            return [_sanitize_value(i) for i in v]
        # For exceptions, convert to a readable string
        if isinstance(v, BaseException):
            try:
                # include exception type and message
                return {"type": v.__class__.__name__, "message": str(v)}
            except Exception:
                return f"<exception-{v.__class__.__name__}>"
        # Fallback: convert unknown types to string (safe)
        try:
            return str(v)
        except Exception:
            # Last resort: type name
            return f"<non-serializable-{type(v).__name__}>"

    def _sanitize_error(err: Any) -> dict:
        # If error is not a dict, just return a single message field
        if not isinstance(err, dict):
            return {"msg": str(err)}

        sanitized = {}
        # Standard keys: loc, msg, type, ctx, input (if present)
        for key in err.keys():
            if key == "ctx":
                sanitized["ctx"] = _sanitize_value(err.get("ctx"))
            elif key == "input":
                # input can be large or contain complex objects; sanitize
                sanitized["input"] = _sanitize_value(err.get("input"))
            else:
                sanitized[key] = _sanitize_value(err.get(key))
        return sanitized

    # Extract raw errors safely
    try:
        raw_errors = exc.errors()
    except Exception as e:
        # If extracting errors fails for whatever reason, provide a fallback
        raw_errors = [{"msg": "Failed to extract validation errors", "error": str(e)}]

    sanitized_errors = [_sanitize_error(e) for e in raw_errors]

    # Log sanitized errors for debugging
    logger.warning(
        "Validation error occurred (sanitized)",
        errors=sanitized_errors,
        path=request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": sanitized_errors,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle FastAPI's internal HTTP exceptions."""
    logger.warning(
        "HTTP exception occurred",
        detail=exc.detail,
        status_code=exc.status_code,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=format_api_response(
            success=False,
            message=exc.detail,
            error_code="HTTP_ERROR"
        )
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(
        "Database error occurred",
        error=str(exc),
        path=request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_api_response(
            success=False,
            message="Database error occurred" if settings.DEBUG else "Internal server error",
            error_code="DATABASE_ERROR"
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_api_response(
            success=False,
            message=str(exc) if settings.DEBUG else "Internal server error",
            error_code="INTERNAL_ERROR"
        )
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheck, tags=["health"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT
    )


# Root endpoint
@app.get("/", tags=["root"])
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs" if settings.DEBUG else None
    }


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)
