#!/bin/bash
# Script de instalación y verificación del Dashboard ATROZ
# Ejecutar: bash setup_dashboard.sh

set -e

echo "=================================="
echo "DASHBOARD ATROZ - INSTALACIÓN"
echo "=================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paso 1: Verificar Python
echo "📋 Verificando Python..."
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python no encontrado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
echo ""

# Paso 2: Instalar dependencias del dashboard
echo "📦 Instalando dependencias del dashboard..."
echo "   - flask"
echo "   - flask-socketio"
echo "   - flask-cors"
echo "   - python-socketio"
echo "   - gevent"
echo "   - psutil"
echo ""

pip install -q flask flask-socketio flask-cors python-socketio gevent psutil

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}❌ Error instalando dependencias${NC}"
    exit 1
fi
echo ""

# Paso 3: Verificar imports
echo "🔍 Verificando imports del dashboard..."
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from farfan_pipeline.dashboard_atroz_ import dashboard_server
    print('✅ Dashboard imports successfully')
    print(f'✅ PDET regions loaded: {len(dashboard_server.PDET_REGIONS)}')
    import flask
    print(f'✅ Flask version: {flask.__version__}')
    import flask_socketio
    print(f'✅ Flask-SocketIO version: {flask_socketio.__version__}')
    import gevent
    print(f'✅ Gevent version: {gevent.__version__}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Verificación exitosa${NC}"
else
    echo -e "${RED}❌ Error en verificación${NC}"
    exit 1
fi
echo ""

# Paso 4: Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p /tmp/uploads
mkdir -p pipeline_inputs
mkdir -p pipeline_outputs
mkdir -p pipeline_temp
echo -e "${GREEN}✅ Directorios creados${NC}"
echo ""

# Paso 5: Mostrar instrucciones
echo "=================================="
echo "✅ INSTALACIÓN COMPLETA"
echo "=================================="
echo ""
echo "Para ejecutar el dashboard:"
echo ""
echo -e "${YELLOW}python -m farfan_pipeline.dashboard_atroz_.dashboard_server${NC}"
echo ""
echo "Luego abrir en navegador:"
echo ""
echo -e "${GREEN}http://localhost:5000${NC}"
echo ""
echo "Endpoints disponibles:"
echo "  - http://localhost:5000/api/v1/regions"
echo "  - http://localhost:5000/api/v1/sisas/status"
echo "  - http://localhost:5000/static/sisas-ecosystem-view-enhanced.html"
echo ""
echo "Para más información, ver:"
echo "  - VERIFICACION_DASHBOARD_REAL.md"
echo "  - DASHBOARD_DEPENDENCIAS_FALTANTES.md"
echo ""
