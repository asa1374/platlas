from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Tuple
from uuid import uuid4

import boto3
from fastapi import HTTPException, status

from app.core.config import get_settings


def _ensure_bucket_configured() -> None:
    settings = get_settings()
    if not settings.submission_upload_bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="파일 업로드 구성이 되어 있지 않습니다.",
        )


def build_s3_client():
    settings = get_settings()
    session = boto3.session.Session()
    return session.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.aws_endpoint_url,
    )


def generate_presigned_upload(filename: str, content_type: str) -> Tuple[str, str]:
    _ensure_bucket_configured()
    settings = get_settings()

    extension = Path(filename).suffix.lower()
    if extension and not content_type:
        guessed = mimetypes.guess_type(filename)[0]
        if guessed:
            content_type = guessed

    if content_type and not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일만 업로드할 수 있습니다.",
        )

    key = f"{settings.submission_upload_prefix.rstrip('/')}/{uuid4().hex}{extension}"
    client = build_s3_client()

    params = {
        "Bucket": settings.submission_upload_bucket,
        "Key": key,
    }
    if content_type:
        params["ContentType"] = content_type

    upload_url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=settings.submission_upload_url_expiration,
    )

    if settings.s3_public_base_url:
        file_url = f"{settings.s3_public_base_url.rstrip('/')}/{key}"
    else:
        region = settings.aws_region or "us-east-1"
        file_url = f"https://{settings.submission_upload_bucket}.s3.{region}.amazonaws.com/{key}"

    return upload_url, file_url
