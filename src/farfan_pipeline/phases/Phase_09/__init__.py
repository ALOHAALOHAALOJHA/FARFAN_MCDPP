"""
Phase Nine: Output Generation
==============================

Phase 9 of the F.A.R.F.A.N pipeline responsible for generating final output
artifacts and reports from the processed policy documents.
"""

from . import (
    PHASE_9_CONSTANTS,
    phase9_10_00_phase_9_constants,
    phase9_10_00_report_assembly,
    phase9_10_00_report_generator,
    phase9_10_00_signal_enriched_reporting,
    phase9_15_00_institutional_entity_annex,
    report_generator,
)

from .PHASE_9_CONSTANTS import *
from .phase9_10_00_phase_9_constants import *
from .phase9_10_00_report_assembly import *
from .phase9_10_00_report_generator import *
from .phase9_10_00_signal_enriched_reporting import *
from .phase9_15_00_institutional_entity_annex import *
from .report_generator import *

__all__ = [
    # Constants
    'PHASE_9_CONSTANTS',
    'phase9_10_00_phase_9_constants',

    # Report generation modules
    'phase9_10_00_report_assembly',
    'phase9_10_00_report_generator',
    'phase9_10_00_signal_enriched_reporting',
    'report_generator',

    # Institutional modules
    'phase9_15_00_institutional_entity_annex',
]
