"""
Phase 4-7 Nexus Interface.

Defines the data flow connections between phases 4, 5, 6, and 7
in the FARFAN pipeline aggregation cascade.

Phase 4: Dimension Aggregation
Phase 5: Area Aggregation
Phase 6: Cluster Aggregation
Phase 7: Macro Evaluation
"""

# GNEA METADATA
__version__ = "1.0.0"
__module_type__ = "ORCH"  # Orchestration - Specification
__criticality__ = "HIGH"
__lifecycle__ = "ACTIVE"
__execution_pattern__ = "Singleton"
__phase_scope__ = "4,5,6,7"
__purpose__ = "Declarative data flow specification for aggregation cascade"
__compliance_status__ = "GNEA_COMPLIANT"

from dataclasses import dataclass
from enum import Enum


class NexusDirection(str, Enum):
    """Direction of data flow between nodes."""

    DELIVERS = "delivers"
    RECEIVES = "receives"
    BIDIRECTIONAL = "bidirectional"


@dataclass(frozen=True)
class NexusNode:
    """
    Represents a connection point in the phase nexus.

    Attributes:
        node_id: Unique identifier for the node
        phase: Phase number (4, 5, 6, 7, or adjacent phases 3, 8)
        node_type: Type of node (input, output, processor)
        description: Human-readable description
    """

    node_id: str
    phase: int
    node_type: str  # "input", "output", "processor"
    description: str


@dataclass(frozen=True)
class NexusRelationship:
    """
    Defines a relationship between two nexus nodes.

    Attributes:
        from_node: Source node
        to_node: Destination node
        direction: Flow direction
        data_type: Type of data transferred
        description: Human-readable description
    """

    from_node: NexusNode
    to_node: NexusNode
    direction: NexusDirection
    data_type: str
    description: str


class Phase4_7NexusInterface:
    """
    Interface defining the nexus between phases 4-7.

    This class provides:
    - Node definitions for each phase
    - Relationship mappings between phases
    - Data flow validation
    - Visualization of the phase connections
    """

    # Define all nodes
    NODES: dict[str, NexusNode] = {
        # Phase 4: Dimension Aggregation
        "phase4_dimension_aggregation_input": NexusNode(
            node_id="phase4_dimension_aggregation_input",
            phase=4,
            node_type="input",
            description="Receives scored results from Phase 3",
        ),
        "phase4_dimension_aggregation_processor": NexusNode(
            node_id="phase4_dimension_aggregation_processor",
            phase=4,
            node_type="processor",
            description="Aggregates scores by dimension",
        ),
        "phase4_dimension_aggregation_output": NexusNode(
            node_id="phase4_dimension_aggregation_output",
            phase=4,
            node_type="output",
            description="Emits dimension-level scores",
        ),
        # Phase 5: Area Aggregation
        "phase5_area_aggregation_input": NexusNode(
            node_id="phase5_area_aggregation_input",
            phase=5,
            node_type="input",
            description="Receives dimension scores from Phase 4",
        ),
        "phase5_area_aggregation_processor": NexusNode(
            node_id="phase5_area_aggregation_processor",
            phase=5,
            node_type="processor",
            description="Aggregates scores by policy area",
        ),
        "phase5_area_aggregation_output": NexusNode(
            node_id="phase5_area_aggregation_output",
            phase=5,
            node_type="output",
            description="Emits area-level scores",
        ),
        # Phase 6: Cluster Aggregation
        "phase6_cluster_aggregation_input": NexusNode(
            node_id="phase6_cluster_aggregation_input",
            phase=6,
            node_type="input",
            description="Receives area scores from Phase 5",
        ),
        "phase6_cluster_aggregation_processor": NexusNode(
            node_id="phase6_cluster_aggregation_processor",
            phase=6,
            node_type="processor",
            description="Aggregates scores by cluster",
        ),
        "phase6_cluster_aggregation_output": NexusNode(
            node_id="phase6_cluster_aggregation_output",
            phase=6,
            node_type="output",
            description="Emits cluster-level scores",
        ),
        # Phase 7: Macro Evaluation
        "phase7_macro_evaluation_input": NexusNode(
            node_id="phase7_macro_evaluation_input",
            phase=7,
            node_type="input",
            description="Receives cluster scores from Phase 6",
        ),
        "phase7_macro_evaluation_processor": NexusNode(
            node_id="phase7_macro_evaluation_processor",
            phase=7,
            node_type="processor",
            description="Computes macro-level evaluation",
        ),
        "phase7_macro_evaluation_output": NexusNode(
            node_id="phase7_macro_evaluation_output",
            phase=7,
            node_type="output",
            description="Emits final macro score",
        ),
    }

    # Define all relationships
    RELATIONSHIPS = [
        # External entry relationship
        NexusRelationship(
            from_node=NexusNode(
                node_id="phase3_quality_scoring_output",
                phase=3,
                node_type="output",
                description="Phase 3 output node",
            ),
            to_node=NODES["phase4_dimension_aggregation_input"],
            direction=NexusDirection.DELIVERS,
            data_type="ScoredResult[]",
            description="Phase 3 delivers scored results to Phase 4",
        ),
        # Phase 4 → Phase 5
        NexusRelationship(
            from_node=NODES["phase4_dimension_aggregation_output"],
            to_node=NODES["phase5_area_aggregation_input"],
            direction=NexusDirection.DELIVERS,
            data_type="DimensionScore[]",
            description="Phase 4 delivers dimension scores to Phase 5",
        ),
        # Phase 5 → Phase 6
        NexusRelationship(
            from_node=NODES["phase5_area_aggregation_output"],
            to_node=NODES["phase6_cluster_aggregation_input"],
            direction=NexusDirection.DELIVERS,
            data_type="AreaScore[]",
            description="Phase 5 delivers area scores to Phase 6",
        ),
        # Phase 6 → Phase 7
        NexusRelationship(
            from_node=NODES["phase6_cluster_aggregation_output"],
            to_node=NODES["phase7_macro_evaluation_input"],
            direction=NexusDirection.DELIVERS,
            data_type="ClusterScore[]",
            description="Phase 6 delivers cluster scores to Phase 7",
        ),
        # External exit relationship
        NexusRelationship(
            from_node=NODES["phase7_macro_evaluation_output"],
            to_node=NexusNode(
                node_id="phase8_semantic_input",
                phase=8,
                node_type="input",
                description="Phase 8 input node",
            ),
            direction=NexusDirection.DELIVERS,
            data_type="MacroScore",
            description="Phase 7 delivers macro score to Phase 8",
        ),
    ]

    @classmethod
    def get_node(cls, node_id: str) -> NexusNode | None:
        """
        Get a node by its ID.

        Args:
            node_id: Unique node identifier

        Returns:
            NexusNode if found, None otherwise
        """
        return cls.NODES.get(node_id)

    @classmethod
    def get_nodes_by_phase(cls, phase: int) -> list[NexusNode]:
        """
        Get all nodes for a specific phase.

        Args:
            phase: Phase number (4, 5, 6, or 7)

        Returns:
            List of NexusNode objects
        """
        return [node for node in cls.NODES.values() if node.phase == phase]

    @classmethod
    def get_relationships_from_node(cls, node_id: str) -> list[NexusRelationship]:
        """
        Get all relationships where the specified node is the source.

        Args:
            node_id: Source node ID

        Returns:
            List of NexusRelationship objects
        """
        return [rel for rel in cls.RELATIONSHIPS if rel.from_node.node_id == node_id]

    @classmethod
    def get_relationships_to_node(cls, node_id: str) -> list[NexusRelationship]:
        """
        Get all relationships where the specified node is the destination.

        Args:
            node_id: Destination node ID

        Returns:
            List of NexusRelationship objects
        """
        return [rel for rel in cls.RELATIONSHIPS if rel.to_node.node_id == node_id]

    @classmethod
    def validate_data_flow(cls) -> tuple[bool, list[str]]:
        """
        Validate that the data flow is properly connected.

        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        messages = []

        # Check that all phases have at least one input and one output node
        for phase in [4, 5, 6, 7]:
            nodes = cls.get_nodes_by_phase(phase)
            input_nodes = [n for n in nodes if n.node_type == "input"]
            output_nodes = [n for n in nodes if n.node_type == "output"]

            if not input_nodes:
                messages.append(f"Phase {phase}: No input nodes defined")
            if not output_nodes:
                messages.append(f"Phase {phase}: No output nodes defined")

        # Check that each internal output node has a corresponding input node
        for phase in [4, 5, 6]:
            output_nodes = [n for n in cls.get_nodes_by_phase(phase) if n.node_type == "output"]
            for output_node in output_nodes:
                relationships = cls.get_relationships_from_node(output_node.node_id)
                if not relationships:
                    messages.append(f"{output_node.node_id}: No downstream connections")

        # Check that the entry node has a source
        entry_node = cls.NODES["phase4_dimension_aggregation_input"]
        entry_relationships = cls.get_relationships_to_node(entry_node.node_id)
        if not entry_relationships:
            messages.append(f"{entry_node.node_id}: No upstream connections")

        # Check that the exit node has a destination
        exit_node = cls.NODES["phase7_macro_evaluation_output"]
        exit_relationships = cls.get_relationships_from_node(exit_node.node_id)
        if not exit_relationships:
            messages.append(f"{exit_node.node_id}: No downstream connections")

        is_valid = len(messages) == 0
        return is_valid, messages

    @classmethod
    def visualize_flow(cls) -> str:
        """
        Generate a text-based visualization of the data flow.

        Returns:
            String representation of the flow
        """
        lines = []
        lines.append("Phase 4-7 Nexus Data Flow:")
        lines.append("=" * 60)

        # External entry
        lines.append("")
        lines.append("EXTERNAL ENTRY:")
        lines.append("  Phase 3 (phase3_quality_scoring_output)")
        lines.append("    ↓ ScoredResult[]")
        lines.append("  Phase 4 (phase4_dimension_aggregation_input) ★ ENTRY NODE")

        # Phase 4 → 5
        lines.append("")
        lines.append("INTERNAL FLOW:")
        lines.append("  Phase 4 (phase4_dimension_aggregation_output)")
        lines.append("    ↓ DimensionScore[]")
        lines.append("  Phase 5 (phase5_area_aggregation_input)")

        # Phase 5 → 6
        lines.append("")
        lines.append("  Phase 5 (phase5_area_aggregation_output)")
        lines.append("    ↓ AreaScore[]")
        lines.append("  Phase 6 (phase6_cluster_aggregation_input)")

        # Phase 6 → 7
        lines.append("")
        lines.append("  Phase 6 (phase6_cluster_aggregation_output)")
        lines.append("    ↓ ClusterScore[]")
        lines.append("  Phase 7 (phase7_macro_evaluation_input)")

        # External exit
        lines.append("")
        lines.append("EXTERNAL EXIT:")
        lines.append("  Phase 7 (phase7_macro_evaluation_output) ★ EXIT NODE")
        lines.append("    ↓ MacroScore")
        lines.append("  Phase 8 (phase8_semantic_input)")

        lines.append("")
        lines.append("=" * 60)
        lines.append("★ = Phase boundary")

        return "\n".join(lines)


def get_nexus_interface() -> Phase4_7NexusInterface:
    """
    Get the Phase 4-7 nexus interface.

    Returns:
        Phase4_7NexusInterface instance
    """
    return Phase4_7NexusInterface()


def validate_nexus_connections() -> tuple[bool, list[str]]:
    """
    Validate all nexus connections.

    Returns:
        Tuple of (is_valid, validation_messages)
    """
    return Phase4_7NexusInterface.validate_data_flow()


def print_nexus_flow() -> None:
    """Print a visualization of the nexus data flow."""
    print(Phase4_7NexusInterface.visualize_flow())


__all__ = [
    "NexusDirection",
    "NexusNode",
    "NexusRelationship",
    "Phase4_7NexusInterface",
    "get_nexus_interface",
    "print_nexus_flow",
    "validate_nexus_connections",
]
