"""
SMTP email delivery for rewritten BugLens reports.
"""
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
import json
from pathlib import Path


def smtp_configuration_status() -> tuple[bool, list[str]]:
    required = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD")
    missing = [name for name in required if not _get_setting(name)]
    return len(missing) == 0, missing


_CONFIG_PATH = Path(__file__).parent.parent / "smtp_config.json"


def _load_config() -> dict:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _get_setting(name: str) -> str | None:
    # Prefer environment variables, then saved config file.
    val = os.getenv(name)
    if val:
        return val
    cfg = _load_config()
    return cfg.get(name)


def smtp_configured() -> bool:
    configured, _ = smtp_configuration_status()
    return configured


def send_email_report(to_email: str, subject: str, body: str) -> None:
    host = _get_setting("SMTP_HOST")
    port = int(_get_setting("SMTP_PORT") or "587")
    username = _get_setting("SMTP_USERNAME")
    password = _get_setting("SMTP_PASSWORD")
    from_email = _get_setting("SMTP_FROM") or (username or "noreply@buglens.local")
    use_tls = (_get_setting("SMTP_USE_TLS") or "true").lower() != "false"

    if not host or not username or not password:
        raise RuntimeError("SMTP is not configured. Set SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD.")
    if "@" not in to_email:
        raise ValueError("Recipient email address looks invalid.")

    msg = EmailMessage()
    msg["Subject"] = subject.strip() or "BugLens defect report"
    msg["From"] = from_email
    msg["To"] = to_email.strip()
    msg.set_content(body.strip() or "No report content provided.")

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        server.login(username, password)
        server.send_message(msg)


