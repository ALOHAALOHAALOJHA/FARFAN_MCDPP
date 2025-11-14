# ATROZ IMPLEMENTATION: ZERO-AMBIGUITY EXECUTION GUIDE

## Overview

This guide provides complete, deterministic instructions for deploying and running the AtroZ Dashboard system. Follow these steps exactly as written to ensure successful deployment.

**System Components:**
- AtroZ Dashboard (Visceral frontend with blood red, copper oxide, toxic green aesthetics)
- Admin Panel (PDF upload and analysis execution)
- Real Pipeline Integration (SAAAAAA orchestrator connector)
- Authentication System (JWT-based with RBAC)
- PDET Colombia Dataset (16 subregions, 170 municipalities)

**Author:** AtroZ Implementation Team  
**Version:** 1.0.0  
**Last Updated:** 2024-11-14

---

## Prerequisites

### System Requirements

| Requirement | Minimum Version | Verification Command |
|------------|----------------|---------------------|
| Python | 3.10+ | `python3 --version` |
| pip | 20.0+ | `pip3 --version` |
| Git | 2.25+ | `git --version` |
| Disk Space | 1GB free | `df -h` |
| RAM | 2GB available | `free -h` |

### Environment

**Supported Operating Systems:**
- Ubuntu 20.04 LTS or later
- macOS 11 (Big Sur) or later
- Windows 10/11 with WSL2

**Required Ports:**
- 5000 (default, configurable via `ATROZ_API_PORT`)

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/THEBLESSMAN867/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE.git
cd F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install AtroZ-specific dependencies
pip install -r requirements_atroz.txt

# Verify installation
pip list | grep -E "flask|jwt|werkzeug"
```

**Expected packages:**
- flask>=3.0.0
- flask-cors>=6.0.0
- flask-socketio>=5.3.5
- pyjwt>=2.8.0
- werkzeug>=3.0.0

### Step 4: Install Package (Editable Mode)

```bash
pip install -e .
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
ATROZ_API_PORT=5000
ATROZ_API_HOST=0.0.0.0
ATROZ_DEBUG=false

# Security (CHANGE IN PRODUCTION!)
ATROZ_API_SECRET=your-secret-key-here-change-me
ATROZ_JWT_SECRET=your-jwt-secret-here-change-me

# JWT Settings
ATROZ_JWT_EXPIRATION_HOURS=24

# CORS
ATROZ_CORS_ORIGINS=*

# Rate Limiting
ATROZ_RATE_LIMIT=true
ATROZ_RATE_LIMIT_REQUESTS=1000
ATROZ_RATE_LIMIT_WINDOW=900

# Cache
ATROZ_CACHE_ENABLED=true
ATROZ_CACHE_TTL=300

# Data Directories
ATROZ_DATA_DIR=output
ATROZ_CACHE_DIR=cache
```

### Security Warning

**⚠️ CRITICAL: Change these values in production:**
1. `ATROZ_API_SECRET` - Use a random 32+ character string
2. `ATROZ_JWT_SECRET` - Use a different random 32+ character string
3. `ATROZ_CORS_ORIGINS` - Set to specific domains (not `*`)

Generate secure secrets:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Deployment

### Option 1: Verified Start (Recommended)

The verified start script performs comprehensive checks before starting:

```bash
./start_atroz_verified.sh
```

**What it checks:**
- ✅ Python version (3.10+)
- ✅ All dependencies installed
- ✅ Directory structure
- ✅ Critical files present
- ✅ PDET dataset (16 subregions, 170 municipalities)
- ✅ Authentication module
- ✅ Pipeline connector
- ✅ Port availability
- ✅ Output directories

**Options:**
```bash
# Skip verification (not recommended)
./start_atroz_verified.sh --skip-verification

# Custom port
./start_atroz_verified.sh --port 8080

# Debug mode
./start_atroz_verified.sh --debug

# View help
./start_atroz_verified.sh --help
```

### Option 2: Manual Start

```bash
# Set environment
export ATROZ_API_PORT=5000
export ATROZ_API_HOST=0.0.0.0
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Start server
python3 -m saaaaaa.api.api_server
```

### Option 3: Development Mode

```bash
# Enable debug mode
export ATROZ_DEBUG=true

# Start with auto-reload
python3 -m saaaaaa.api.api_server
```

---

## Verification

### 1. Server Health Check

```bash
curl http://localhost:5000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-14T16:30:00.000000",
  "version": "1.0.0"
}
```

### 2. PDET Data Verification

```bash
curl http://localhost:5000/api/v1/pdet/regions
```

**Expected:**
- 16 PDET regions returned
- Each with municipalities list

### 3. Dashboard Access

Open browser to:
- **Dashboard:** http://localhost:5000/
- **Admin Panel:** http://localhost:5000/admin.html

**Visual Verification:**
- ✅ Blood red (#8B0000) background tones
- ✅ Copper oxide (#17A589) accents
- ✅ Toxic green (#39FF14) highlights
- ✅ Particle effects visible
- ✅ Neural grid background
- ✅ DNA helix animation in micro level
- ✅ Glitching logo effect
- ✅ 16 PDET constellation nodes

### 4. Authentication Test

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AtroZ_Admin_2024!"}'
```

**Expected:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "admin"
}
```

### 5. Test Analysis Workflow

1. **Login to Admin Panel:**
   - URL: http://localhost:5000/admin.html
   - Username: `admin`
   - Password: `AtroZ_Admin_2024!`

2. **Select PDET Region:**
   - Choose any of the 16 subregions
   - Select a municipality from the dropdown

3. **Upload PDF:**
   - Drag and drop a test PDF
   - Or click to select file
   - Maximum 50MB

4. **Start Analysis:**
   - Click "Iniciar Análisis"
   - Watch progress stages
   - Verify results display

---

## Usage

### Admin Panel

**Default Credentials:**
- Username: `admin`
- Password: `AtroZ_Admin_2024!`

**⚠️ CHANGE PASSWORD IMMEDIATELY IN PRODUCTION!**

**Workflow:**
1. Login with credentials
2. Select PDET subregion and municipality
3. Upload development plan PDF (max 50MB)
4. Click "Iniciar Análisis"
5. Monitor progress through 7 stages:
   - PDF text extraction
   - Macro level analysis
   - Meso level (clusters) analysis
   - Micro level (44 questions) analysis
   - Recommendation generation
   - Evidence compilation
   - Finalization
6. View results in admin panel
7. Click "Ver Reporte Completo" to open in dashboard

### API Endpoints

**Public Endpoints:**
```
GET  /api/v1/health                    - Health check
GET  /api/v1/pdet/regions              - List all PDET regions
GET  /api/v1/pdet/regions/<id>         - Get region details
POST /api/v1/auth/login                - Login
```

**Protected Endpoints (Require JWT Token):**
```
POST /api/v1/auth/logout               - Logout
POST /api/v1/auth/verify               - Verify token
GET  /api/v1/pdet/data                 - Get PDET dataset
POST /api/v1/admin/upload              - Upload PDF
POST /api/v1/admin/analyze             - Start analysis
GET  /api/v1/admin/analysis/<id>       - Get analysis status
GET  /api/v1/admin/analyses/recent     - List recent analyses
```

### PDET Dataset

**Accessing Programmatically:**

```python
from src.saaaaaa.api.pdet_colombia_data import (
    PDET_SUBREGIONS,
    ALL_MUNICIPALITIES,
    get_statistics,
    get_subregion_by_id,
    get_municipalities_by_subregion,
    get_municipalities_by_department
)

# Get statistics
stats = get_statistics()
print(f"Total Subregions: {stats['total_subregions']}")        # 16
print(f"Total Municipalities: {stats['total_municipalities']}")  # 170

# Get specific subregion
subregion = get_subregion_by_id('alto-patia')
print(subregion.name)  # Alto Patía y Norte del Cauca
print(len(subregion.municipalities))  # 24

# Get municipalities by department
munis = get_municipalities_by_department('Antioquia')
print(len(munis))  # 23
```

---

## Pipeline Integration

### Real Orchestrator Mode

When the SAAAAAA orchestrator is available:

```python
from src.saaaaaa.api.pipeline_connector import pipeline_connector

# Check if orchestrator is available
print(pipeline_connector.orchestrator_available)  # True or False

# Connector will automatically use real analysis when available
# Falls back to mock mode if orchestrator not initialized
```

### Verification Manifests

After batch analysis:

```python
from src.saaaaaa.api.pipeline_connector import pipeline_connector

# Load results
results = [pipeline_connector.load_result(id) for id in result_ids]

# Create verification manifest
manifest = pipeline_connector.create_verification_manifest(
    analysis_results=results,
    pipeline_version="1.0.0"
)

# Check validation
print(f"Validation Passed: {manifest.validation_passed}")
print(f"Success Rate: {manifest.successful_analyses / manifest.total_analyses * 100}%")
print(f"Average Processing Time: {manifest.average_processing_time_seconds}s")

# Manifests are auto-saved to output/verification_manifests/
```

---

## Success Criteria

### Deployment Success

- [x] Server starts without errors
- [x] Health check returns `200 OK`
- [x] Dashboard loads in browser
- [x] All CSS animations working (glitch, pulse, helix, particles)
- [x] 16 PDET regions visible in constellation
- [x] Admin panel accessible
- [x] Login works with default credentials
- [x] PDET data loads (16 subregions, 170 municipalities)

### Functional Success

- [x] PDF upload works (drag-drop and click)
- [x] File size validation (50MB limit)
- [x] Municipality selection works
- [x] Analysis can be initiated
- [x] Progress tracking shows 7 stages
- [x] Results display with metrics:
  - Macro score
  - Cluster counts
  - Question counts (44)
  - Recommendations
  - Evidence items
  - Processing time
- [x] Recent analyses list populates

### Security Success

- [x] Authentication required for admin endpoints
- [x] JWT tokens expire after configured time
- [x] Rate limiting active
- [x] Password validation enforces:
  - 12+ characters
  - Uppercase letters
  - Lowercase letters
  - Digits
  - Special characters
- [x] Login attempts limited (5 attempts, 15-min lockout)

---

## Troubleshooting

### Server Won't Start

**Problem:** Port already in use
```
Solution: Kill existing process or use different port
$ lsof -ti:5000 | xargs kill
or
$ ./start_atroz_verified.sh --port 8080
```

**Problem:** Dependencies missing
```
Solution: Reinstall requirements
$ pip install -r requirements_atroz.txt
```

**Problem:** Python version too old
```
Solution: Upgrade Python
$ python3 --version  # Should be 3.10+
```

### Dashboard Not Loading

**Problem:** CSS not applying
```
Solution: Check static files exist
$ ls -la src/saaaaaa/api/static/css/
$ ls -la src/saaaaaa/api/static/js/
```

**Problem:** Particles not visible
```
Solution: Check JavaScript console for errors
Browser DevTools > Console
```

### Authentication Fails

**Problem:** Invalid credentials
```
Default: username=admin, password=AtroZ_Admin_2024!
Check for typos, password is case-sensitive
```

**Problem:** Token expired
```
Solution: Login again or increase JWT expiration
export ATROZ_JWT_EXPIRATION_HOURS=48
```

### Analysis Fails

**Problem:** PDF too large
```
Maximum: 50MB
Solution: Compress PDF or split into sections
```

**Problem:** Orchestrator not available
```
System automatically falls back to mock analysis
Check logs for initialization errors
```

---

## Performance Tuning

### For High Load

```bash
# Increase rate limits
export ATROZ_RATE_LIMIT_REQUESTS=5000
export ATROZ_RATE_LIMIT_WINDOW=900

# Extend cache TTL
export ATROZ_CACHE_TTL=600

# Use production WSGI server (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 saaaaaa.api.api_server:app
```

### For Development

```bash
# Enable debug mode
export ATROZ_DEBUG=true

# Disable caching
export ATROZ_CACHE_ENABLED=false

# Verbose logging
export FLASK_DEBUG=1
```

---

## Maintenance

### Backup

**Critical files to backup:**
```
output/analysis_results/     - All analysis results
output/verification_manifests/  - Validation manifests
.env                          - Environment configuration
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements_atroz.txt --upgrade

# Restart server
./start_atroz_verified.sh
```

### Monitoring

**Health checks:**
```bash
# Every 5 minutes
*/5 * * * * curl -f http://localhost:5000/api/v1/health || systemctl restart atroz
```

**Log locations:**
- Application logs: `output/logs/` (if configured)
- System logs: Check via `journalctl` if using systemd

---

## Support

**For issues, questions, or contributions:**

1. Check this guide first
2. Review logs for error messages
3. Run verification script: `./start_atroz_verified.sh`
4. Submit GitHub issue with:
   - System information (`python --version`, OS)
   - Error logs
   - Steps to reproduce
   - Expected vs actual behavior

**Security Issues:**
Report privately via GitHub Security Advisory

---

## Appendix

### Complete Dataset Statistics

```
PDET Subregions: 16
Total Municipalities: 170
Departments Covered: 18

Subregions by Municipality Count:
1. Alto Patía y Norte del Cauca: 24
2. Cuenca del Caguán y Piedemonte Caqueteño: 14
3. Montes de María: 15
4. Chocó: 14
5. Bajo Cauca y Nordeste Antioqueño: 13
6. Catatumbo: 11
7. Pacífico y Frontera Nariñense: 11
8. Putumayo: 11
9. Macarena-Guaviare: 10
10. Sierra Nevada-Perijá-Zona Bananera: 10
11. Urabá Antioqueño: 10
12. Pacífico Medio: 7
13. Sur de Bolívar: 7
14. Sur de Córdoba: 5
15. Arauca: 4
16. Sur del Tolima: 4
```

### Default Color Palette

```css
--atroz-red-900: #3A0E0E      /* Dark blood red */
--atroz-red-700: #7A0F0F      /* Blood red */
--atroz-red-500: #C41E3A      /* Bright blood red */
--atroz-blood: #8B0000        /* Pure blood red */
--atroz-blue-900: #04101A     /* Deep ocean blue */
--atroz-blue-700: #102F56     /* Dark navy */
--atroz-blue-electric: #00D4FF /* Electric blue */
--atroz-green-900: #0B231B    /* Deep forest green */
--atroz-green-300: #BFEFCB    /* Light mint */
--atroz-green-toxic: #39FF14  /* Toxic neon green */
--atroz-copper-700: #7B3F1D   /* Dark copper */
--atroz-copper-500: #B2642E   /* Copper */
--atroz-copper-oxide: #17A589 /* Copper oxide (patina) */
```

---

**End of Guide**

**Version:** 1.0.0  
**Last Updated:** 2024-11-14  
**Maintained by:** AtroZ Implementation Team
