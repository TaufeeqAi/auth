
### backend/app/utils/push_notifications.py
"""FCM integration for push notifications"""

import json
import httpx
from typing import Dict, Any, Optional, List
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from ..core.config import settings


class FCMService:
    def __init__(self):
        self.project_id = settings.FCM_PROJECT_ID
        self.service_account_path = settings.FCM_SERVICE_ACCOUNT_PATH
        self._access_token = None

    async def _get_access_token(self) -> Optional[str]:
        """Get FCM access token using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=["https://www.googleapis.com/auth/firebase.messaging"]
            )
            
            credentials.refresh(Request())
            return credentials.token
            
        except Exception as e:
            print(f"Failed to get FCM access token: {e}")
            return None

    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """Send push notification to single device"""
        access_token = await self._get_access_token()
        if not access_token:
            return False
            
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        
        if image_url:
            message["message"]["notification"]["image"] = image_url
            
        if data:
            message["message"]["data"] = data
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=message
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"Failed to send FCM notification: {e}")
            return False

    async def send_multicast_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, int]:
        """Send notification to multiple devices"""
        access_token = await self._get_access_token()
        if not access_token:
            return {"success": 0, "failure": len(tokens)}
            
        # FCM multicast message
        message = {
            "message": {
                "tokens": tokens,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        
        if data:
            message["message"]["data"] = data
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=message
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": result.get("successCount", 0),
                        "failure": result.get("failureCount", 0)
                    }
                    
        except Exception as e:
            print(f"Failed to send multicast FCM notification: {e}")
            
        return {"success": 0, "failure": len(tokens)}

    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> bool:
        """Subscribe devices to a topic"""
        access_token = await self._get_access_token()
        if not access_token:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://iid.googleapis.com/iid/v1:batchAdd",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "to": f"/topics/{topic}",
                        "registration_tokens": tokens
                    }
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"Failed to subscribe to topic: {e}")
            return False
