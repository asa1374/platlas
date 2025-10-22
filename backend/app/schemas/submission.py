from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr, Field

from app.db.models.submission import SubmissionStatus


class SubmissionBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    submitter_name: str = Field(min_length=1, max_length=255)
    submitter_email: EmailStr
    platform_name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    website_url: Optional[AnyHttpUrl] = None
    ios_url: Optional[AnyHttpUrl] = None
    android_url: Optional[AnyHttpUrl] = None
    web_url: Optional[AnyHttpUrl] = None
    screenshot_url: Optional[str] = Field(default=None, max_length=1024)


class SubmissionCreate(SubmissionBase):
    recaptcha_token: Optional[str] = Field(default=None, alias="recaptchaToken")


class SubmissionRead(SubmissionBase):
    id: int
    status: SubmissionStatus
    rejection_reason: Optional[str] = None
    platform_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    items: list[SubmissionRead]
    total: int


class SubmissionRejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class PresignedUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: Optional[str] = Field(default=None, alias="contentType")


class PresignedUploadResponse(BaseModel):
    upload_url: str = Field(alias="uploadUrl")
    file_url: str = Field(alias="fileUrl")
