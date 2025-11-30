# app/utils/auth.py
"""
Centralized JWT utilities and authentication helpers.

All routers should use:
    from app.utils.auth import get_current_user

This ensures consistent token behavior and eliminates duplicate logic.
"""

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request, status
from jose import jwt, JWTError
from app.config import settings


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    The token structure stays identical for full frontend compatibility.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate the JWT token.
    Returns the payload dict or raises HTTPException(401).
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(request: Request) -> str:
    """
    Extracts the authenticated user's username from the Authorization header.
    This replaces all duplicated versions across routers.

    Returns:
        user_id: str - the username stored in the token's "sub" field
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.split(" ")[1]

    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id
