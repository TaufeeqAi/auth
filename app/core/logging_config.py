# backend/app/core/logging_config.py
import sys
import logging.config
import structlog
from .config import settings

def configure_logging():
    """
    Configure stdlib logging to route through structlog's ProcessorFormatter.
    Exceptions will be captured by format_exc_info when `logger.exception`
    (or exc_info=True) is used.
    """

    # choose renderer: human-friendly for dev, JSON for production
    renderer = structlog.dev.ConsoleRenderer(colors=settings.is_development) \
        if settings.is_development else structlog.processors.JSONRenderer()

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # stdlib formatter that delegates to structlog's ProcessorFormatter
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                # the processor will render the event dict to a string
                "processor": renderer,
                # processors that run for non-structlog loggers (pre-chain)
                "foreign_pre_chain": [
                    # add useful context fields before structlog processors run
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.ExtraAdder(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    # include stack info and formatted exception info if present
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                ],
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": settings.LOG_LEVEL,
                # ensure output goes to STDOUT (helpful in Docker / CI)
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "INFO" if settings.is_development else "WARNING",
                "propagate": False,
            },
        },
    })

    # Configure structlog itself (this affects structlog.get_logger())
    structlog.configure(
        processors=[
            # Filter by level before anything else (avoid expensive ops for filtered messages)
            structlog.stdlib.filter_by_level,
            # Attach standard logging level and logger name
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.ExtraAdder(),
            # Attach timestamp & optional stack info
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            # Convert exc_info into a string field on the event dict
            structlog.processors.format_exc_info,
            # Finally wrap into ProcessorFormatter-compatible format
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
