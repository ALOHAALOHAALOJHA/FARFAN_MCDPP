"""Authentication endpoints for AtroZ Dashboard.

Provides login, logout, and session management endpoints that integrate
with the AdminAuthenticator from auth_admin.py.
"""

from __future__ import annotations

import os

import structlog
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .auth_admin import get_authenticator

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login credentials"""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    """Successful login response"""

    success: bool
    session_id: str
    username: str
    message: str


class LogoutResponse(BaseModel):
    """Logout response"""

    success: bool
    message: str


class SessionResponse(BaseModel):
    """Session validation response"""

    valid: bool
    username: str | None = None
    message: str


class ChangePasswordRequest(BaseModel):
    """Password change request"""

    old_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePasswordResponse(BaseModel):
    """Password change response"""

    success: bool
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, request: Request) -> Response:
    """
    Authenticate user and create session.

    Args:
        credentials: Username and password
        request: FastAPI request object (for IP address)

    Returns:
        LoginResponse with session_id if successful
    """
    auth = get_authenticator()

    # Get client IP address securely
    # In production behind a reverse proxy, configure the proxy to set X-Forwarded-For
    # and only trust IPs from known proxies. For now, we prioritize direct connection.
    client_ip = "unknown"

    # Direct connection is most trustworthy
    if request.client:
        client_ip = request.client.host
    # Only trust proxy headers if configured (via environment variable)
    elif os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true":
        # Get the last IP in X-Forwarded-For (closest proxy we control)
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            # Take the rightmost IP (last proxy in chain, most trustworthy)
            ips = [ip.strip() for ip in forwarded_for.split(",")]
            client_ip = ips[-1] if ips else "unknown"
        else:
            # Fallback to X-Real-IP if X-Forwarded-For is not present
            client_ip = request.headers.get("X-Real-IP", "unknown")

    session_id = auth.authenticate(
        username=credentials.username, password=credentials.password, ip_address=client_ip
    )

    if session_id is None:
        logger.warning("login_failed", username=credentials.username, ip=client_ip)
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Invalid credentials or rate limit exceeded"},
        )

    logger.info("login_successful", username=credentials.username, ip=client_ip)

    response = JSONResponse(
        status_code=200,
        content={
            "success": True,
            "session_id": session_id,
            "username": credentials.username,
            "message": "Login successful",
        },
    )

    # Set session cookie
    # Use secure cookies in production (HTTPS only)
    # Use strict samesite in production for stronger CSRF protection
    is_production = os.getenv("FARFAN_ENV", "development").lower() == "production"
    response.set_cookie(
        key="atroz_session",
        value=session_id,
        httponly=True,
        secure=is_production,
        samesite="strict" if is_production else "lax",
        max_age=3600,  # 1 hour
        domain=os.getenv("COOKIE_DOMAIN") if os.getenv("COOKIE_DOMAIN") else None,
    )

    return response


@router.post("/logout", response_model=LogoutResponse)
async def logout(request: Request) -> Response:
    """
    Terminate user session.

    Args:
        request: FastAPI request object (for session cookie)

    Returns:
        LogoutResponse indicating success
    """
    auth = get_authenticator()

    # Get session from cookie or header
    session_id = request.cookies.get("atroz_session")
    if not session_id:
        session_id = request.headers.get("X-Session-ID")

    if session_id:
        session = auth.get_session(session_id)
        username = session.username if session else "unknown"
        auth.logout(session_id)
        logger.info("logout_successful", username=username)

    response = JSONResponse(
        status_code=200, content={"success": True, "message": "Logged out successfully"}
    )

    # Clear session cookie
    response.delete_cookie(key="atroz_session")

    return response


@router.get("/session", response_model=SessionResponse)
async def validate_session(request: Request) -> Response:
    """
    Validate current session.

    Args:
        request: FastAPI request object (for session cookie)

    Returns:
        SessionResponse indicating if session is valid
    """
    auth = get_authenticator()

    # Get session from cookie or header
    session_id = request.cookies.get("atroz_session")
    if not session_id:
        session_id = request.headers.get("X-Session-ID")

    if not session_id:
        return JSONResponse(
            status_code=200,
            content={"valid": False, "username": None, "message": "No session found"},
        )

    client_ip = request.client.host if request.client else None

    if auth.validate_session(session_id, client_ip):
        session = auth.get_session(session_id)
        return JSONResponse(
            status_code=200,
            content={
                "valid": True,
                "username": session.username if session else None,
                "message": "Session is valid",
            },
        )

    return JSONResponse(
        status_code=200,
        content={"valid": False, "username": None, "message": "Session is invalid or expired"},
    )


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(password_change: ChangePasswordRequest, request: Request) -> Response:
    """
    Change user password.

    Requires valid session (via cookie or header).

    Args:
        password_change: Old and new password
        request: FastAPI request object (for session)

    Returns:
        ChangePasswordResponse indicating success
    """
    auth = get_authenticator()

    # Get session from cookie or header
    session_id = request.cookies.get("atroz_session")
    if not session_id:
        session_id = request.headers.get("X-Session-ID")

    if not session_id:
        return JSONResponse(
            status_code=401, content={"success": False, "message": "Authentication required"}
        )

    # Validate session
    session = auth.get_session(session_id)
    if not session:
        return JSONResponse(
            status_code=401, content={"success": False, "message": "Invalid or expired session"}
        )

    # Change password
    success = auth.change_password(
        username=session.username,
        old_password=password_change.old_password,
        new_password=password_change.new_password,
    )

    if not success:
        logger.warning(
            "password_change_failed", username=session.username, reason="Invalid old password"
        )
        return JSONResponse(
            status_code=400, content={"success": False, "message": "Invalid old password"}
        )

    logger.info("password_changed", username=session.username)

    return JSONResponse(
        status_code=200, content={"success": True, "message": "Password changed successfully"}
    )
