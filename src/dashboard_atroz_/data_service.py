"""Shim for the dashboard transformer service.

References the implementation in `farfan_pipeline.api.dashboard_data_service`.
"""

from ..api.dashboard_data_service import DashboardDataService

__all__ = ["DashboardDataService"]
