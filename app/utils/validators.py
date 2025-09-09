# Data validation utilities
# backend/app/utils/validators.py
import re
from typing import Optional
from pydantic import validator
from email_validator import validate_email, EmailNotValidError


def validate_email_address(email: str) -> str:
    """Validate email address format"""
    try:
        validated_email = validate_email(email)
        return validated_email.email
    except EmailNotValidError:
        raise ValueError("Invalid email address")


def validate_password_strength(password: str) -> str:
    """Validate password meets security requirements"""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    
    return password


def validate_username(username: str) -> str:
    """Validate username format"""
    if not re.match(r"^[a-zA-Z0-9_]{3,30}$", username):
        raise ValueError(
            "Username must be 3-30 characters and contain only letters, numbers, and underscores"
        )
    return username


def validate_phone_number(phone: Optional[str]) -> Optional[str]:
    """Validate phone number format"""
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)
    
    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        raise ValueError("Phone number must be 10-15 digits")
    
    return digits_only