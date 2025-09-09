
### backend/app/utils/biometric_validators.py
"""Biometric data validation utilities"""

import re
import base64
import hashlib
from typing import Optional, Dict, Any


class BiometricValidator:
    @staticmethod
    def validate_fingerprint_template(template: str) -> bool:
        """Validate fingerprint template format"""
        try:
            # Check if it's valid base64
            decoded = base64.b64decode(template)
            
            # Basic length check (fingerprint templates are usually 500+ bytes)
            if len(decoded) < 100:
                return False
                
            # Additional validation could include:
            # - Template format verification
            # - Checksum validation
            # - Biometric standard compliance
            
            return True
            
        except Exception:
            return False

    @staticmethod
    def validate_face_id_data(face_data: str) -> bool:
        """Validate Face ID biometric data"""
        try:
            decoded = base64.b64decode(face_data)
            
            # Basic validation
            if len(decoded) < 50:
                return False
                
            return True
            
        except Exception:
            return False

    @staticmethod
    def generate_biometric_hash(biometric_data: str, salt: str) -> str:
        """Generate secure hash of biometric data"""
        combined = f"{biometric_data}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def validate_public_key(public_key: str) -> bool:
        """Validate biometric public key format"""
        try:
            decoded = base64.b64decode(public_key)
            
            # Basic validation
            if len(decoded) < 32:  # Minimum key length
                return False
                
            return True
            
        except Exception:
            return False
