from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


def verify_recaptcha(token: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.recaptcha_secret_key:
        # If no secret key is configured we treat the verification as optional
        return {"success": True, "score": 1.0}

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA 검증 토큰이 필요합니다.",
        )

    try:
        response = httpx.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": settings.recaptcha_secret_key, "response": token},
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
    except httpx.HTTPError as exc:  # pragma: no cover - network interaction
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="reCAPTCHA 검증에 실패했습니다.",
        ) from exc

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA 검증에 실패했습니다.",
        )

    score = result.get("score")
    if score is not None and score < settings.recaptcha_score_threshold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잠재적인 자동 제출이 감지되었습니다.",
        )

    return result
