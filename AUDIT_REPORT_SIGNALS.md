# Informe de Auditoría del Componente `signals`

**Fecha:** 2024-10-27

## 1. Resumen Ejecutivo

El componente `signals` de F.A.R.F.A.N está diseñado como un sistema sofisticado para irrigar el proceso analítico con patrones, indicadores y umbrales específicos de cada área de política, con mecanismos robustos para la validación, el versionado y la prueba criptográfica de su consumo. La arquitectura teórica es sólida y sigue principios de diseño modernos, incluyendo inmutabilidad, resiliencia y auditabilidad.

Sin embargo, la auditoría ha revelado que la implementación actual **falla a la hora de materializar los objetivos de diseño debido a una serie de desconexiones críticas entre sus componentes**. En su modo de operación por defecto, el sistema utiliza datos de muy baja calidad que no provienen de la fuente de verdad designada (`data/questionnaire_monolith.json`), lo que **reduce drásticamente, o incluso anula, el valor analítico** que este componente debería aportar.

Este informe detalla los hallazgos a nivel estructural, los clasifica por prioridad y proporciona un plan de acción concreto para corregir las deficiencias y alinear la implementación con su arquitectura.

## 2. Hallazgos de la Auditoría

Los hallazgos se presentan en orden de prioridad, desde el más crítico hasta el de menor impacto.

### 2.1. (Prioridad: CRÍTICO) Desconexión entre la Carga de Señales y el Consumo en el Modo por Defecto

**Problema a Nivel Estructural:**
El núcleo de la aplicación, gestionado por `WiringBootstrap` (`src/saaaaaa/core/wiring/bootstrap.py`), opera por defecto en un modo `memory://`. En este modo, la inicialización de las señales (`_seed_signals`) ignora por completo el módulo `signal_loader.py`, que es el componente diseñado para extraer y procesar la información completa y detallada del monolito. En su lugar, "siembra" `SignalPack`s casi vacíos, que contienen únicamente un máximo de 10 patrones básicos y ningún otro tipo de señal (indicadores, entidades, verbos, etc.).

**Impacto:**
*   **Pérdida Total de Valor Analítico:** Los `Executor`s, que son los consumidores finales, reciben señales de muy baja calidad. Esto significa que los análisis se realizan sin la profundidad y el contexto que el sistema de señales fue diseñado para proporcionar. Las decisiones tomadas por los `Executor`s son, por tanto, menos informadas y potencialmente incorrectas.
*   **Operación Engañosa:** El sistema aparenta funcionar (no hay errores en tiempo de ejecución), pero los datos que fluyen por el "wiring" son incorrectos.

**Solución Operativa:**
Modificar el método `_seed_signals` en `src/saaaaaa/core/wiring/bootstrap.py` para que utilice la lógica de `signal_loader.py`.

1.  **Importar el cargador:** Añadir `from saaaaaa.core.orchestrator.signal_loader import build_all_signal_packs` al fichero `bootstrap.py`.
2.  **Reemplazar la lógica de "siembra":** Sustituir el contenido de `_seed_signals` para que invoque a `build_all_signal_packs` y cargue los `SignalPack`s completos en el `InMemorySignalSource` y el `SignalRegistry`. Se debe utilizar el `QuestionnaireResourceProvider` ya disponible para pasar los datos del monolito.

```python
# En src/saaaaaa/core/wiring/bootstrap.py

# ... (imports)
from saaaaaa.core.orchestrator.signal_loader import build_all_signal_packs

# ...

    def _seed_signals(
        self,
        memory_source: InMemorySignalSource,
        registry: SignalRegistry,
        provider: QuestionnaireResourceProvider,
    ) -> None:
        """Seed initial signals in memory mode using the canonical loader."""
        logger.info("wiring_init_phase", phase="seed_signals")

        # Cargar el monolito desde el provider
        monolith_data = provider._data
        if not monolith_data:
            logger.warning("monolith_data_is_empty", phase="seed_signals")
            return

        # Utilizar el constructor canónico para crear los SignalPacks
        all_packs = build_all_signal_packs(monolith=monolith_data)

        for area, pack in all_packs.items():
            # Registrar en la fuente en memoria
            memory_source.register(area, pack)
            # Y también en el registro para disponibilidad inmediata
            registry.put(area, pack)
            logger.debug("signal_seeded", policy_area=area, patterns=len(pack.patterns))

        logger.info("signals_seeded_from_monolith", areas=len(all_packs))

```

### 2.2. (Prioridad: ALTO) El Servicio de API de Señales (`signals_service.py`) es un Stub no Funcional

**Problema a Nivel Estructural:**
El servicio de API en `src/saaaaaa/api/signals_service.py` está diseñado para servir los `SignalPack`s a través de HTTP, permitiendo una arquitectura de microservicios. Sin embargo, la implementación actual es un `stub`. La función `load_signals_from_monolith` no extrae las señales reales; en su lugar, llama a `_create_stub_signal_packs()`, que genera datos de prueba falsos y limitados.

**Impacto:**
*   **Modo HTTP Inservible:** Cualquier componente configurado para usar el `SignalClient` en modo `http://` (activado mediante la bandera `enable_http_signals`) recibirá datos de prueba incorrectos. Esto bloquea la posibilidad de desplegar el sistema de señales como un servicio independiente.
*   **Inconsistencia Arquitectural:** Existe una clara discrepancia entre la intención del diseño (un servicio de señales funcional) y la realidad de la implementación.

**Solución Operativa:**
Reemplazar la implementación `stub` en `signals_service.py` para que utilice la lógica real de `signal_loader.py`.

1.  **Importar el cargador:** Añadir `from saaaaaa.core.orchestrator.signal_loader import build_all_signal_packs`.
2.  **Corregir `load_signals_from_monolith`:** Modificar la función para que cargue el monolito a través del `load_questionnaire` canónico y luego utilice `build_all_signal_packs` para generar los `SignalPack`s reales.

```python
# En src/saaaaaa/api/signals_service.py

# ... (imports)
from saaaaaa.core.orchestrator.signal_loader import build_all_signal_packs

# ...

def load_signals_from_monolith() -> dict[str, SignalPack]:
    """
    Load signal packs from questionnaire monolith using canonical loader.
    """
    try:
        # Usar el cargador canónico para obtener los datos del monolito
        canonical_q = load_questionnaire()
        logger.info(
            "signals_loaded_from_monolith",
            sha256=canonical_q.sha256[:16] + "...",
            question_count=canonical_q.total_question_count,
        )

        # Usar el constructor de signal packs para extraer las señales
        return build_all_signal_packs(questionnaire=canonical_q)

    except Exception as e:
        logger.error("failed_to_load_monolith_for_service", error=str(e), exc_info=True)
        # Como fallback, retornar un diccionario vacío para evitar fallos catastróficos
        return {}
```

### 2.3. (Prioridad: MEDIO) La Prueba de Consumo de Señales es un Placeholder no Integrado

**Problema a Nivel Estructural:**
El sistema de prueba de consumo (`SignalConsumptionProof` en `signal_consumption.py`) está diseñado para crear un rastro auditable del uso de señales. La intención, como se ve en un `placeholder` dentro de `AdvancedDataFlowExecutor`, es que los `Executor`s registren cada vez que un patrón de una señal coincide con el texto. Sin embargo, esta lógica no está integrada en los métodos de análisis reales (ej. `IndustrialPolicyProcessor`). La implementación `placeholder` actual realiza una búsqueda simple y desconectada del análisis principal.

**Impacto:**
*   **Falsa Sensación de Seguridad:** El sistema puede generar pruebas de consumo, pero estas no reflejan el uso real de las señales en la lógica de negocio.
*   **Falta de Trazabilidad:** No es posible verificar criptográficamente qué señales contribuyeron a un resultado analítico específico, lo cual era un objetivo clave del diseño.

**Solución Operativa:**
Integrar la llamada a `consumption_proof.record_pattern_match()` dentro de los métodos que realizan el emparejamiento de patrones.

1.  **Pasar el Objeto `consumption_proof`:** El objeto `consumption_proof` debe ser accesible para los métodos de análisis. Esto se puede lograr pasándolo a través del contexto de argumentos (`_argument_context`), como ya se hace con `signals`.
2.  **Modificar los Métodos de Emparejamiento:** Clases como `IndustrialPolicyProcessor`, en métodos como `_match_patterns_in_sentences`, deben ser modificadas para que, después de encontrar una coincidencia, registren dicha coincidencia en el objeto `consumption_proof`.

### 2.4. (Prioridad: BAJO) El Directorio `config/policy_signals` es Engañoso y Obsoleto

**Problema a Nivel Estructural:**
El directorio `config/policy_signals` contiene ficheros JSON que parecen definir las políticas de señales. Sin embargo, el código ignora por completo este directorio y extrae las señales directamente del monolito.

**Impacto:**
*   **Confusión para Desarrolladores:** Un nuevo desarrollador podría intentar modificar estos ficheros esperando un cambio en el comportamiento del sistema, lo cual no ocurriría.
*   **Mantenimiento de Código Muerto:** Estos ficheros son artefactos obsoletos que añaden ruido al repositorio.

**Solución Operativa:**
1.  **Eliminar el Directorio:** Eliminar el directorio `config/policy_signals` del repositorio.
2.  **Documentar la Fuente de Verdad:** Asegurarse de que la documentación del proyecto indique claramente que `data/questionnaire_monolith.json` es la única fuente de verdad para la configuración de señales y que `signal_loader.py` contiene la lógica para su extracción.

## 3. Conclusión General

El componente `signals` es un ejemplo de una buena arquitectura socavada por una implementación incompleta y desconectada. La corrección de los problemas identificados, especialmente los dos primeros, es **crítica** para que el sistema cumpla su propósito de enriquecer el proceso analítico. Se recomienda abordar las soluciones propuestas en el orden de prioridad establecido para restaurar la funcionalidad y el valor del componente.
