from datetime import datetime, timedelta, timezone
from typing import Any, Union, Dict
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a password using Argon2.
    """
    return pwd_context.hash(password)

def create_refresh_token(subject: Union[str, Any]) -> tuple[str, str]:
    """
    Generates a Refresh JWT and its hash.
    Returns: (encoded_jwt, hashed_token)
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.PRIVATE_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    hashed_token = get_password_hash(encoded_jwt)
    return encoded_jwt, hashed_token

def create_access_token(subject: Union[str, Any], claims: Dict[str, Any] | None = None) -> str:
    """
    Generates a JWT using the RS256 algorithm and the Private Key.
    
    :param subject: The main identifier (usually user_id)
    :param claims: Additional data (like 'tier', 'email', etc.)
    """
    if claims is None:
        claims = {}
        
    # Set Expiration
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    # Prepare Payload
    # 'sub' (Subject) is a standard claim for the User ID
    # 'exp' is expiration
    # 'iat' is issued at time
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject)  
    }
    
    # Add Custom Claims (The "Decentralized" Data)
    # This puts 'tier' inside the token itself so other services can read it.
    to_encode.update(claims)
    
    # Sign with PRIVATE KEY using RS256
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.PRIVATE_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt