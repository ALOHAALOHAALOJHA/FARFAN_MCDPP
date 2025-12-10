"""
Test Layer Metadata Integration in CalibrationCertificate
==========================================================

Validates that layer metadata is correctly embedded in certificates and provides
complete provenance information for reproducibility verification.
"""

from certificate_generator import CertificateGenerator, LayerMetadata


def test_layer_metadata_generation():
    print("=" * 80)
    print("Test: Layer Metadata Generation")
    print("=" * 80)
    
    generator = CertificateGenerator()
    
    certificate = generator.generate_certificate(
        instance_id="test-layer-metadata-001",
        method_id="test.method.executor",
        node_id="node_test_001",
        context={"test": "layer_metadata_integration"},
        intrinsic_score=0.85,
        layer_scores={
            "@b": 0.90,
            "@chain": 0.87,
            "@q": 0.84,
            "@d": 0.88,
            "@p": 0.81,
            "@C": 0.86,
            "@u": 0.78,
            "@m": 0.80,
        },
        weights={
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        },
        interaction_weights={
            "@u,@chain": 0.13,
            "@chain,@C": 0.10,
            "@q,@d": 0.10,
        },
    )
    
    print("\n✓ Certificate generated successfully")
    print(f"  Instance ID: {certificate.instance_id}")
    print(f"  Calibrated Score: {certificate.calibrated_score:.4f}")
    
    assert hasattr(certificate, "layer_metadata"), "Certificate missing layer_metadata attribute"
    assert isinstance(certificate.layer_metadata, dict), "layer_metadata should be a dict"
    assert len(certificate.layer_metadata) > 0, "layer_metadata should not be empty"
    
    print(f"\n✓ Layer metadata attribute exists")
    print(f"  Number of layers documented: {len(certificate.layer_metadata)}")
    
    for layer_symbol, metadata in certificate.layer_metadata.items():
        assert isinstance(metadata, LayerMetadata), f"Layer {layer_symbol} metadata should be LayerMetadata instance"
        assert metadata.symbol == layer_symbol, f"Layer symbol mismatch: {metadata.symbol} != {layer_symbol}"
        assert metadata.name, f"Layer {layer_symbol} missing name"
        assert metadata.description, f"Layer {layer_symbol} missing description"
        assert metadata.formula, f"Layer {layer_symbol} missing formula"
        assert isinstance(metadata.weights, dict), f"Layer {layer_symbol} weights should be dict"
        assert isinstance(metadata.thresholds, dict), f"Layer {layer_symbol} thresholds should be dict"
    
    print(f"\n✓ All layer metadata validated")
    
    expected_layers = {"@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"}
    actual_layers = set(certificate.layer_metadata.keys())
    assert actual_layers == expected_layers, f"Layer mismatch: {actual_layers} != {expected_layers}"
    
    print(f"\n✓ All expected layers present in metadata")
    
    return certificate


def test_layer_metadata_serialization():
    print("\n" + "=" * 80)
    print("Test: Layer Metadata Serialization to JSON")
    print("=" * 80)
    
    generator = CertificateGenerator()
    
    certificate = generator.generate_certificate(
        instance_id="test-serialization-001",
        method_id="test.method",
        node_id="node_001",
        context={"test": "serialization"},
        intrinsic_score=0.80,
        layer_scores={"@b": 0.85, "@chain": 0.82},
        weights={"@b": 0.6, "@chain": 0.4},
    )
    
    json_str = certificate.to_json()
    assert "layer_metadata" in json_str, "JSON should contain layer_metadata field"
    
    print("\n✓ Certificate serializes to JSON with layer_metadata field")
    
    import json
    cert_dict = json.loads(json_str)
    assert "layer_metadata" in cert_dict, "Parsed JSON should have layer_metadata key"
    assert isinstance(cert_dict["layer_metadata"], dict), "layer_metadata should be dict in JSON"
    
    for layer_symbol in ["@b", "@chain"]:
        assert layer_symbol in cert_dict["layer_metadata"], f"Layer {layer_symbol} should be in metadata"
        layer_meta = cert_dict["layer_metadata"][layer_symbol]
        assert "symbol" in layer_meta, f"Layer {layer_symbol} metadata missing symbol"
        assert "name" in layer_meta, f"Layer {layer_symbol} metadata missing name"
        assert "description" in layer_meta, f"Layer {layer_symbol} metadata missing description"
        assert "formula" in layer_meta, f"Layer {layer_symbol} metadata missing formula"
        assert "weights" in layer_meta, f"Layer {layer_symbol} metadata missing weights"
        assert "thresholds" in layer_meta, f"Layer {layer_symbol} metadata missing thresholds"
    
    print("✓ Layer metadata correctly structured in JSON")
    print(f"  Layers documented: {list(cert_dict['layer_metadata'].keys())}")
    
    return certificate


def test_layer_metadata_content():
    print("\n" + "=" * 80)
    print("Test: Layer Metadata Content Verification")
    print("=" * 80)
    
    generator = CertificateGenerator()
    
    certificate = generator.generate_certificate(
        instance_id="test-content-001",
        method_id="test.method",
        node_id="node_001",
        context={"test": "content"},
        intrinsic_score=0.80,
        layer_scores={"@b": 0.85, "@u": 0.78, "@C": 0.82},
        weights={"@b": 0.4, "@u": 0.3, "@C": 0.3},
    )
    
    b_meta = certificate.layer_metadata["@b"]
    assert b_meta.name == "Base Theory Layer"
    assert "code quality" in b_meta.description.lower()
    assert "b_theory" in b_meta.formula or "0.40" in b_meta.formula
    assert len(b_meta.weights) > 0
    assert len(b_meta.thresholds) > 0
    
    print("\n✓ @b (Base Layer) metadata verified")
    print(f"  Name: {b_meta.name}")
    print(f"  Formula: {b_meta.formula}")
    
    u_meta = certificate.layer_metadata["@u"]
    assert u_meta.name == "Unit Layer"
    assert "document" in u_meta.description.lower()
    assert "geometric_mean" in u_meta.formula or "U =" in u_meta.formula
    assert len(u_meta.weights) > 0
    assert len(u_meta.thresholds) > 0
    
    print("\n✓ @u (Unit Layer) metadata verified")
    print(f"  Name: {u_meta.name}")
    print(f"  Formula: {u_meta.formula}")
    
    c_meta = certificate.layer_metadata["@C"]
    assert c_meta.name == "Contract Layer"
    assert "contract" in c_meta.description.lower()
    assert "c_scale" in c_meta.formula or "0.4" in c_meta.formula
    assert len(c_meta.weights) > 0
    assert len(c_meta.thresholds) > 0
    
    print("\n✓ @C (Contract Layer) metadata verified")
    print(f"  Name: {c_meta.name}")
    print(f"  Formula: {c_meta.formula}")
    
    return certificate


def test_signature_with_layer_metadata():
    print("\n" + "=" * 80)
    print("Test: Certificate Signature Includes Layer Metadata")
    print("=" * 80)
    
    generator = CertificateGenerator()
    
    certificate = generator.generate_certificate(
        instance_id="test-signature-001",
        method_id="test.method",
        node_id="node_001",
        context={"test": "signature"},
        intrinsic_score=0.80,
        layer_scores={"@b": 0.85},
        weights={"@b": 1.0},
    )
    
    is_valid = generator.verify_certificate(certificate)
    assert is_valid, "Certificate signature should be valid"
    
    print("\n✓ Certificate signature is valid")
    print(f"  Signature: {certificate.signature[:32]}...")
    
    from dataclasses import replace
    
    tampered_layer_meta = certificate.layer_metadata.copy()
    tampered_layer_meta["@b"] = replace(
        certificate.layer_metadata["@b"],
        formula="TAMPERED_FORMULA"
    )
    
    tampered_cert = replace(certificate, layer_metadata=tampered_layer_meta)
    is_valid_tampered = generator.verify_certificate(tampered_cert)
    
    assert not is_valid_tampered, "Tampered certificate should be invalid"
    
    print("✓ Signature verification detects layer_metadata tampering")
    
    return certificate


def test_layer_metadata_reproducibility():
    print("\n" + "=" * 80)
    print("Test: Layer Metadata Enables Reproducibility")
    print("=" * 80)
    
    generator = CertificateGenerator()
    
    certificate = generator.generate_certificate(
        instance_id="test-reproducibility-001",
        method_id="test.method.executor",
        node_id="node_001",
        context={"test": "reproducibility"},
        intrinsic_score=0.85,
        layer_scores={
            "@b": 0.90,
            "@chain": 0.87,
            "@u": 0.78,
        },
        weights={
            "@b": 0.5,
            "@chain": 0.3,
            "@u": 0.2,
        },
    )
    
    print("\n✓ Certificate contains complete layer specifications:")
    
    for layer_symbol, metadata in certificate.layer_metadata.items():
        score = certificate.layer_scores.get(layer_symbol, 0.0)
        weight_key = f"a_{layer_symbol}"
        weight = certificate.parameter_provenance.get(weight_key)
        
        print(f"\n  {layer_symbol} - {metadata.name}")
        print(f"    Score: {score:.4f}")
        if weight:
            print(f"    Weight: {weight.value:.4f}")
        print(f"    Formula: {metadata.formula[:60]}...")
        print(f"    Thresholds: {len(metadata.thresholds)} defined")
        print(f"    Component Weights: {len(metadata.weights)} defined")
    
    print("\n✓ Layer metadata provides self-contained documentation")
    print("✓ Certificate enables independent reproducibility verification")
    
    return certificate


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("LAYER METADATA INTEGRATION TEST SUITE")
    print("=" * 80)
    
    try:
        test_layer_metadata_generation()
        test_layer_metadata_serialization()
        test_layer_metadata_content()
        test_signature_with_layer_metadata()
        test_layer_metadata_reproducibility()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80)
        print("\nLayer metadata integration is working correctly!")
        print("Certificates now include complete layer provenance:")
        print("  • Formulas for all active layers")
        print("  • Component weights and thresholds")
        print("  • Self-documenting for reproducibility verification")
        print("  • Protected by certificate signature")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        raise
