"""
Dashboard Configuration
"""

import os

# Database Configuration
# Default to a local PostgreSQL instance, or SQLite for development
DATABASE_URL = os.getenv("ATROZ_DATABASE_URL", "postgresql://user:pass@localhost/atroz_dashboard")
USE_SQLITE = os.getenv("ATROZ_USE_SQLITE", "false").lower() == "true"

# Feature Flags
ENABLE_REALTIME_INGESTION = os.getenv("ATROZ_ENABLE_INGESTION", "true").lower() == "true"
