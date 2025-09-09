
### backend/app/utils/social_auth.py
"""Social login helpers"""

import httpx
import jwt
from typing import Dict, Any, Optional
from ..core.config import get_settings

settings = get_settings()


class GoogleOAuth:
    @staticmethod
    async def verify_token(access_token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
                )
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            print(f"Google token verification failed: {e}")
            
        return None

    @staticmethod
    async def get_user_info(user_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get additional user information from Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            print(f"Failed to get Google user info: {e}")
            
        return None


class AppleOAuth:
    @staticmethod
    async def verify_token(id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Apple ID token"""
        try:
            # Get Apple's public keys
            async with httpx.AsyncClient() as client:
                keys_response = await client.get("https://appleid.apple.com/auth/keys")
                
                if keys_response.status_code != 200:
                    return None
                    
                keys = keys_response.json()
                
                # Decode token header to get kid
                header = jwt.get_unverified_header(id_token)
                kid = header.get("kid")
                
                # Find matching key
                key = None
                for k in keys["keys"]:
                    if k["kid"] == kid:
                        key = jwt.algorithms.RSAAlgorithm.from_jwk(k)
                        break
                        
                if not key:
                    return None
                    
                # Verify and decode token
                decoded = jwt.decode(
                    id_token,
                    key,
                    algorithms=["RS256"],
                    audience=settings.APPLE_CLIENT_ID,
                    issuer="https://appleid.apple.com"
                )
                
                return decoded
                
        except Exception as e:
            print(f"Apple token verification failed: {e}")
            
        return None
