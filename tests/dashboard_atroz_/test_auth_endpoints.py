"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient

from farfan_pipeline.dashboard_atroz_.signals_service import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_credentials():
    """
    Test credentials fixture.
    
    Note: Using default admin credentials for testing.
    In production, these should be changed or mocked.
    """
    return {
        "username": "admin",
        "password": "atroz_admin_2024"
    }


def test_login_success(client, test_credentials):
    """Test successful login with default credentials."""
    response = client.post(
        "/auth/login",
        json=test_credentials
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "session_id" in data
    assert data["username"] == "admin"
    assert "atroz_session" in response.cookies


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "error" in data


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "password"
        }
    )
    
    assert response.status_code == 401


def test_logout(client, test_credentials):
    """Test logout endpoint."""
    # First login
    login_response = client.post(
        "/auth/login",
        json=test_credentials
    )
    assert login_response.status_code == 200
    
    # Then logout
    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200
    data = logout_response.json()
    assert data["success"] is True


def test_session_validation_valid(client, test_credentials):
    """Test session validation with valid session."""
    # First login
    login_response = client.post(
        "/auth/login",
        json=test_credentials
    )
    assert login_response.status_code == 200
    session_id = login_response.json()["session_id"]
    
    # Validate session using header
    session_response = client.get(
        "/auth/session",
        headers={"X-Session-ID": session_id}
    )
    assert session_response.status_code == 200
    data = session_response.json()
    assert data["valid"] is True
    assert data["username"] == "admin"


def test_session_validation_invalid(client):
    """Test session validation with invalid session."""
    response = client.get(
        "/auth/session",
        headers={"X-Session-ID": "invalid_session_id"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


def test_session_validation_no_session(client):
    """Test session validation with no session."""
    response = client.get("/auth/session")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["username"] is None
