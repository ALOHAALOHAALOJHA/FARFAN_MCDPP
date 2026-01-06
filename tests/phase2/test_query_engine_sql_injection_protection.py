"""
Security tests for SQL injection prevention in Evidence Query Engine.

Tests the SecureQueryParser's ability to detect and reject malicious SQL injection
attempts while allowing legitimate queries.
"""

import pytest

from farfan_pipeline.phases.Phase_two.phase2_80_01_evidence_query_engine import (
    QueryValidationError,
    SecureQueryParser,
    create_query_engine,
)
class TestSQLInjectionProtection:
    """Security tests for SQL injection prevention."""

    @pytest.fixture
    def engine(self):
        """Create query engine with security enabled."""
        nodes = [
            {
                "node_id": "node_001",
                "claim_type": "evidence",
                "content": {"text": "Test content"},
                "source": "test_source",
                "confidence": 0.9,
                "timestamp": "2026-01-06T00:00:00Z",
            },
            {
                "node_id": "node_002",
                "claim_type": "claim",
                "content": {"text": "Another test"},
                "source": "test_source",
                "confidence": 0.7,
                "timestamp": "2026-01-06T01:00:00Z",
            }
        ]
        return create_query_engine(nodes=nodes)

    @pytest.fixture
    def security_parser(self):
        """Create standalone security parser."""
        return SecureQueryParser()

    @pytest.mark.parametrize("malicious_input", [
        "'; DROP TABLE evidence; --",
        "1 OR 1=1",
        "1; DELETE FROM evidence WHERE 1=1",
        "' UNION SELECT * FROM users --",
        "1'; EXEC xp_cmdshell('dir'); --",
        "SELECT * FROM evidence WHERE 1=1--",
        "SELECT * FROM evidence /* comment */ WHERE 1=1",
        "node_id = '1' OR '1'='1",
    ])
    def test_malicious_input_rejected(self, engine, malicious_input):
        """Verify malicious inputs are rejected."""
        with pytest.raises(QueryValidationError) as exc_info:
            engine.query(f"SELECT * FROM evidence WHERE {malicious_input}")

        assert "injection" in str(exc_info.value).lower() or "rejected" in str(exc_info.value).lower()

    @pytest.mark.parametrize("safe_query,expected_count", [
        ("SELECT * FROM evidence WHERE node_id = 'node_001'", 1),
        ("SELECT * FROM evidence WHERE confidence > 0.8", 1),
        ("SELECT * FROM evidence WHERE source = 'test_source'", 2),
        ("SELECT * FROM evidence WHERE timestamp > '2026-01-01'", 2),
    ])
    def test_safe_input_allowed(self, engine, safe_query, expected_count):
        """Verify legitimate queries are processed."""
        result = engine.query(safe_query)
        assert len(result.nodes) == expected_count

    def test_allowlist_enforcement(self, engine):
        """Verify only allowlisted fields are queryable."""
        # Try to query a non-allowlisted field
        with pytest.raises(QueryValidationError) as exc_info:
            engine.query("SELECT * FROM evidence WHERE password = 'secret'")

        assert "not in allowed fields" in str(exc_info.value)

    def test_allowlisted_fields_work(self, engine):
        """Verify all allowlisted fields can be queried."""
        # These should all work without raising exceptions
        allowlisted_queries = [
            "SELECT * FROM evidence WHERE node_id = 'node_001'",
            "SELECT * FROM evidence WHERE source = 'test_source'",
            "SELECT * FROM evidence WHERE confidence > 0.5",
        ]

        for query in allowlisted_queries:
            result = engine.query(query)
            assert isinstance(result.nodes, list)

    def test_query_length_limit(self, engine):
        """Verify queries exceeding maximum length are rejected."""
        # Create a query longer than MAX_QUERY_LENGTH (1000 characters)
        long_query = "SELECT * FROM evidence WHERE " + " AND ".join(
            [f"field_{i} = 'value_{i}'" for i in range(100)]
        )

        with pytest.raises(QueryValidationError) as exc_info:
            engine.query(long_query)

        assert "maximum length" in str(exc_info.value).lower()

    def test_injection_pattern_detection_drop(self, security_parser):
        """Verify DROP TABLE pattern is detected."""
        malicious = "SELECT * FROM evidence; DROP TABLE evidence"

        with pytest.raises(QueryValidationError):
            security_parser.validate_query(malicious)

    def test_injection_pattern_detection_union(self, security_parser):
        """Verify UNION SELECT pattern is detected."""
        malicious = "SELECT * FROM evidence UNION SELECT * FROM users"

        with pytest.raises(QueryValidationError):
            security_parser.validate_query(malicious)

    def test_injection_pattern_detection_comment(self, security_parser):
        """Verify SQL comment patterns are detected."""
        malicious = "SELECT * FROM evidence WHERE id = 1 --"

        with pytest.raises(QueryValidationError):
            security_parser.validate_query(malicious)

    def test_field_validation(self, security_parser):
        """Verify field validation against allowlist."""
        # Allowed field should pass
        security_parser.validate_field("node_id")
        security_parser.validate_field("source")
        security_parser.validate_field("confidence")

        # Disallowed field should fail
        with pytest.raises(QueryValidationError):
            security_parser.validate_field("password")

        with pytest.raises(QueryValidationError):
            security_parser.validate_field("admin_token")

    def test_security_can_be_disabled(self):
        """Verify security can be disabled for testing."""
        nodes = [
            {
                "node_id": "test",
                "claim_type": "test",
                "content": {},
                "source": "test",
                "confidence": 0.5,
                "timestamp": "2026-01-06T00:00:00Z",
            }
        ]
        engine = create_query_engine(nodes=nodes)

        # Manually disable security
        engine.enable_security = False

        # Query a non-allowlisted field or an injection - would be rejected with security on
        # but should pass when security is disabled (if the field exists or is ignored)
        # We use a non-allowlisted field like 'password'
        result = engine.query("SELECT * FROM evidence WHERE password = 'secret'")
        assert isinstance(result.nodes, list)

    def test_legitimate_complex_query(self, engine):
        """Verify complex but legitimate queries work."""
        complex_query = (
            "SELECT * FROM evidence "
            "WHERE confidence > 0.5 "
            "AND source = 'test_source' "
            "ORDER BY timestamp DESC "
            "LIMIT 10"
        )

        result = engine.query(complex_query)
        assert isinstance(result.nodes, list)

    def test_security_logging(self, engine, caplog):
        """Verify rejected queries are logged."""
        import logging
        caplog.set_level(logging.WARNING)

        malicious_query = "SELECT * FROM evidence; DROP TABLE evidence"

        with pytest.raises(QueryValidationError):
            engine.query(malicious_query)

        # Verify warning was logged
        assert any("rejected" in record.message.lower() for record in caplog.records)

    def test_or_injection_pattern(self, security_parser):
        """Verify OR 1=1 injection pattern is detected."""
        patterns = [
            "' OR '1'='1",
            "' OR 1=1",
            "1 OR 1=1",
        ]

        for pattern in patterns:
            with pytest.raises(QueryValidationError):
                security_parser.validate_query(pattern)

    def test_xp_cmdshell_detection(self, security_parser):
        """Verify xp_cmdshell pattern is detected."""
        malicious = "'; EXEC xp_cmdshell('rm -rf /')"

        with pytest.raises(QueryValidationError):
            security_parser.validate_query(malicious)

    def test_outfile_injection_detection(self, security_parser):
        """Verify INTO OUTFILE pattern is detected."""
        malicious = "SELECT * INTO OUTFILE '/etc/passwd'"

        with pytest.raises(QueryValidationError):
            security_parser.validate_query(malicious)
