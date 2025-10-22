from functools import lru_cache

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    app_name: str = Field(default="Platlas API", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    api_prefix: str = Field(default="/api")
    default_page_size: int = Field(default=50)

    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="changeme", alias="ADMIN_PASSWORD")
    admin_jwt_secret: str = Field(default="super-secret", alias="ADMIN_JWT_SECRET")
    admin_jwt_expiration_minutes: int = Field(default=60, alias="ADMIN_JWT_EXPIRATION_MINUTES")

    submission_upload_bucket: Optional[str] = Field(default=None, alias="SUBMISSION_UPLOAD_BUCKET")
    submission_upload_prefix: str = Field(default="submissions", alias="SUBMISSION_UPLOAD_PREFIX")
    submission_upload_url_expiration: int = Field(default=900, alias="SUBMISSION_UPLOAD_URL_EXPIRATION")
    aws_region: Optional[str] = Field(default=None, alias="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_endpoint_url: Optional[str] = Field(default=None, alias="AWS_ENDPOINT_URL")
    s3_public_base_url: Optional[str] = Field(default=None, alias="S3_PUBLIC_BASE_URL")

    recaptcha_secret_key: Optional[str] = Field(default=None, alias="RECAPTCHA_SECRET_KEY")
    recaptcha_score_threshold: float = Field(default=0.4, alias="RECAPTCHA_SCORE_THRESHOLD")

    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    notification_email_sender: Optional[str] = Field(default=None, alias="NOTIFICATION_EMAIL_SENDER")
    notification_email_recipients: List[str] = Field(
        default_factory=list, alias="NOTIFICATION_EMAIL_RECIPIENTS"
    )
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()  # type: ignore[arg-type]
