# Application constants
# backend/app/utils/constants.py
from enum import Enum


class ResponseMessages:
    # Success messages
    USER_CREATED = "User created successfully"
    USER_UPDATED = "User updated successfully"
    USER_DELETED = "User deleted successfully"
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    PASSWORD_UPDATED = "Password updated successfully"
    
    # Error messages
    USER_NOT_FOUND = "User not found"
    INVALID_CREDENTIALS = "Invalid email or password"
    USER_ALREADY_EXISTS = "User already exists"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "Insufficient permissions"
    VALIDATION_ERROR = "Validation error"
    INTERNAL_ERROR = "Internal server error"


class ErrorCodes:
    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_EXISTS = "USER_EXISTS"
    USER_INACTIVE = "USER_INACTIVE"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_EMAIL = "INVALID_EMAIL"
    WEAK_PASSWORD = "WEAK_PASSWORD"
    
    # System errors
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class UserRoles:
    ATTENDEE = "attendee"
    MANAGER = "manager"


class TokenTypes:
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFICATION = "verification"