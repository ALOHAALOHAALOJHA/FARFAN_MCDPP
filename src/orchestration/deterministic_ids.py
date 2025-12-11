"""
Deterministic ID Generation
============================

Provides deterministic ID generation to replace uuid.uuid4() calls.
All IDs are derived from context (correlation_id, component, counter) to ensure
reproducibility across pipeline runs.

Author: Determinism Certification Team
Version: 1.0.0
Specification: SIN_CARRETA Doctrine - Deterministic Execution
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Optional


# Global salt for deterministic ID generation
_DETERMINISTIC_ID_SALT = b"FARFAN_DETERMINISTIC_ID_GENERATION_V1"


def generate_deterministic_id(
    context: str,
    component: str,
    salt: Optional[bytes] = None
) -> str:
    """
    Generate deterministic ID from context and component.
    
    This replaces uuid.uuid4() calls with deterministic generation based on:
    - context: correlation_id, policy_unit_id, or other execution context
    - component: identifies what the ID is for (e.g., "event", "correlation", "report")
    
    Args:
        context: Contextual information (e.g., correlation_id, policy_unit_id)
        component: Component identifier (e.g., "event_id", "correlation_id")
        salt: Optional salt bytes (defaults to global salt)
        
    Returns:
        Deterministic UUID-format string (e.g., "a1b2c3d4-...")
        
    Examples:
        >>> id1 = generate_deterministic_id("corr_123", "event_id")
        >>> id2 = generate_deterministic_id("corr_123", "event_id")
        >>> assert id1 == id2  # Deterministic
        
        >>> id3 = generate_deterministic_id("corr_123", "report_id")
        >>> assert id1 != id3  # Different components = different IDs
    """
    actual_salt = salt if salt is not None else _DETERMINISTIC_ID_SALT
    
    # Create deterministic hash
    material = f"{context}:{component}".encode('utf-8')
    hash_hmac = hmac.new(
        key=actual_salt,
        msg=material,
        digestmod=hashlib.sha256
    )
    
    # Extract 16 bytes for UUID format
    hash_bytes = hash_hmac.digest()[:16]
    
    # Format as UUID (8-4-4-4-12)
    hex_str = hash_bytes.hex()
    uuid_str = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
    
    return uuid_str


def generate_event_id(correlation_id: str, event_type: str, sequence: int = 0) -> str:
    """
    Generate deterministic event ID.
    
    Args:
        correlation_id: Correlation ID for this execution context
        event_type: Type of event (e.g., "validation_started", "gate_failed")
        sequence: Sequence number for multiple events of same type
        
    Returns:
        Deterministic event ID
        
    Example:
        >>> eid = generate_event_id("corr_123", "validation_started", 0)
    """
    context = f"{correlation_id}:{event_type}:{sequence}"
    return generate_deterministic_id(context, "event_id")


def generate_correlation_id(policy_unit_id: str, phase: str, run_counter: int = 0) -> str:
    """
    Generate deterministic correlation ID.
    
    Args:
        policy_unit_id: Unique identifier for policy document/unit
        phase: Phase identifier (e.g., "phase_0", "phase_2")
        run_counter: Counter for multiple runs (default 0)
        
    Returns:
        Deterministic correlation ID
        
    Example:
        >>> cid = generate_correlation_id("PDT_2024_MUNICIPALITY_X", "phase_2", 0)
    """
    context = f"{policy_unit_id}:{phase}:{run_counter}"
    return generate_deterministic_id(context, "correlation_id")


def generate_report_id(policy_unit_id: str, report_type: str) -> str:
    """
    Generate deterministic report ID.
    
    Args:
        policy_unit_id: Unique identifier for policy document/unit
        report_type: Type of report (e.g., "final", "interim")
        
    Returns:
        Deterministic report ID
        
    Example:
        >>> rid = generate_report_id("PDT_2024_MUNICIPALITY_X", "final")
    """
    context = f"{policy_unit_id}:{report_type}"
    return generate_deterministic_id(context, "report_id")


class DeterministicIDGenerator:
    """
    Stateful deterministic ID generator with sequence counters.
    
    Maintains counters per context to generate unique but deterministic IDs
    for multiple events/items within the same context.
    
    Usage:
        >>> gen = DeterministicIDGenerator("corr_12345")
        >>> event_id_1 = gen.generate_event_id("validation_started")
        >>> event_id_2 = gen.generate_event_id("validation_started")
        >>> assert event_id_1 != event_id_2  # Different due to sequence counter
        >>> 
        >>> # But reproducible across runs:
        >>> gen2 = DeterministicIDGenerator("corr_12345")
        >>> event_id_1b = gen2.generate_event_id("validation_started")
        >>> assert event_id_1 == event_id_1b  # Same context + same sequence = same ID
    """
    
    def __init__(self, base_context: str):
        """
        Initialize ID generator with base context.
        
        Args:
            base_context: Base context (e.g., correlation_id, policy_unit_id)
        """
        self.base_context = base_context
        self._event_counters: dict[str, int] = {}
    
    def generate_event_id(self, event_type: str) -> str:
        """
        Generate event ID with automatic sequence counter.
        
        Args:
            event_type: Type of event
            
        Returns:
            Deterministic event ID
        """
        sequence = self._event_counters.get(event_type, 0)
        self._event_counters[event_type] = sequence + 1
        return generate_event_id(self.base_context, event_type, sequence)
    
    def generate_id(self, component: str, sequence: Optional[int] = None) -> str:
        """
        Generate generic deterministic ID.
        
        Args:
            component: Component identifier
            sequence: Optional explicit sequence (auto-increments if None)
            
        Returns:
            Deterministic ID
        """
        if sequence is None:
            sequence = self._event_counters.get(component, 0)
            self._event_counters[component] = sequence + 1
        
        context = f"{self.base_context}:{component}:{sequence}"
        return generate_deterministic_id(context, component)
    
    def reset_counter(self, component: str) -> None:
        """Reset counter for a specific component."""
        self._event_counters[component] = 0
    
    def reset_all_counters(self) -> None:
        """Reset all counters."""
        self._event_counters.clear()


# Convenience function for backward compatibility
def deterministic_uuid(context: str, component: str = "default") -> str:
    """
    Drop-in replacement for uuid.uuid4() that generates deterministic IDs.
    
    **IMPORTANT:** Requires context parameter. This is intentional to enforce
    passing execution context for reproducibility.
    
    Args:
        context: Execution context (correlation_id, policy_unit_id, etc.)
        component: Component identifier (default: "default")
        
    Returns:
        Deterministic UUID-format string
        
    Example:
        >>> # Instead of: event_id = str(uuid.uuid4())
        >>> event_id = deterministic_uuid(correlation_id, "event_id")
    """
    return generate_deterministic_id(context, component)
