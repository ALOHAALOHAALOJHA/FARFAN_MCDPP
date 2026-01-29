"""
Signals Compatibility Package
==============================

Re-exports signal types from actual location.
"""

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.structural import (
    StructuralAlignmentSignal,
    AlignmentStatus,
    CanonicalMappingSignal,
)

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_types.types.integrity import (
    EventPresenceSignal,
    PresenceStatus,
    EventCompletenessSignal,
    CompletenessLevel,
)

__all__ = [
    "StructuralAlignmentSignal",
    "AlignmentStatus",
    "CanonicalMappingSignal",
    "EventPresenceSignal",
    "PresenceStatus",
    "EventCompletenessSignal",
    "CompletenessLevel",
]
