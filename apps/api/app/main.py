"""
Vaulta Voice Agent - FastAPI Application Entry Point
"""

import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_utils import log_exception, log_request
from app.core.exceptions import VaultaError, VerificationRequiredError
from app.api import vapi_routes
from app.api import admin_routes
from app.services.session_manager import session_manager


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend service for Vaulta Voice AI Agent"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(vapi_routes.router)
app.include_router(admin_routes.router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    request_body_obj = None

    if settings.LOG_REQUESTS_ENABLED and settings.LOG_REQUEST_BODY:
        try:
            body_bytes = await request.body()
            if body_bytes:
                body_text = body_bytes.decode("utf-8", errors="ignore")
                if len(body_text) > settings.LOG_REQUEST_BODY_MAX_CHARS:
                    body_text = body_text[: settings.LOG_REQUEST_BODY_MAX_CHARS] + "...(truncated)"
                try:
                    request_body_obj = json.loads(body_text)
                except json.JSONDecodeError:
                    request_body_obj = {"raw": body_text}
        except Exception:
            request_body_obj = {"raw": "[unavailable]"}

    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    session_id = request.headers.get("x-session-id")

    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        session_id=session_id,
        request_body=request_body_obj,
    )

    return response


@app.on_event("startup")
async def startup_event():
    """Tasks to run on startup."""
    # Start session cleanup task
    asyncio.create_task(session_manager.start_cleanup_task())


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check for monitoring."""
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.sessions),
        "environment": settings.ENVIRONMENT,
        "pii_redaction": settings.PIN_REDACTION_ENABLED
    }


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(VerificationRequiredError)
async def verification_required_handler(request: Request, exc: VerificationRequiredError):
    """Handle verification errors gracefully."""
    return JSONResponse(
        status_code=403,
        content={
            "error": "verification_required",
            "message": str(exc),
            "action": "request_auth"
        }
    )


@app.exception_handler(VaultaError)
async def vaulta_error_handler(request: Request, exc: VaultaError):
    """Handle general Vaulta errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "banking_error",
            "message": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """Catch-all error handler."""
    log_exception("Unhandled error", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
