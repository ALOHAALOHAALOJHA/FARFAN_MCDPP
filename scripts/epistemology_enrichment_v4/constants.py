from __future__ import annotations

from typing import Final


CLASS_LEVELS: Final[set[str]] = {
    "N1-EMP",
    "N2-INF",
    "N3-AUD",
    "N4-SYN",
    "INFRASTRUCTURE",
    "PROTOCOL",
}

CLASS_EPISTEMOLOGIES: Final[set[str]] = {
    "POSITIVIST_EMPIRICAL",
    "BAYESIAN_PROBABILISTIC",
    "DETERMINISTIC_LOGICAL",
    "CAUSAL_MECHANISTIC",
    "POPPERIAN_FALSIFICATIONIST",
    "CRITICAL_REFLEXIVE",
    "NONE",
}

METHOD_LEVELS: Final[set[str]] = {
    "N1-EMP",
    "N2-INF",
    "N3-AUD",
    "N4-SYN",
    "INFRASTRUCTURE",
}

# Minimal set (spec) + allowed set (audit_v4_rigorous.py)
VETO_ACTIONS: Final[set[str]] = {
    "block_branch",
    "reduce_confidence",
    "flag_caution",
    "suppress_fact",
    "invalidate_graph",
    "flag_and_reduce",
    "flag_insufficiency",
    "downgrade_confidence_to_zero",
    "flag_invalid_sequence",
    "suppress_contradicting_nodes",
}
