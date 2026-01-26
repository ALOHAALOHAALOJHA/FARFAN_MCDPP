# DEPENDENCIAS FALTANTES PARA DASHBOARD ATROZ

## ❌ PROBLEMA CRÍTICO

El dashboard **NO PUEDE EJECUTARSE** porque faltan dependencias en `requirements.txt`.

---

## 📦 DEPENDENCIAS FALTANTES

El dashboard usa **Flask + Flask-SocketIO** pero NO están en `requirements.txt`:

```python
# dashboard_server.py línea 5-8:
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
```

### **Dependencias requeridas NO instaladas:**
1. ❌ `flask` - Framework web
2. ❌ `flask-socketio` - WebSocket real-time
3. ❌ `flask-cors` - CORS support
4. ❌ `python-socketio` - SocketIO backend
5. ❌ `gevent` - Async mode para SocketIO (dashboard usa `async_mode='gevent'`)
6. ❌ `psutil` - System metrics (usado en `/api/metrics`)

---

## 🔧 SOLUCIÓN - INSTALAR DEPENDENCIAS

### **Opción 1: Instalar manualmente (rápido)**

```bash
cd /home/user/FARFAN_MCDPP

pip install flask flask-socketio flask-cors python-socketio gevent psutil
```

**Versiones recomendadas:**
```bash
pip install \
  flask>=3.0.0 \
  flask-socketio>=5.3.0 \
  flask-cors>=4.0.0 \
  python-socketio>=5.11.0 \
  gevent>=24.0.0 \
  psutil>=5.9.0
```

### **Opción 2: Actualizar requirements.txt (permanente)**

Agregar al final de `requirements.txt`:

```txt
# DASHBOARD LAYER (agregado 2026-01-23)
flask>=3.0.0
flask-socketio>=5.3.0
flask-cors>=4.0.0
python-socketio>=5.11.0
gevent>=24.0.0
psutil>=5.9.0
```

Luego instalar:
```bash
pip install -r requirements.txt
```

---

## ✅ VERIFICAR INSTALACIÓN

Después de instalar, verificar:

```bash
cd /home/user/FARFAN_MCDPP

python -c "
import sys
sys.path.insert(0, 'src')
try:
    from farfan_pipeline.dashboard_atroz_ import dashboard_server
    print('✅ Dashboard imports successfully')
    print(f'✅ PDET regions: {len(dashboard_server.PDET_REGIONS)}')
    print(f'✅ Flask version: {dashboard_server.Flask.__version__}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Output esperado:**
```
✅ Dashboard imports successfully
✅ PDET regions: 170
✅ Flask version: 3.0.x
```

---

## 🚀 EJECUTAR DASHBOARD (después de instalar dependencias)

```bash
cd /home/user/FARFAN_MCDPP

# Opción 1: Ejecutar directamente
python -m farfan_pipeline.dashboard_atroz_.dashboard_server

# Opción 2: Con PYTHONPATH explícito
PYTHONPATH=src python src/farfan_pipeline/dashboard_atroz_/dashboard_server.py
```

**Output esperado:**
```
INFO:farfan_pipeline.dashboard_atroz_.dashboard_server:Starting AtroZ Dashboard Server...
INFO:farfan_pipeline.dashboard_atroz_.dashboard_server:Loaded 170 PDET regions with real data
INFO:farfan_pipeline.dashboard_atroz_.dashboard_server:Upload directory: /tmp/uploads
INFO:werkzeug: * Running on http://0.0.0.0:5000
```

Luego abrir navegador: **http://localhost:5000**

---

## 📝 DEPENDENCIAS COMPLETAS DEL DASHBOARD

Para referencia completa, el dashboard requiere:

### **Backend Framework:**
- `flask` - Web framework
- `flask-socketio` - WebSocket real-time updates
- `flask-cors` - Cross-Origin Resource Sharing
- `python-socketio` - SocketIO client/server
- `gevent` - Async greenlet-based concurrency

### **Utilities:**
- `psutil` - System metrics (CPU, memoria)

### **Ya en requirements.txt (usados por dashboard):**
- ✅ `fastapi` - API v1 router
- ✅ `uvicorn` - ASGI server (para API separado)
- ✅ `pydantic` - Data validation
- ✅ `python-dotenv` - Environment variables
- ✅ `structlog` - Logging
- ✅ `httpx` - HTTP client
- ✅ `sse-starlette` - Server-Sent Events

---

## ⚠️ NOTA IMPORTANTE

El dashboard tiene **dos servidores separados**:

1. **Flask Server** (`dashboard_server.py`):
   - Puerto: 5000
   - Funcionalidad: WebSocket, UI, upload PDFs
   - Dependencias: Flask, Flask-SocketIO, gevent ❌ FALTAN

2. **FastAPI Server** (`api_server.py`):
   - Puerto: 8000 (configurable)
   - Funcionalidad: API v1 endpoints
   - Dependencias: FastAPI, uvicorn ✅ YA INSTALADAS

**Ambos pueden ejecutarse simultáneamente o por separado.**

---

## 🎯 RESUMEN

1. ❌ **Dashboard NO funciona** sin instalar Flask + dependencias
2. ✅ **Solución**: `pip install flask flask-socketio flask-cors python-socketio gevent psutil`
3. ⚠️ **Recomendación**: Actualizar `requirements.txt` permanentemente
4. 🚀 **Después de instalar**: Dashboard arranca normalmente en puerto 5000

---

## 📋 CHECKLIST DE INSTALACIÓN

- [ ] Instalar Flask y dependencias
- [ ] Verificar imports con comando de verificación
- [ ] Ejecutar dashboard_server.py
- [ ] Confirmar que arranca en puerto 5000
- [ ] Abrir http://localhost:5000 en navegador
- [ ] Verificar que carga 170 regiones PDET
- [ ] (Opcional) Actualizar requirements.txt para instalaciones futuras
