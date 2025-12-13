from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import hashlib

from app.config import settings


# ==================== Password Functions ====================


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Uses SHA256 pre-hashing to avoid bcrypt's 72-byte limit.
    This approach:
    1. Hashes password with SHA256 (produces consistent 32-byte output)
    2. Hashes the SHA256 result with bcrypt
    3. Avoids any truncation issues while maintaining security

    Args:
        password: Plain text password

    Returns:
        Hashed password string (bcrypt format)
    """
    # Pre-hash with SHA256 to avoid bcrypt's 72-byte limit
    # SHA256 always produces 32-byte output regardless of input length
    password_sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Hash with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_sha256.encode("utf-8"), salt)

    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    # Pre-hash with SHA256 (same as when hashing)
    password_sha256 = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

    # Verify with bcrypt
    return bcrypt.checkpw(
        password_sha256.encode("utf-8"), hashed_password.encode("utf-8")
    )


# ==================== JWT Token Functions ====================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing user data to encode in token (e.g., {"user_id": "...", "email": "..."})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
