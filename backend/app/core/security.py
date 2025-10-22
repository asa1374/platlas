from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings


def create_admin_token(subject: str) -> str:
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.admin_jwt_expiration_minutes)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "exp": now + expires_delta,
        "iat": now,
    }
    return jwt.encode(payload, settings.admin_jwt_secret, algorithm="HS256")


def decode_admin_token(token: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.admin_jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session",
        ) from exc

    subject: Optional[str] = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin session",
        )
    return subject
