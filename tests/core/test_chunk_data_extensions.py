"""
Tests for ChunkData extended fields and validation.

Validates expected_elements schema expectations and document_position
byte offset tracking with comprehensive __post_init__ validation.
"""

import logging

import pytest

from farfan_pipeline.core.types import ChunkData


@pytest.fixture
def minimal_valid_chunk():
    """Minimal valid chunk with empty expected_elements and no document_position."""
    return ChunkData(
        id=100,
        text="Minimal chunk text",
        chunk_type="diagnostic",
        sentences=[],
        tables=[],
        start_pos=0,
        end_pos=50,
        confidence=0.9,
        policy_area_id="PA01",
        dimension_id="DIM01",
    )


@pytest.fixture
def chunk_with_position():
    """Chunk with document_position range."""
    return ChunkData(
        id=101,
        text="Chunk with position",
        chunk_type="activity",
        sentences=[0],
        tables=[],
        start_pos=0,
        end_pos=20,
        confidence=0.85,
        policy_area_id="PA02",
        dimension_id="DIM02",
        document_position=(1000, 2000),
    )


@pytest.fixture
def chunk_with_expected_elements():
    """Chunk with populated expected_elements schema."""
    return ChunkData(
        id=102,
        text="Chunk with schema expectations",
        chunk_type="indicator",
        sentences=[0, 1],
        tables=[],
        start_pos=0,
        end_pos=30,
        confidence=0.92,
        policy_area_id="PA03",
        dimension_id="DIM03",
        expected_elements=[
            {"type": "table", "required": True, "minimum": 1},
            {"type": "numeric_data", "required": False},
            {"type": "citation", "minimum": 0},
        ],
    )


@pytest.fixture
def fully_populated_chunk():
    """Chunk with both expected_elements and document_position."""
    return ChunkData(
        id=103,
        text="Fully populated chunk",
        chunk_type="resource",
        sentences=[0, 1, 2],
        tables=[0],
        start_pos=0,
        end_pos=25,
        confidence=0.95,
        policy_area_id="PA04",
        dimension_id="DIM04",
        expected_elements=[
            {"type": "budget_allocation", "required": True, "minimum": 1},
            {"type": "timeframe"},
        ],
        document_position=(5000, 5500),
    )


class TestChunkDataValidFields:
    """Test suite for valid ChunkData configurations."""

    def test_minimal_valid_chunk(self, minimal_valid_chunk):
        """Minimal chunk with empty fields should be valid."""
        assert minimal_valid_chunk.expected_elements == []
        assert minimal_valid_chunk.document_position is None
        assert minimal_valid_chunk.text == "Minimal chunk text"

    def test_chunk_with_position_range(self, chunk_with_position):
        """Chunk with valid position range should be accepted."""
        assert chunk_with_position.document_position == (1000, 2000)
        assert chunk_with_position.text == "Chunk with position"

    def test_chunk_with_expected_elements_schema(self, chunk_with_expected_elements):
        """Chunk with populated expected_elements should be valid."""
        assert len(chunk_with_expected_elements.expected_elements) == 3
        assert chunk_with_expected_elements.expected_elements[0]["type"] == "table"
        assert chunk_with_expected_elements.expected_elements[0]["required"] is True
        assert chunk_with_expected_elements.expected_elements[0]["minimum"] == 1
        assert (
            chunk_with_expected_elements.expected_elements[1]["type"] == "numeric_data"
        )
        assert chunk_with_expected_elements.expected_elements[1]["required"] is False
        assert chunk_with_expected_elements.expected_elements[2]["type"] == "citation"
        assert chunk_with_expected_elements.expected_elements[2]["minimum"] == 0

    def test_fully_populated_chunk_both_fields(self, fully_populated_chunk):
        """Chunk with both new fields populated should be valid."""
        assert len(fully_populated_chunk.expected_elements) == 2
        assert fully_populated_chunk.document_position == (5000, 5500)
        assert fully_populated_chunk.expected_elements[0]["type"] == "budget_allocation"
        assert fully_populated_chunk.expected_elements[1]["type"] == "timeframe"

    def test_zero_length_position_triggers_warning(self, caplog):
        """Zero-length position range should trigger warning log entry."""
        with caplog.at_level(logging.WARNING):
            chunk = ChunkData(
                id=999,
                text="Test zero-length position",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=26,
                confidence=0.8,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=(1500, 1500),
            )
        assert "zero-length document_position" in caplog.text
        assert chunk.document_position == (1500, 1500)


class TestChunkDataTextValidation:
    """Test suite for text field validation."""

    def test_empty_text_raises_error(self):
        """Empty text should raise ValueError."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            ChunkData(
                id=1,
                text="",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
            )

    def test_whitespace_only_text_raises_error(self):
        """Whitespace-only text should raise ValueError."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            ChunkData(
                id=1,
                text="   \n\t  ",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
            )


class TestChunkDataDocumentPositionValidation:
    """Test suite for document_position field validation."""

    def test_inverted_position_range_raises_error(self):
        """Position range with end < start should raise ValueError."""
        with pytest.raises(ValueError, match="end offset.*must be >= start offset"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=(2000, 1000),
            )

    def test_negative_start_offset_raises_error(self):
        """Negative start offset should raise ValueError."""
        with pytest.raises(ValueError, match="start offset must be non-negative"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=(-100, 1000),
            )

    def test_non_tuple_document_position_raises_error(self):
        """Non-tuple document_position should raise ValueError."""
        with pytest.raises(ValueError, match="document_position must be a tuple"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=[1000, 2000],
            )

    def test_wrong_arity_document_position_raises_error(self):
        """document_position with != 2 elements should raise ValueError."""
        with pytest.raises(ValueError, match="must have exactly 2 elements"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=(1000, 2000, 3000),
            )

    def test_non_integer_position_start_raises_error(self):
        """Non-integer start position element should raise ValueError."""
        with pytest.raises(ValueError, match="start.*must be an integer"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=("1000", 2000),
            )

    def test_non_integer_position_end_raises_error(self):
        """Non-integer end position element should raise ValueError."""
        with pytest.raises(ValueError, match="end.*must be an integer"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                document_position=(1000, 2000.5),
            )


class TestChunkDataExpectedElementsValidation:
    """Test suite for expected_elements field validation."""

    def test_non_list_expected_elements_raises_error(self):
        """Non-list expected_elements should raise ValueError."""
        with pytest.raises(ValueError, match="expected_elements must be a list"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements="not a list",
            )

    def test_non_dict_expected_element_raises_error(self):
        """Non-dict element in expected_elements should raise ValueError."""
        with pytest.raises(ValueError, match="must be a dict"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=["not a dict"],
            )

    def test_missing_type_key_raises_error(self):
        """expected_elements dict without 'type' key should raise ValueError."""
        with pytest.raises(ValueError, match="missing required 'type' key"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=[{"required": True}],
            )

    def test_non_string_type_value_raises_error(self):
        """Non-string 'type' value should raise ValueError."""
        with pytest.raises(ValueError, match=r"\['type'\] must be a string"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=[{"type": 123}],
            )

    def test_non_boolean_required_value_raises_error(self):
        """Non-boolean 'required' value should raise ValueError."""
        with pytest.raises(ValueError, match=r"\['required'\] must be a boolean"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=[{"type": "table", "required": "yes"}],
            )

    def test_non_integer_minimum_value_raises_error(self):
        """Non-integer 'minimum' value should raise ValueError."""
        with pytest.raises(ValueError, match=r"\['minimum'\] must be an integer"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=[{"type": "table", "minimum": 1.5}],
            )

    def test_negative_minimum_value_raises_error(self):
        """Negative 'minimum' value should raise ValueError."""
        with pytest.raises(ValueError, match=r"\['minimum'\] must be non-negative"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=[{"type": "table", "minimum": -1}],
            )


class TestChunkDataMultipleElementValidation:
    """Test validation across multiple expected_elements."""

    def test_multiple_valid_elements(self):
        """Multiple valid expected_elements should all be accepted."""
        chunk = ChunkData(
            id=200,
            text="Complex schema",
            chunk_type="indicator",
            sentences=[],
            tables=[],
            start_pos=0,
            end_pos=15,
            confidence=0.9,
            policy_area_id="PA05",
            dimension_id="DIM05",
            expected_elements=[
                {"type": "table", "required": True, "minimum": 2},
                {"type": "figure", "required": False, "minimum": 0},
                {"type": "citation", "minimum": 1},
                {"type": "formula"},
            ],
        )
        assert len(chunk.expected_elements) == 4

    def test_error_in_second_element_reports_correct_index(self):
        """Error in second element should report index 1."""
        with pytest.raises(ValueError, match=r"expected_elements\[1\]"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA01",
                dimension_id="DIM01",
                expected_elements=[
                    {"type": "valid_type"},
                    {"type": 123},  # Invalid
                ],
            )


class TestChunkDataFieldInteraction:
    """Test interaction between new fields and existing validation."""

    def test_new_fields_with_invalid_chunk_id_still_fails(self):
        """Invalid chunk_id should still fail even with valid new fields."""
        with pytest.raises(ValueError, match="chunk_id"):
            ChunkData(
                id=1,
                text="Valid text",
                chunk_type="diagnostic",
                sentences=[],
                tables=[],
                start_pos=0,
                end_pos=10,
                confidence=0.9,
                policy_area_id="PA99",
                dimension_id="DIM99",
                expected_elements=[{"type": "table"}],
                document_position=(1000, 2000),
            )

    def test_new_fields_preserved_after_chunk_id_derivation(self):
        """New fields should be preserved when chunk_id is derived."""
        chunk = ChunkData(
            id=1,
            text="Valid text",
            chunk_type="diagnostic",
            sentences=[],
            tables=[],
            start_pos=0,
            end_pos=10,
            confidence=0.9,
            policy_area_id="PA01",
            dimension_id="DIM01",
            expected_elements=[{"type": "table"}],
            document_position=(1000, 2000),
        )
        assert chunk.chunk_id == "PA01-DIM01"
        assert len(chunk.expected_elements) == 1
        assert chunk.document_position == (1000, 2000)
