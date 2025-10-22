from __future__ import annotations

from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin, get_db
from app.core.notifications import (
    notify_submission_approved,
    notify_submission_rejected,
)
from app.core.recaptcha import verify_recaptcha
from app.core.storage import generate_presigned_upload
from app.core.slugs import slugify
from app.db.models import Platform, Submission, SubmissionStatus
from app.schemas.common import ApiResponse
from app.schemas.submission import (
    PresignedUploadRequest,
    PresignedUploadResponse,
    SubmissionCreate,
    SubmissionListResponse,
    SubmissionRead,
    SubmissionRejectRequest,
)
from app.services.platforms import generate_unique_slug


router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/upload-url", response_model=ApiResponse[PresignedUploadResponse])
def create_upload_url(payload: PresignedUploadRequest) -> ApiResponse[PresignedUploadResponse]:
    upload_url, file_url = generate_presigned_upload(
        payload.filename, payload.content_type or ""
    )
    response = PresignedUploadResponse(uploadUrl=upload_url, fileUrl=file_url)
    return ApiResponse(message="업로드 URL이 생성되었습니다.", data=response)


@router.post("/", response_model=ApiResponse[SubmissionRead], status_code=status.HTTP_201_CREATED)
def create_submission(
    payload: SubmissionCreate, db: Session = Depends(get_db)
) -> ApiResponse[SubmissionRead]:
    verify_recaptcha(payload.recaptcha_token or "")

    _ensure_not_duplicate(db, payload)

    submission = Submission(
        submitter_name=payload.submitter_name.strip(),
        submitter_email=payload.submitter_email,
        platform_name=payload.platform_name.strip(),
        description=payload.description,
        website_url=str(payload.website_url) if payload.website_url else None,
        ios_url=str(payload.ios_url) if payload.ios_url else None,
        android_url=str(payload.android_url) if payload.android_url else None,
        web_url=str(payload.web_url) if payload.web_url else None,
        screenshot_url=payload.screenshot_url,
        status=SubmissionStatus.PENDING,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return ApiResponse(message="제출이 완료되었습니다.", data=submission)


@router.get(
    "/", response_model=ApiResponse[SubmissionListResponse], dependencies=[Depends(get_current_admin)]
)
def list_submissions(
    status_filter: Optional[SubmissionStatus] = None,
    db: Session = Depends(get_db),
) -> ApiResponse[SubmissionListResponse]:
    stmt = select(Submission).order_by(Submission.created_at.desc())
    if status_filter:
        stmt = stmt.where(Submission.status == status_filter)

    submissions = db.execute(stmt).scalars().unique().all()
    count_stmt = select(func.count()).select_from(Submission)
    if status_filter:
        count_stmt = count_stmt.where(Submission.status == status_filter)
    total = db.execute(count_stmt).scalar_one()

    return ApiResponse(
        data=SubmissionListResponse(items=submissions, total=total),
    )


@router.post(
    "/{submission_id}/approve",
    response_model=ApiResponse[SubmissionRead],
    dependencies=[Depends(get_current_admin)],
)
def approve_submission(submission_id: int, db: Session = Depends(get_db)) -> ApiResponse[SubmissionRead]:
    submission = _get_submission_or_404(db, submission_id)
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 제출입니다.",
        )

    platform = _convert_submission_to_platform(db, submission)
    submission.status = SubmissionStatus.APPROVED
    submission.platform = platform
    submission.approved_at = datetime.now(timezone.utc)

    db.add(submission)
    db.commit()
    db.refresh(platform)
    db.refresh(submission)
    db.refresh(submission, attribute_names=["platform"])

    notify_submission_approved(submission)

    return ApiResponse(message="제출이 승인되었습니다.", data=submission)


@router.post(
    "/{submission_id}/reject",
    response_model=ApiResponse[SubmissionRead],
    dependencies=[Depends(get_current_admin)],
)
def reject_submission(
    submission_id: int,
    payload: SubmissionRejectRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[SubmissionRead]:
    submission = _get_submission_or_404(db, submission_id)
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 제출입니다.",
        )

    submission.status = SubmissionStatus.REJECTED
    submission.rejection_reason = payload.reason
    submission.rejected_at = datetime.now(timezone.utc)

    db.add(submission)
    db.commit()
    db.refresh(submission)

    notify_submission_rejected(submission)

    return ApiResponse(message="제출이 거절되었습니다.", data=submission)


def _ensure_not_duplicate(db: Session, payload: SubmissionCreate) -> None:
    name = payload.platform_name.strip()
    slug_candidate = slugify(name)

    name_exists = db.execute(
        select(Platform.id).where(
            or_(
                func.lower(Platform.name) == func.lower(name),
                Platform.slug == slug_candidate,
            )
        )
    ).scalar_one_or_none()
    if name_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 플랫폼입니다.",
        )

    pending_exists = db.execute(
        select(Submission.id)
        .where(func.lower(Submission.platform_name) == func.lower(name))
        .where(Submission.status == SubmissionStatus.PENDING)
    ).scalar_one_or_none()
    if pending_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 검토 중인 제출이 있습니다.",
        )

    urls = [payload.website_url, payload.ios_url, payload.android_url, payload.web_url]
    cleaned_urls = sorted({str(url).rstrip("/") for url in urls if url})
    if not cleaned_urls:
        return

    existing_url = db.execute(
        select(Platform.id).where(
            or_(
                *(Platform.url == url for url in cleaned_urls),
                *(Platform.web_url == url for url in cleaned_urls),
                *(Platform.ios_url == url for url in cleaned_urls),
                *(Platform.android_url == url for url in cleaned_urls),
            )
        )
    ).scalar_one_or_none()
    if existing_url:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 URL이 있습니다.",
        )

    existing_submission_url = db.execute(
        select(Submission.id)
        .where(Submission.status == SubmissionStatus.PENDING)
        .where(
            or_(
                *(Submission.website_url == url for url in cleaned_urls),
                *(Submission.web_url == url for url in cleaned_urls),
                *(Submission.ios_url == url for url in cleaned_urls),
                *(Submission.android_url == url for url in cleaned_urls),
            )
        )
    ).scalar_one_or_none()
    if existing_submission_url:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 검토 중인 URL이 있습니다.",
        )


def _get_submission_or_404(db: Session, submission_id: int) -> Submission:
    submission = db.execute(
        select(Submission).where(Submission.id == submission_id)
    ).scalars().first()
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출을 찾을 수 없습니다.",
        )
    return submission


def _convert_submission_to_platform(db: Session, submission: Submission) -> Platform:
    slug = generate_unique_slug(db, submission.platform_name)
    platform = Platform(
        name=submission.platform_name,
        slug=slug,
        description=submission.description,
        url=submission.website_url,
        ios_url=submission.ios_url,
        android_url=submission.android_url,
        web_url=submission.web_url,
    )
    db.add(platform)
    db.flush()
    submission.platform_id = platform.id
    return platform
