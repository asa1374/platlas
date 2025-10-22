from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_current_admin
from app.core.config import get_settings
from app.core.security import create_admin_token
from app.schemas.admin import AdminLoginRequest, AdminSession
from app.schemas.common import ApiResponse


router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login", response_model=ApiResponse[AdminSession])
def admin_login(payload: AdminLoginRequest, response: Response) -> ApiResponse[AdminSession]:
    settings = get_settings()
    if (
        payload.username != settings.admin_username
        or payload.password != settings.admin_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    token = create_admin_token(payload.username)
    max_age = settings.admin_jwt_expiration_minutes * 60
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        max_age=max_age,
        secure=settings.environment == "production",
        samesite="lax",
    )

    return ApiResponse(
        message="로그인되었습니다.",
        data=AdminSession(username=payload.username),
    )


@router.post("/logout", response_model=ApiResponse[None])
def admin_logout(response: Response) -> ApiResponse[None]:
    response.delete_cookie("admin_token")
    return ApiResponse(message="로그아웃되었습니다.")


@router.get("/me", response_model=ApiResponse[AdminSession])
def admin_me(current_admin: str = Depends(get_current_admin)) -> ApiResponse[AdminSession]:
    return ApiResponse(data=AdminSession(username=current_admin))
