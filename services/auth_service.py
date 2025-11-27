# services/auth_service.py
"""
Authentication and session management service
"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_HOURS = 24

def generate_token(user_id: int, email: str) -> str:
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_token(token: str) -> Optional[int]:
    """Extract user_id from token"""
    payload = verify_token(token)
    return payload.get('user_id') if payload else None
