"""
Tests for SMTP email delivery helpers.
"""
from unittest.mock import MagicMock, patch

import pytest

try:
    from .modules import send_email_report, smtp_configured, smtp_configuration_status
except ImportError:
    from modules import send_email_report, smtp_configured, smtp_configuration_status


def test_smtp_configured_requires_core_env(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    assert smtp_configured() is False

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USERNAME", "demo@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    assert smtp_configured() is True


def test_smtp_configuration_status_reports_missing(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)

    ok, missing = smtp_configuration_status()

    assert ok is False
    assert set(missing) == {"SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"}


def test_smtp_configuration_status_reports_ok(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USERNAME", "demo@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")

    ok, missing = smtp_configuration_status()

    assert ok is True
    assert missing == []


def test_send_email_report_raises_when_smtp_missing(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    with pytest.raises(RuntimeError):
        send_email_report("qa@example.com", "Subject", "Body")


def test_send_email_report_raises_on_invalid_recipient(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USERNAME", "demo@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    with pytest.raises(ValueError):
        send_email_report("not-an-email", "Subject", "Body")


@patch("modules.mailer.smtplib.SMTP")
def test_send_email_report_uses_smtp(mock_smtp, monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "demo@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM", "buglens@example.com")

    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    send_email_report("qa@example.com", "Login issue", "Line 1\nLine 2")

    mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=20)
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("demo@example.com", "secret")
    smtp_instance.send_message.assert_called_once()
