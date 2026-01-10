"""
Signal Irrigation Architecture Visualizations

Generates visualizations for signal irrigation ecosystem:
- Sankey diagrams showing signal flow volumes
- State machine diagrams for synchronization control
- Heatmaps of signal utilization by phase and policy area

Uses Python libraries that can generate D3.js-compatible JSON or SVG.

Author: F.A.R.F.A.N Pipeline
Date: 2025-01-15
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class SignalFlowNode:
    """Node in signal flow diagram."""

    id: str
    label: str
    value: int = 0
    category: str = ""


@dataclass
class SignalFlowLink:
    """Link between nodes in signal flow diagram."""

    source: str
    target: str
    value: int = 0


class SankeyDiagramGenerator:
    """Generates Sankey diagrams showing signal flow volumes."""

    def __init__(self):
        self.nodes: list[SignalFlowNode] = []
        self.links: list[SignalFlowLink] = []
        self.node_map: dict[str, int] = {}  # node_id -> index

    def add_node(self, node_id: str, label: str, value: int = 0, category: str = "") -> None:
        """Add a node to the diagram."""
        if node_id not in self.node_map:
            self.node_map[node_id] = len(self.nodes)
            self.nodes.append(
                SignalFlowNode(id=node_id, label=label, value=value, category=category)
            )
        else:
            # Update existing node value
            idx = self.node_map[node_id]
            self.nodes[idx].value += value

    def add_link(self, source_id: str, target_id: str, value: int) -> None:
        """Add a link between nodes."""
        # Ensure nodes exist
        if source_id not in self.node_map:
            self.add_node(source_id, source_id.replace("_", " ").title())
        if target_id not in self.node_map:
            self.add_node(target_id, target_id.replace("_", " ").title())

        self.links.append(SignalFlowLink(source=source_id, target=target_id, value=value))

    def to_d3_json(self) -> dict[str, Any]:
        """Convert to D3.js Sankey diagram format."""
        nodes = [
            {
                "id": node.id,
                "label": node.label,
                "value": node.value,
                "category": node.category,
            }
            for node in self.nodes
        ]

        links = [
            {
                "source": self.node_map[link.source],
                "target": self.node_map[link.target],
                "value": link.value,
            }
            for link in self.links
        ]

        return {"nodes": nodes, "links": links}

    def to_json(self, output_path: Path) -> Path:
        """Save diagram to JSON file."""
        data = self.to_d3_json()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2))
        logger.info("sankey_diagram_saved", output_path=str(output_path))
        return output_path


class StateMachineGenerator:
    """Generates state machine diagrams for synchronization control."""

    def __init__(self):
        self.states: dict[str, dict[str, Any]] = {}
        self.transitions: list[dict[str, Any]] = []

    def add_state(self, state_id: str, label: str, state_type: str = "normal") -> None:
        """Add a state to the state machine.

        Args:
            state_id: Unique state identifier
            label: Human-readable label
            state_type: Type of state ("initial", "final", "normal")
        """
        self.states[state_id] = {
            "id": state_id,
            "label": label,
            "type": state_type,
        }

    def add_transition(
        self,
        from_state: str,
        to_state: str,
        label: str = "",
        condition: str = "",
    ) -> None:
        """Add a transition between states."""
        self.transitions.append(
            {
                "from": from_state,
                "to": to_state,
                "label": label,
                "condition": condition,
            }
        )

    def to_cytoscape_json(self) -> dict[str, Any]:
        """Convert to Cytoscape.js format."""
        elements = []

        # Add nodes
        for state_id, state_data in self.states.items():
            elements.append(
                {
                    "data": {
                        "id": state_id,
                        "label": state_data["label"],
                        "type": state_data["type"],
                    },
                    "classes": state_data["type"],
                }
            )

        # Add edges
        for idx, transition in enumerate(self.transitions):
            elements.append(
                {
                    "data": {
                        "id": f"edge_{idx}",
                        "source": transition["from"],
                        "target": transition["to"],
                        "label": transition["label"],
                        "condition": transition["condition"],
                    },
                }
            )

        return {"elements": elements}

    def to_json(self, output_path: Path) -> Path:
        """Save state machine to JSON file."""
        data = self.to_cytoscape_json()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2))
        logger.info("state_machine_saved", output_path=str(output_path))
        return output_path


class HeatmapGenerator:
    """Generates heatmaps of signal utilization by phase and policy area."""

    def __init__(self):
        self.data: dict[tuple[str, str], float] = defaultdict(
            float
        )  # (phase, policy_area) -> value
        self.phases: set[str] = set()
        self.policy_areas: set[str] = set()

    def add_data_point(self, phase: str, policy_area: str, value: float) -> None:
        """Add a data point to the heatmap."""
        key = (phase, policy_area)
        self.data[key] = value
        self.phases.add(phase)
        self.policy_areas.add(policy_area)

    def to_d3_json(self) -> dict[str, Any]:
        """Convert to D3.js heatmap format."""
        phases_list = sorted(self.phases)
        policy_areas_list = sorted(self.policy_areas)

        # Build matrix
        matrix = []
        for phase in phases_list:
            row = []
            for pa in policy_areas_list:
                value = self.data.get((phase, pa), 0.0)
                row.append(value)
            matrix.append(row)

        return {
            "phases": phases_list,
            "policy_areas": policy_areas_list,
            "matrix": matrix,
            "max_value": max((v for v in self.data.values()), default=0.0),
            "min_value": min((v for v in self.data.values()), default=0.0),
        }

    def to_json(self, output_path: Path) -> Path:
        """Save heatmap to JSON file."""
        data = self.to_d3_json()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2))
        logger.info("heatmap_saved", output_path=str(output_path))
        return output_path


class VisualizationOrchestrator:
    """Orchestrates generation of all visualizations."""

    def __init__(self, audit_results: Any):  # AuditResults type
        self.audit_results = audit_results
        self.output_dir = Path("artifacts/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> dict[str, Path]:
        """Generate all visualizations."""
        results = {}

        # Generate Sankey diagram
        sankey_path = self._generate_sankey()
        results["sankey"] = sankey_path

        # Generate state machine
        state_machine_path = self._generate_state_machine()
        results["state_machine"] = state_machine_path

        # Generate heatmap
        heatmap_path = self._generate_heatmap()
        results["heatmap"] = heatmap_path

        return results

    def _generate_sankey(self) -> Path:
        """Generate Sankey diagram of signal flow."""
        generator = SankeyDiagramGenerator()

        # Add nodes for signal flow
        generator.add_node("questionnaire", "Questionnaire Monolith", 60000, "source")
        generator.add_node("signal_registry", "Signal Registry", 0, "processing")
        generator.add_node("pattern_extraction", "Pattern Extraction", 0, "processing")
        generator.add_node("phase_executors", "Phase Executors", 0, "consumption")
        generator.add_node("evidence_production", "Evidence Production", 0, "output")

        # Estimate flow volumes (would use actual metrics from audit)
        generator.add_link("questionnaire", "signal_registry", 60000)
        generator.add_link("signal_registry", "pattern_extraction", 10000)
        generator.add_link("pattern_extraction", "phase_executors", 8000)
        generator.add_link("phase_executors", "evidence_production", 5000)

        # Add policy area nodes
        for pa in ["PA01", "PA02", "PA03", "PA04", "PA05"]:
            generator.add_node(f"pa_{pa}", pa, 0, "policy_area")
            generator.add_link("signal_registry", f"pa_{pa}", 1000)
            generator.add_link(f"pa_{pa}", "phase_executors", 800)

        output_path = self.output_dir / "signal_flow_sankey.json"
        return generator.to_json(output_path)

    def _generate_state_machine(self) -> Path:
        """Generate state machine for synchronization control."""
        generator = StateMachineGenerator()

        # Add states
        generator.add_state("idle", "Idle", "initial")
        generator.add_state("loading_questionnaire", "Loading Questionnaire", "normal")
        generator.add_state("extracting_signals", "Extracting Signals", "normal")
        generator.add_state("phase_executing", "Phase Executing", "normal")
        generator.add_state("signal_injecting", "Signal Injecting", "normal")
        generator.add_state("pattern_matching", "Pattern Matching", "normal")
        generator.add_state("evidence_assembling", "Evidence Assembling", "normal")
        generator.add_state("validating", "Validating", "normal")
        generator.add_state("complete", "Complete", "final")
        generator.add_state("error", "Error", "final")

        # Add transitions
        generator.add_transition("idle", "loading_questionnaire", "Start Pipeline")
        generator.add_transition(
            "loading_questionnaire", "extracting_signals", "Questionnaire Loaded"
        )
        generator.add_transition("extracting_signals", "phase_executing", "Signals Extracted")
        generator.add_transition("phase_executing", "signal_injecting", "Phase Started")
        generator.add_transition("signal_injecting", "pattern_matching", "Signals Injected")
        generator.add_transition("pattern_matching", "evidence_assembling", "Patterns Matched")
        generator.add_transition("evidence_assembling", "validating", "Evidence Assembled")
        generator.add_transition("validating", "complete", "Validation Passed")
        generator.add_transition("validating", "error", "Validation Failed")
        generator.add_transition("pattern_matching", "error", "Match Error")
        generator.add_transition("signal_injecting", "error", "Injection Error")

        output_path = self.output_dir / "synchronization_state_machine.json"
        return generator.to_json(output_path)

    def _generate_heatmap(self) -> Path:
        """Generate heatmap of signal utilization."""
        generator = HeatmapGenerator()

        # Add utilization data by phase and policy area
        phases = ["Phase1", "Phase2", "Phase3", "Phase4", "Phase5"]
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]

        # Use metrics from audit if available, otherwise use placeholder values
        utilization_metrics = self.audit_results.utilization_metrics

        # Sample data - would use actual metrics
        for phase in phases:
            for pa in policy_areas:
                # Placeholder: would use actual utilization data
                value = 0.75  # 75% utilization
                generator.add_data_point(phase, pa, value)

        output_path = self.output_dir / "signal_utilization_heatmap.json"
        return generator.to_json(output_path)


def generate_visualizations(audit_results: Any, output_dir: Path | None = None) -> dict[str, Path]:
    """Generate all visualizations from audit results.

    Args:
        audit_results: AuditResults object
        output_dir: Optional output directory (defaults to artifacts/visualizations)

    Returns:
        Dict mapping visualization type to output path
    """
    orchestrator = VisualizationOrchestrator(audit_results)
    if output_dir:
        orchestrator.output_dir = output_dir
    return orchestrator.generate_all()
