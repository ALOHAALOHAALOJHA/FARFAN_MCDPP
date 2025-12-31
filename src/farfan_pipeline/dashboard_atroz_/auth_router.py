"""Authentication endpoints for AtroZ Dashboard.

Provides login, logout, and session management endpoints that integrate
with the AdminAuthenticator from auth_admin.py.
"""

from __future__ import annotations

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
    client_ip = request.client.host if request.client else "unknown"
    
    session_id = auth.authenticate(
        username=credentials.username,
        password=credentials.password,
        ip_address=client_ip
    )
    
    if session_id is None:
        logger.warning(
            "login_failed",
            username=credentials.username,
            ip=client_ip
        )
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": "Invalid credentials or rate limit exceeded"
            }
        )
    
    logger.info(
        "login_successful",
        username=credentials.username,
        ip=client_ip
    )
    
    response = JSONResponse(
        status_code=200,
        content={
            "success": True,
            "session_id": session_id,
            "username": credentials.username,
            "message": "Login successful"
        }
    )
    
    # Set session cookie
    response.set_cookie(
        key="atroz_session",
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=3600  # 1 hour
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
        auth.logout(session_id)
        logger.info("logout_successful", session_id=session_id[:8] + "...")
    
    response = JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Logged out successfully"
        }
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
            content={
                "valid": False,
                "username": None,
                "message": "No session found"
            }
        )
    
    client_ip = request.client.host if request.client else None
    
    if auth.validate_session(session_id, client_ip):
        session = auth.get_session(session_id)
        return JSONResponse(
            status_code=200,
            content={
                "valid": True,
                "username": session.username if session else None,
                "message": "Session is valid"
            }
        )
    
    return JSONResponse(
        status_code=200,
        content={
            "valid": False,
            "username": None,
            "message": "Session is invalid or expired"
        }
    )
