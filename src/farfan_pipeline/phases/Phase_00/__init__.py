"""
Phase 0: Validation, Hardening & Bootstrap
==========================================

The foundational layer of the F.A.R.F.A.N pipeline that executes before any
analytical computation. It guarantees a deterministic, resource-bounded, and
validated environment.
"""

from .phase0_90_01_verified_pipeline_runner import VerifiedPipelineRunner

__all__ = ["VerifiedPipelineRunner"]
