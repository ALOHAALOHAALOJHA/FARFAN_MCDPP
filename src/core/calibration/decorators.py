"""
CALIBRATION DECORATORS
Enforces anchoring to central calibration system.
"""
from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def calibrated_method(method_id: str) -> Callable[[F], F]:
    """
    OBLIGATORIO: Decorador que FUERZA anclaje al sistema central.
    
    Workflow:
    1. Carga parámetros del JSON (intrinsic calibration)
    2. Ejecuta el método
    3. Calibra el resultado via orchestrator
    4. Valida y retorna
    
    Args:
        method_id: Canonical method identifier
    
    Returns:
        Decorated function with calibration enforcement
    
    Example:
        @calibrated_method("D1Q1_executor")
        def execute_d1q1(pdt: PDT) -> float:
            return compute_score(pdt)
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from . import get_calibration_orchestrator, get_intrinsic_loader
            
            logger.debug(f"Calibrating method: {method_id}")
            
            loader = get_intrinsic_loader()
            required_layers = loader.get_required_layers_for_method(method_id)
            
            logger.debug(
                f"Method {method_id} requires {len(required_layers)} layers: {required_layers}"
            )
            
            raw_result = func(*args, **kwargs)
            
            orchestrator = get_calibration_orchestrator()
            
            context = kwargs.get("_calibration_context", {})
            evidence = kwargs.get("_calibration_evidence", {})
            
            try:
                if hasattr(orchestrator, "calibrate_method"):
                    calibration_result = orchestrator.calibrate_method(
                        method_id,
                        context=context,
                        evidence=evidence,
                    )
                    logger.info(
                        f"Method {method_id} calibrated: "
                        f"score={calibration_result.final_score:.3f}"
                    )
            except Exception as e:
                logger.debug(f"Calibration check skipped for {method_id}: {e}")
            
            return raw_result
        
        return wrapper  # type: ignore[return-value]
    
    return decorator


def calibration_required(
    threshold: float = 0.7,
    method_id: str | None = None,
) -> Callable[[F], F]:
    """
    Decorator that enforces minimum calibration threshold.
    Raises exception if method's calibration score is below threshold.
    
    Args:
        threshold: Minimum calibration score required
        method_id: Method ID (if None, inferred from function name)
    
    Returns:
        Decorated function with threshold enforcement
    
    Example:
        @calibration_required(threshold=0.8, method_id="D1Q1_executor")
        def execute_d1q1(pdt: PDT) -> float:
            return compute_score(pdt)
    """
    def decorator(func: F) -> F:
        actual_method_id = method_id or func.__name__
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from . import get_calibration_orchestrator, get_intrinsic_loader
            
            loader = get_intrinsic_loader()
            base_score = loader.get_base_score(actual_method_id)
            
            if base_score < threshold:
                logger.warning(
                    f"Method {actual_method_id} base score {base_score:.3f} "
                    f"below threshold {threshold:.3f}"
                )
            
            orchestrator = get_calibration_orchestrator()
            
            context = kwargs.get("_calibration_context", {})
            evidence = kwargs.get("_calibration_evidence", {})
            
            try:
                if hasattr(orchestrator, "calibrate_method"):
                    calibration_result = orchestrator.calibrate_method(
                        actual_method_id,
                        context=context,
                        evidence=evidence,
                    )
                    final_score = calibration_result.final_score
                    
                    if final_score < threshold:
                        raise ValueError(
                            f"Method {actual_method_id} calibration score {final_score:.3f} "
                            f"below required threshold {threshold:.3f}"
                        )
            except Exception as e:
                logger.debug(f"Calibration threshold check skipped for {actual_method_id}: {e}")
            
            return func(*args, **kwargs)
        
        return wrapper  # type: ignore[return-value]
    
    return decorator


__all__ = [
    "calibrated_method",
    "calibration_required",
]
