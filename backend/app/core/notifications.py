from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Iterable

import httpx

from app.core.config import get_settings
from app.db.models.submission import Submission

logger = logging.getLogger(__name__)


def send_slack_notification(text: str) -> None:
    settings = get_settings()
    if not settings.slack_webhook_url:
        return

    try:
        response = httpx.post(settings.slack_webhook_url, json={"text": text}, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network interactions
        logger.warning("Failed to send Slack notification: %s", exc)


def send_email_notification(subject: str, body: str, recipients: Iterable[str]) -> None:
    settings = get_settings()
    if not settings.notification_email_sender or not recipients:
        return

    message = EmailMessage()
    message["From"] = settings.notification_email_sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    if not settings.smtp_host:
        logger.warning("SMTP_HOST is not configured; skipping email notification")
        return

    try:
        if settings.smtp_use_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.starttls()
                if settings.smtp_username and settings.smtp_password:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_username and settings.smtp_password:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
    except Exception as exc:  # pragma: no cover - network interactions
        logger.warning("Failed to send email notification: %s", exc)


def notify_submission_approved(submission: Submission) -> None:
    platform_name = submission.platform_name
    platform_url = submission.platform.url if submission.platform else submission.website_url
    message_lines = [
        f"새 플랫폼 제출이 승인되었습니다: {platform_name}",
        f"제출자: {submission.submitter_name} <{submission.submitter_email}>",
    ]
    if platform_url:
        message_lines.append(f"웹사이트: {platform_url}")
    if submission.platform:
        message_lines.append(f"플랫폼 상세: /platforms/{submission.platform.slug}")

    text = "\n".join(message_lines)
    send_slack_notification(text)

    recipients = get_settings().notification_email_recipients
    if recipients:
        send_email_notification(
            subject=f"[Platlas] 제출 승인 - {platform_name}",
            body=text,
            recipients=recipients,
        )


def notify_submission_rejected(submission: Submission) -> None:
    if not submission.submitter_email:
        return

    recipients = [submission.submitter_email]
    subject = f"[Platlas] 제출 결과 안내 - {submission.platform_name}"
    reason = submission.rejection_reason or "사유가 제공되지 않았습니다."
    body = (
        f"안녕하세요, {submission.submitter_name}님.\n\n"
        f"제출해 주신 '{submission.platform_name}'은(는) 검토 결과 거절되었습니다.\n"
        f"사유: {reason}\n\n"
        "추가 문의 사항이 있으시면 회신 부탁드립니다."
    )

    send_email_notification(subject, body, recipients)
