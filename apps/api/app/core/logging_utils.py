"""Logging helpers with safe defaults."""

import logging
from app.core.config import settings
from app.core.security import sanitize_for_logging


def get_logger(name: str = "vaulta") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    return logger


def log_exception(context: str, exc: Exception) -> None:
    """Log exceptions when enabled via config, without leaking PII."""
    if not settings.LOG_ERRORS_ENABLED:
        return
    logger = get_logger()
    logger.exception("%s: %s", context, exc)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    session_id: str | None = None,
    request_body: object | None = None,
) -> None:
    """Log a request when enabled via config, with optional sanitized body."""
    if not settings.LOG_REQUESTS_ENABLED:
        return
    logger = get_logger()
    payload = {
        "method": method,
        "path": path,
        "status": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    if session_id:
        payload["session_id"] = session_id
    if settings.LOG_REQUEST_BODY and request_body is not None:
        payload["request_body"] = sanitize_for_logging(request_body)
    logger.info("request=%s", payload)
