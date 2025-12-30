# Authentication System Documentation

## Overview

The F.A.R.F.A.N Dashboard now includes a complete authentication system with REST API endpoints for user login, logout, and session management.

## Endpoints

### POST /auth/login

Authenticate a user and create a session.

**Request Body:**
```json
{
  "username": "admin",
  "password": "atroz_admin_2024"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "session_id": "tLx8f3qR9mK2vP7nH4wJ6sY1bC5dE0uA3gZ8xM9vN",
  "username": "admin",
  "message": "Login successful"
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Invalid credentials or rate limit exceeded"
}
```

**Side Effects:**
- Sets `atroz_session` HttpOnly cookie with session ID
- Records login attempt for rate limiting
- Creates session entry in authenticator

### POST /auth/logout

Terminate the current user session.

**Request Headers/Cookies:**
- Cookie: `atroz_session=<session_id>`
- OR Header: `X-Session-ID: <session_id>`

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Side Effects:**
- Removes session from authenticator
- Deletes `atroz_session` cookie

### GET /auth/session

Validate the current session.

**Request Headers/Cookies:**
- Cookie: `atroz_session=<session_id>`
- OR Header: `X-Session-ID: <session_id>`

**Success Response - Valid Session (200):**
```json
{
  "valid": true,
  "username": "admin",
  "message": "Session is valid"
}
```

**Success Response - Invalid Session (200):**
```json
{
  "valid": false,
  "username": null,
  "message": "Session is invalid or expired"
}
```

## Security Features

1. **Password Hashing**: Passwords are hashed using SHA-256 with unique salts
2. **Session Management**: Sessions expire after 60 minutes of inactivity
3. **Rate Limiting**: Maximum 5 login attempts per IP within 15 minutes
4. **IP Tracking**: Sessions are tied to the originating IP address
5. **HttpOnly Cookies**: Session cookies are not accessible via JavaScript
6. **Secure Cookies**: In production (when `FARFAN_ENV=production`), cookies are only sent over HTTPS
7. **Automatic Cleanup**: Expired sessions are automatically removed
8. **No Session ID Logging**: Session IDs are never logged to prevent enumeration attacks

## Default Credentials

**Username**: `admin`  
**Password**: `atroz_admin_2024`

⚠️ **WARNING**: Change the default password in production!

## Usage Examples

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"atroz_admin_2024"}' \
  -c cookies.txt

# Check session (using cookie)
curl -X GET http://localhost:8000/auth/session \
  -b cookies.txt

# Logout
curl -X POST http://localhost:8000/auth/logout \
  -b cookies.txt
```

### Using Python requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "atroz_admin_2024"}
)
session_id = response.json()["session_id"]

# Validate session
response = requests.get(
    "http://localhost:8000/auth/session",
    headers={"X-Session-ID": session_id}
)
print(response.json())

# Logout
requests.post(
    "http://localhost:8000/auth/logout",
    headers={"X-Session-ID": session_id}
)
```

### Using JavaScript fetch

```javascript
// Login
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // Important for cookies
  body: JSON.stringify({
    username: 'admin',
    password: 'atroz_admin_2024'
  })
});
const data = await response.json();

// Session validation (cookie is sent automatically)
const sessionResponse = await fetch('http://localhost:8000/auth/session', {
  credentials: 'include'
});
const sessionData = await sessionResponse.json();

// Logout
await fetch('http://localhost:8000/auth/logout', {
  method: 'POST',
  credentials: 'include'
});
```

## Integration with AdminAuthenticator

The authentication endpoints use the existing `AdminAuthenticator` class from `auth_admin.py`:

- Session creation and validation
- Password hashing and verification
- Rate limiting on login attempts
- Session timeout management
- User management

## Configuration

### Environment Variables

- `FARFAN_ENV`: Set to `production` to enable secure cookies (HTTPS only)
  - Development: Cookies work over HTTP
  - Production: Cookies only sent over HTTPS

```bash
# Development (default)
export FARFAN_ENV=development

# Production
export FARFAN_ENV=production
```

### Session Timeout

Session timeout can be configured when initializing the `AdminAuthenticator`:

```python
from farfan_pipeline.dashboard_atroz_.auth_admin import AdminAuthenticator

# Custom timeout (in minutes)
auth = AdminAuthenticator(session_timeout_minutes=30)
```

## Adding New Users

To add new users programmatically:

```python
from farfan_pipeline.dashboard_atroz_.auth_admin import get_authenticator

auth = get_authenticator()
auth.add_user(
    username="newuser",
    password="secure_password_123",
    role="user"
)
```

## Changing Passwords

Users can change their password:

```python
from farfan_pipeline.dashboard_atroz_.auth_admin import get_authenticator

auth = get_authenticator()
success = auth.change_password(
    username="admin",
    old_password="atroz_admin_2024",
    new_password="new_secure_password"
)
```

## Testing

Run the authentication test suite:

```bash
pytest tests/dashboard_atroz_/test_auth_endpoints.py -v
```

## Architecture

```
┌─────────────────┐
│   Client App    │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  FastAPI App    │
│ (signals_service)│
└────────┬────────┘
         │
         ├── /auth/*  ──────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐   ┌─────────────────┐
│  auth_router.py │───│ auth_admin.py   │
│  (REST API)     │   │ (Core Auth)     │
└─────────────────┘   └─────────────────┘
                      │
                      ├── Session Management
                      ├── Password Hashing
                      ├── Rate Limiting
                      └── User Management
```

## Files Modified/Created

1. **NEW**: `src/farfan_pipeline/dashboard_atroz_/auth_router.py`
   - FastAPI router with authentication endpoints
   
2. **MODIFIED**: `src/farfan_pipeline/dashboard_atroz_/signals_service.py`
   - Added auth_router to the main FastAPI application
   
3. **NEW**: `tests/dashboard_atroz_/test_auth_endpoints.py`
   - Comprehensive test suite for authentication

## Future Enhancements

- [ ] Add password complexity requirements
- [ ] Implement account lockout after too many failed attempts
- [ ] Add multi-factor authentication (MFA)
- [ ] Implement refresh tokens
- [ ] Add audit logging for authentication events
- [ ] Support for OAuth2/OIDC integration
- [ ] Role-based access control (RBAC) for endpoints
