#!/bin/bash
# ==============================================================================
# Script de instalación y verificación del Dashboard ATROZ
# Versión: 2.0.0 (2026-01-24)
# Ejecutar: bash setup_dashboard.sh
# ==============================================================================

set -e

echo "=================================="
echo "DASHBOARD ATROZ - INSTALACIÓN v2.0"
echo "=================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detectar directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==============================================================================
# Paso 1: Verificar/Crear entorno virtual
# ==============================================================================
echo "📋 Verificando entorno Python..."

# Detectar Python disponible
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python no encontrado${NC}"
    echo "   Instalar Python 3.12+ desde https://python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"

# Verificar versión mínima (3.10+)
MAJOR_VERSION=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
MINOR_VERSION=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 10 ]); then
    echo -e "${RED}❌ Se requiere Python 3.10+, encontrado $PYTHON_VERSION${NC}"
    exit 1
fi
echo ""

# ==============================================================================
# Paso 2: Configurar entorno virtual
# ==============================================================================
echo "🔧 Configurando entorno virtual..."

VENV_DIR="$SCRIPT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}✅ Entorno virtual existente encontrado${NC}"
else
    echo "   Creando nuevo entorno virtual..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Entorno virtual creado en $VENV_DIR${NC}"
fi

# Activar entorno virtual
source "$VENV_DIR/bin/activate"
PIP_CMD="$VENV_DIR/bin/pip"
PYTHON_VENV="$VENV_DIR/bin/python"

echo -e "${GREEN}✅ Entorno virtual activado${NC}"
echo ""

# ==============================================================================
# Paso 3: Instalar dependencias del dashboard
# ==============================================================================
echo "📦 Instalando dependencias del dashboard..."
echo "   Dashboard: flask, flask-socketio, flask-cors, gevent, gevent-websocket"
echo "   Pipeline:  blake3, structlog, pydantic, psutil"
echo ""

# Actualizar pip primero
$PIP_CMD install --upgrade pip -q 2>/dev/null || true

# Dependencias del dashboard Flask
$PIP_CMD install -q \
    flask \
    flask-socketio \
    flask-cors \
    python-socketio \
    gevent \
    gevent-websocket \
    psutil

# Dependencias core del pipeline (necesarias para imports)
$PIP_CMD install -q \
    blake3 \
    structlog \
    pydantic

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}❌ Error instalando dependencias${NC}"
    exit 1
fi
echo ""

# ==============================================================================
# Paso 4: Verificar imports del dashboard
# ==============================================================================
echo "🔍 Verificando imports del dashboard..."

$PYTHON_VENV -c "
import sys
import importlib.metadata
sys.path.insert(0, 'src')

errors = []
warnings = []

# Verificar módulos externos
def check_module(name, import_name=None):
    import_name = import_name or name
    try:
        mod = __import__(import_name)
        try:
            version = importlib.metadata.version(name)
            print(f'✅ {name}: {version}')
        except:
            print(f'✅ {name}: instalado')
        return True
    except ImportError as e:
        errors.append(f'{name}: {e}')
        return False

print('--- Dependencias externas ---')
check_module('flask')
check_module('flask-socketio', 'flask_socketio')
check_module('flask-cors', 'flask_cors')
check_module('gevent')
check_module('psutil')
check_module('blake3')
check_module('structlog')
check_module('pydantic')

print('')
print('--- Módulos internos ---')

# Verificar módulos internos del dashboard
try:
    from farfan_pipeline.dashboard_atroz_ import dashboard_server
    print(f'✅ dashboard_server importado')
    print(f'   PDET regions: {len(dashboard_server.PDET_REGIONS)}')
except ImportError as e:
    errors.append(f'dashboard_server: {e}')

try:
    from farfan_pipeline.orchestration import UnifiedOrchestrator, PhaseID
    print(f'✅ orchestration.UnifiedOrchestrator importado')
    print(f'✅ orchestration.PhaseID importado')
except ImportError as e:
    errors.append(f'orchestration: {e}')

try:
    from farfan_pipeline.dashboard_atroz_.pipeline_dashboard_bridge import PipelineDashboardBridge
    print(f'✅ pipeline_dashboard_bridge importado')
except ImportError as e:
    errors.append(f'pipeline_dashboard_bridge: {e}')

try:
    from farfan_pipeline.dashboard_atroz_.pdet_dashboard_adapter import load_pdet_regions_for_dashboard
    print(f'✅ pdet_dashboard_adapter importado')
except ImportError as e:
    errors.append(f'pdet_dashboard_adapter: {e}')

print('')

if errors:
    print('❌ ERRORES ENCONTRADOS:')
    for err in errors:
        print(f'   - {err}')
    sys.exit(1)
else:
    print('✅ Todas las verificaciones pasaron')
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Verificación de imports exitosa${NC}"
else
    echo -e "${RED}❌ Error en verificación de imports${NC}"
    echo ""
    echo "Posibles soluciones:"
    echo "  1. Ejecutar: pip install -e . (instalar paquete en modo editable)"
    echo "  2. Verificar que PYTHONPATH incluya 'src/'"
    echo "  3. Revisar errores de import arriba"
    exit 1
fi
echo ""

# ==============================================================================
# Paso 5: Crear directorios necesarios
# ==============================================================================
echo "📁 Creando directorios necesarios..."
mkdir -p "$SCRIPT_DIR/data/uploads"
mkdir -p "$SCRIPT_DIR/pipeline_inputs"
mkdir -p "$SCRIPT_DIR/pipeline_outputs"
mkdir -p "$SCRIPT_DIR/pipeline_temp"
mkdir -p "$SCRIPT_DIR/build/reports"
echo -e "${GREEN}✅ Directorios creados${NC}"
echo ""

# ==============================================================================
# Paso 6: Verificar dashboard.html existe
# ==============================================================================
echo "🌐 Verificando archivos estáticos..."
DASHBOARD_HTML="$SCRIPT_DIR/dashboard.html"
if [ -f "$DASHBOARD_HTML" ]; then
    echo -e "${GREEN}✅ dashboard.html encontrado${NC}"
else
    echo -e "${YELLOW}⚠️  dashboard.html no encontrado - se usará endpoint API${NC}"
fi

STATIC_DIR="$SCRIPT_DIR/src/farfan_pipeline/dashboard_atroz_/static"
if [ -d "$STATIC_DIR" ]; then
    STATIC_COUNT=$(ls -1 "$STATIC_DIR" 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ Directorio static/ encontrado ($STATIC_COUNT archivos)${NC}"
else
    echo -e "${YELLOW}⚠️  Directorio static/ no encontrado${NC}"
fi
echo ""

# ==============================================================================
# Paso 7: Mostrar instrucciones de ejecución
# ==============================================================================
echo "=================================="
echo -e "${GREEN}✅ INSTALACIÓN COMPLETA${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}Para ejecutar el dashboard:${NC}"
echo ""
echo -e "  ${YELLOW}# Opción 1: Con entorno virtual activado${NC}"
echo "  source .venv/bin/activate"
echo "  PYTHONPATH=src python -m farfan_pipeline.dashboard_atroz_.dashboard_server"
echo ""
echo -e "  ${YELLOW}# Opción 2: Comando directo${NC}"
echo "  PYTHONPATH=src .venv/bin/python -m farfan_pipeline.dashboard_atroz_.dashboard_server"
echo ""
echo -e "${BLUE}Luego abrir en navegador:${NC}"
echo ""
echo -e "  ${GREEN}http://localhost:5000${NC}"
echo ""
echo -e "${BLUE}Endpoints API v1 disponibles:${NC}"
echo "  - http://localhost:5000/api/v1/regions           (170 municipios PDET)"
echo "  - http://localhost:5000/api/v1/regions/<id>      (detalle de región)"
echo "  - http://localhost:5000/api/v1/sisas/status      (estado SISAS)"
echo "  - http://localhost:5000/api/v1/sisas/metrics     (métricas SISAS)"
echo "  - http://localhost:5000/api/v1/canonical/questions"
echo "  - http://localhost:5000/api/v1/canonical/dimensions"
echo "  - http://localhost:5000/api/v1/canonical/policy-areas"
echo "  - http://localhost:5000/api/v1/canonical/clusters"
echo ""
echo -e "${BLUE}Documentación:${NC}"
echo "  - VERIFICACION_DASHBOARD_REAL.md"
echo "  - src/farfan_pipeline/dashboard_atroz_/README.md"
echo ""
