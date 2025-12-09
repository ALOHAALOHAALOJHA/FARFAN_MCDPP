"""Shim for pipeline connector used by the dashboard.

References the implementation in `farfan_pipeline.api.pipeline_connector`.
"""

from ..api.pipeline_connector import PipelineConnector, PipelineResult

__all__ = ["PipelineConnector", "PipelineResult"]
