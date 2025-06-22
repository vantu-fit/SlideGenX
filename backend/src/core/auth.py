from jose import jwt, JWTError
from typing import Optional
from core.config import settings
import re

def password_validation(password: str) -> bool:
    """
    Validate the password strength.
    
    Args:
        password (str): The password to validate.
    
    Returns:
        bool: True if the password is strong, False otherwise.
    """
    # Password must be at least 8 characters long and contain letters and numbers
    regex = r'^.{8,}$'

    return bool(re.match(regex, password))

# ---------------------------
# JWT TOKEN UTILS
# ---------------------------

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# ---------------------------
# VERIFY / DECODE TOKENS
# ---------------------------

def decode_token(token: str) -> Optional[dict]:
    token = token.strip('"')  # remove outer quotes if present
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_username_from_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    return payload.get("username") if payload else None

def get_role_from_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    return payload.get("role") if payload else None