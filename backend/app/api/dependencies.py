from collections.abc import Generator
from typing import Optional

from fastapi import Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import decode_admin_token
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(
    request: Request, authorization: Optional[str] = Header(default=None)
) -> str:
    token: Optional[str] = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", maxsplit=1)[1]
    elif "admin_token" in request.cookies:
        token = request.cookies.get("admin_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
        )

    return decode_admin_token(token)
