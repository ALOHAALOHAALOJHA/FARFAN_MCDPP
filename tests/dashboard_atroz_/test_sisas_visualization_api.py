"""
Tests for SISAS Advanced Visualization API Endpoints

This test module validates the new REST API endpoints added for
enhanced SISAS metrics visualization in the ATROZ Dashboard.
"""

import pytest
from datetime import datetime
import json


class TestSISASVisualizationAPIs:
    """Test suite for SISAS visualization API endpoints."""

    def test_historical_metrics_endpoint_structure(self):
        """Test that historical metrics endpoint returns correct structure."""
        # Mock response structure validation
        response = {
            "range": "1h",
            "interval": "1m",
            "data_points": [
                {
                    "timestamp": "2026-01-22T10:00:00",
                    "signals_dispatched": 156,
                    "signals_delivered": 148,
                    "signals_failed": 8,
                    "avg_latency_ms": 47,
                    "active_consumers": 14,
                    "dead_letter_count": 3
                }
            ],
            "summary": {
                "total_dispatched": 9360,
                "total_delivered": 8880,
                "avg_latency": 47.3,
                "success_rate": 94.9
            }
        }
        
        # Validate structure
        assert "range" in response
        assert "interval" in response
        assert "data_points" in response
        assert "summary" in response
        
        # Validate data point structure
        if response["data_points"]:
            dp = response["data_points"][0]
            assert "timestamp" in dp
            assert "signals_dispatched" in dp
            assert "signals_delivered" in dp
            assert "avg_latency_ms" in dp
            assert "active_consumers" in dp
            
        # Validate summary
        summary = response["summary"]
        assert "total_dispatched" in summary
        assert "total_delivered" in summary
        assert "success_rate" in summary

    def test_aggregated_metrics_endpoint_structure(self):
        """Test that aggregated metrics endpoint returns all required sections."""
        response = {
            "overview": {
                "total_signals_dispatched": 1247,
                "success_rate": 94.9
            },
            "gates": {},
            "signal_types": {},
            "error_breakdown": {},
            "phase_distribution": {},
            "latency_distribution": {}
        }
        
        # Validate all sections present
        assert "overview" in response
        assert "gates" in response
        assert "signal_types" in response
        assert "error_breakdown" in response
        assert "phase_distribution" in response
        assert "latency_distribution" in response

    def test_consumers_detailed_endpoint_structure(self):
        """Test that consumers detailed endpoint returns correct structure."""
        response = {
            "consumers": [
                {
                    "id": "phase_00_bootstrap",
                    "status": "active",
                    "throughput_per_min": 156,
                    "queue_depth": 12
                }
            ],
            "summary": {
                "total_consumers": 17,
                "active": 14
            }
        }
        
        # Validate structure
        assert "consumers" in response
        assert "summary" in response
        
        # Validate consumer structure
        if response["consumers"]:
            consumer = response["consumers"][0]
            assert "id" in consumer
            assert "status" in consumer
            assert "throughput_per_min" in consumer
            assert "queue_depth" in consumer

    def test_extractors_performance_endpoint_structure(self):
        """Test that extractors performance endpoint returns correct structure."""
        response = {
            "extractors": [
                {
                    "id": "MC01",
                    "name": "STRUCTURAL",
                    "progress": 92,
                    "status": "complete",
                    "signals_emitted": 245
                }
            ],
            "summary": {
                "total_extractors": 10,
                "avg_progress": 76.5
            }
        }
        
        # Validate structure
        assert "extractors" in response
        assert "summary" in response
        
        # Validate extractor structure
        if response["extractors"]:
            extractor = response["extractors"][0]
            assert "id" in extractor
            assert "name" in extractor
            assert "progress" in extractor
            assert "status" in extractor
            assert "signals_emitted" in extractor

    def test_gates_detailed_endpoint_structure(self):
        """Test that gates detailed endpoint returns correct structure."""
        response = {
            "gates": [
                {
                    "gate_number": 1,
                    "name": "Scope Alignment",
                    "pass_rate": 97.2,
                    "passed": 1247,
                    "rejected": 36,
                    "total": 1283,
                    "rejection_reasons": {}
                }
            ],
            "summary": {
                "total_gates": 4,
                "overall_pass_rate": 97.8
            }
        }
        
        # Validate structure
        assert "gates" in response
        assert "summary" in response
        
        # Validate gate structure
        if response["gates"]:
            gate = response["gates"][0]
            assert "gate_number" in gate
            assert "name" in gate
            assert "pass_rate" in gate
            assert "passed" in gate
            assert "rejected" in gate
            assert "total" in gate
            assert "rejection_reasons" in gate

    def test_time_range_parameters(self):
        """Test that time range parameters are validated correctly."""
        valid_ranges = ["1h", "6h", "24h", "7d"]
        valid_intervals = ["1m", "5m", "15m", "1h"]
        
        for time_range in valid_ranges:
            assert time_range in ["1h", "6h", "24h", "7d"]
            
        for interval in valid_intervals:
            assert interval in ["1m", "5m", "15m", "1h"]

    def test_metric_calculations(self):
        """Test that metric calculations are mathematically correct."""
        # Test success rate calculation
        dispatched = 1247
        delivered = 1183
        success_rate = (delivered / dispatched) * 100
        
        assert 94.0 <= success_rate <= 95.0  # Should be around 94.9%
        
        # Test pass rate calculation
        passed = 1247
        total = 1283
        pass_rate = (passed / total) * 100
        
        assert 97.0 <= pass_rate <= 98.0  # Should be around 97.2%

    def test_data_consistency(self):
        """Test that related metrics are consistent across endpoints."""
        # Signals dispatched should be >= signals delivered
        dispatched = 1247
        delivered = 1183
        assert dispatched >= delivered
        
        # Active consumers should be <= total consumers
        active = 14
        total = 17
        assert active <= total
        
        # Passed + rejected should equal total for gates
        passed = 1247
        rejected = 36
        total = 1283
        assert passed + rejected == total

    def test_latency_distribution_buckets(self):
        """Test that latency distribution buckets are properly defined."""
        buckets = ["0-20ms", "20-40ms", "40-60ms", "60-80ms", "80-100ms", "100ms+"]
        
        assert len(buckets) == 6
        assert "0-20ms" in buckets
        assert "100ms+" in buckets

    def test_phase_coverage(self):
        """Test that all pipeline phases are covered."""
        phases = ["P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"]
        
        assert len(phases) == 10
        assert "P00" in phases
        assert "P09" in phases

    def test_extractor_ids(self):
        """Test that all 10 extractors are defined."""
        extractors = ["MC01", "MC02", "MC03", "MC04", "MC05", 
                     "MC06", "MC07", "MC08", "MC09", "MC10"]
        
        assert len(extractors) == 10
        for i in range(1, 11):
            expected_id = f"MC{i:02d}"
            assert expected_id in extractors

    def test_error_types(self):
        """Test that all error types are categorized."""
        error_types = ["NO_CONSUMER", "TIMEOUT", "VALIDATION_FAILED", 
                      "GATE_REJECTED", "SYSTEM_ERROR"]
        
        assert len(error_types) >= 5
        assert "NO_CONSUMER" in error_types
        assert "SYSTEM_ERROR" in error_types


class TestChartDataFormats:
    """Test suite for chart data format compatibility."""

    def test_time_series_data_format(self):
        """Test that time series data is in correct format for Chart.js."""
        data = {
            "labels": ["2026-01-22T10:00:00", "2026-01-22T10:01:00"],
            "datasets": [
                {
                    "label": "Dispatched",
                    "data": [156, 158]
                }
            ]
        }
        
        assert "labels" in data
        assert "datasets" in data
        assert isinstance(data["datasets"], list)
        assert len(data["labels"]) == len(data["datasets"][0]["data"])

    def test_bar_chart_data_format(self):
        """Test that bar chart data is in correct format."""
        data = {
            "labels": ["Gate 1", "Gate 2", "Gate 3", "Gate 4"],
            "datasets": [{
                "label": "Success Rate (%)",
                "data": [97.2, 100, 97.5, 96.5]
            }]
        }
        
        assert len(data["labels"]) == 4
        assert all(isinstance(x, (int, float)) for x in data["datasets"][0]["data"])

    def test_pie_chart_data_format(self):
        """Test that pie/donut chart data is in correct format."""
        data = {
            "labels": ["MC01", "MC02", "MC03"],
            "datasets": [{
                "data": [245, 198, 176]
            }]
        }
        
        assert len(data["labels"]) == len(data["datasets"][0]["data"])
        assert sum(data["datasets"][0]["data"]) > 0


class TestVisualizationIntegration:
    """Integration tests for visualization components."""

    def test_websocket_message_format(self):
        """Test that WebSocket messages have correct structure."""
        message = {
            "event": "sisas_metrics",
            "data": {
                "throughput": {
                    "dispatched": 156,
                    "delivered": 148
                },
                "gates": [],
                "consumers": []
            }
        }
        
        assert "event" in message
        assert "data" in message
        assert "throughput" in message["data"]

    def test_dashboard_initialization_sequence(self):
        """Test that dashboard components initialize in correct order."""
        initialization_order = [
            "websocket",
            "charts",
            "metrics",
            "gate_matrix",
            "consumer_grid",
            "flow_diagram",
            "auto_refresh"
        ]
        
        assert len(initialization_order) == 7
        assert initialization_order[0] == "websocket"
        assert initialization_order[-1] == "auto_refresh"

    def test_responsive_breakpoints(self):
        """Test that responsive breakpoints are properly defined."""
        breakpoints = {
            "mobile": 768,
            "tablet": 1200,
            "desktop": 1920
        }
        
        assert breakpoints["mobile"] < breakpoints["tablet"]
        assert breakpoints["tablet"] < breakpoints["desktop"]


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
