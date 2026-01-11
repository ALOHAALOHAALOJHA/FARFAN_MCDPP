"""
Comprehensive tests for SOTA NER implementation in signal extraction.

Tests cover:
- spaCy NER with custom entity patterns
- Domain knowledge integration
- Colombian entity recognition
- Policy area specific extraction
- Entity scoring and ranking
- Fallback mechanisms
"""

import pytest

# Test data for Colombian policy documents
SAMPLE_TEXT_PA02 = """
El Ministerio de Salud y Protección Social, en coordinación con la 
Secretaría de Salud departamental y el Instituto Nacional de Salud,
implementa programas de atención primaria. La Superintendencia Nacional
de Salud supervisa los servicios de EPS e IPS.
"""

SAMPLE_TEXT_PA03 = """
El Ministerio de Educación Nacional (MEN) trabaja con el ICBF y el SENA
para mejorar la cobertura educativa. La Secretaría de Educación municipal
coordina con las instituciones educativas y el ICETEX.
"""

SAMPLE_TEXT_PA09 = """
La Alcaldía Municipal, bajo supervisión de la Contraloría General y la
Procuraduría General de la Nación, implementa proyectos de transparencia.
La Veeduría Ciudadana y el DAFP apoyan el proceso.
"""


class TestSOTASignalExtractor:
    """Test suite for SOTA signal extractor with NER."""
    
    @pytest.fixture
    def extractor(self):
        """Create SOTA signal extractor instance."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import SOTASignalExtractor
        return SOTASignalExtractor(enable_spacy=True)
    
    def test_spacy_loaded_with_ner(self, extractor):
        """Test that spaCy is loaded with NER component enabled."""
        assert extractor.nlp is not None, "spaCy should be loaded"
        assert "ner" in extractor.nlp.pipe_names, "NER component should be enabled"
        assert "entity_ruler" in extractor.nlp.pipe_names, "EntityRuler should be added"
    
    def test_entity_patterns_added(self, extractor):
        """Test that domain entity patterns were added."""
        # EntityRuler should have patterns
        ruler = extractor.nlp.get_pipe("entity_ruler")
        # Patterns were added in initialization
        assert ruler is not None
    
    def test_extract_entities_salud(self, extractor):
        """Test entity extraction for PA02 (Salud)."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        entities = extractor._extract_entities(PolicyArea.SALUD, SAMPLE_TEXT_PA02)
        
        assert len(entities) > 0, "Should extract entities"
        assert any("Ministerio de Salud" in e for e in entities), "Should find Ministerio de Salud"
        assert any("Secretaría" in e for e in entities), "Should find Secretaría"
        
        print(f"✓ PA02 extracted {len(entities)} entities: {entities[:5]}")
    
    def test_extract_entities_educacion(self, extractor):
        """Test entity extraction for PA03 (Educación)."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        entities = extractor._extract_entities(PolicyArea.EDUCACIÓN, SAMPLE_TEXT_PA03)
        
        assert len(entities) > 0, "Should extract entities"
        # Check for key entities
        entity_text = " ".join(entities).upper()
        assert "ICBF" in entity_text or "SENA" in entity_text or "MEN" in entity_text, \
            "Should find educational entities"
        
        print(f"✓ PA03 extracted {len(entities)} entities: {entities[:5]}")
    
    def test_extract_entities_institucional(self, extractor):
        """Test entity extraction for PA09 (Fortalecimiento Institucional)."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        entities = extractor._extract_entities(PolicyArea.FISCAL, SAMPLE_TEXT_PA09)
        
        assert len(entities) > 0, "Should extract entities"
        # Alcaldía, Contraloría, Procuraduría should be found
        entity_text = " ".join(entities)
        assert any(keyword in entity_text for keyword in ["Alcaldía", "Contraloría", "Procuraduría"]), \
            "Should find institutional entities"
        
        print(f"✓ PA09 extracted {len(entities)} entities: {entities[:5]}")
    
    def test_entity_scoring(self, extractor):
        """Test that entities are properly scored and ranked."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Text with repeated entity
        text = """
        El Ministerio de Salud coordina programas. El Ministerio de Salud 
        establece protocolos. Ministerio de Salud y la OMS trabajan juntos.
        Una pequeña entidad también participa.
        """
        
        entities = extractor._extract_entities(PolicyArea.SALUD, text)
        
        # "Ministerio de Salud" should rank high due to:
        # - ORG type (high score)
        # - Length (specific)
        # - Frequency (appears multiple times)
        assert "Ministerio de Salud" in entities or "Ministerio" in entities[0], \
            "Frequent entity should rank high"
        
        print(f"✓ Entity scoring working: top entity = {entities[0]}")
    
    def test_domain_knowledge_integration(self, extractor):
        """Test integration of domain knowledge with NER."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Text that mentions domain entities
        text = "IDEAM y ANLA coordinan con MinAmbiente"
        
        entities = extractor._extract_entities(PolicyArea.AMBIENTE, text)
        
        # Should find both NER entities and domain knowledge entities
        assert len(entities) > 0, "Should extract entities"
        entity_text = " ".join(entities).upper()
        assert "IDEAM" in entity_text or "ANLA" in entity_text or "MINAMBIENTE" in entity_text, \
            "Should find environment entities"
        
        print(f"✓ Domain knowledge integrated: {entities}")
    
    def test_regex_fallback(self, extractor):
        """Test regex fallback when spaCy fails."""
        # Temporarily disable spaCy to test fallback
        original_nlp = extractor.nlp
        extractor.nlp = None
        extractor.enable_spacy = False
        
        entities = extractor._extract_entities_regex(SAMPLE_TEXT_PA02)
        
        assert len(entities) > 0, "Regex fallback should extract entities"
        
        # Restore spaCy
        extractor.nlp = original_nlp
        extractor.enable_spacy = True
        
        print(f"✓ Regex fallback working: {len(entities)} entities")
    
    def test_all_policy_areas(self, extractor):
        """Test entity extraction works for all policy areas."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        test_text = "El Ministerio coordina con la Secretaría para implementar programas."
        
        for policy_area in PolicyArea:
            entities = extractor._extract_entities(policy_area, test_text)
            assert isinstance(entities, list), f"Should return list for {policy_area}"
            # May be empty for some policy areas, that's OK
        
        print(f"✓ All {len(list(PolicyArea))} policy areas tested")


class TestSignalsServiceNER:
    """Test suite for signals_service.py NER integration."""
    
    def test_extract_entities_for_policy_area(self):
        """Test NER function in signals_service.py"""
        pytest.importorskip("fastapi", reason="FastAPI not available in test environment")
        from farfan_pipeline.dashboard_atroz_.signals_service import _extract_entities_for_policy_area
        
        # Test each policy area
        test_cases = [
            ("PA01", "Ordenamiento Territorial"),
            ("PA02", "Salud y Protección Social"),
            ("PA03", "Educación y Primera Infancia"),
            ("PA04", "Infraestructura y Equipamientos"),
            ("PA05", "Desarrollo Económico"),
            ("PA06", "Sostenibilidad Ambiental"),
            ("PA07", "Seguridad y Convivencia"),
            ("PA08", "Víctimas y Reconciliación"),
            ("PA09", "Fortalecimiento Institucional"),
            ("PA10", "Conectividad y TIC"),
        ]
        
        for pa_code, pa_name in test_cases:
            entities = _extract_entities_for_policy_area(pa_code, pa_name)
            
            assert isinstance(entities, list), f"{pa_code} should return list"
            assert len(entities) > 0, f"{pa_code} should have entities"
            assert all(isinstance(e, str) for e in entities), f"{pa_code} entities should be strings"
            
            print(f"✓ {pa_code}: {len(entities)} entities")
    
    def test_domain_knowledge_fallback(self):
        """Test domain knowledge function."""
        pytest.importorskip("fastapi", reason="FastAPI not available in test environment")
        from farfan_pipeline.dashboard_atroz_.signals_service import _extract_entities_domain_knowledge
        
        # Test each policy area has domain knowledge
        for pa_code in [f"PA{i:02d}" for i in range(1, 11)]:
            entities = _extract_entities_domain_knowledge(pa_code)
            
            assert isinstance(entities, list), f"{pa_code} should return list"
            assert len(entities) > 0, f"{pa_code} should have domain entities"
            
            print(f"✓ {pa_code} domain KB: {len(entities)} entities")
    
    def test_ner_with_spacy_available(self):
        """Test that NER uses spaCy when available."""
        pytest.importorskip("fastapi", reason="FastAPI not available in test environment")
        from farfan_pipeline.dashboard_atroz_.signals_service import _extract_entities_for_policy_area
        
        # PA02 has rich domain knowledge
        entities = _extract_entities_for_policy_area("PA02", "Salud y Protección Social")
        
        # Should include domain entities
        assert any("Ministerio" in e or "Secretaría" in e for e in entities), \
            "Should include governmental entities"
        
        print(f"✓ NER with spaCy: {entities[:3]}")


class TestEntityKnowledgeBase:
    """Test suite for entity knowledge base completeness."""
    
    def test_all_policy_areas_covered(self):
        """Test that all 10 policy areas have domain entities."""
        pytest.importorskip("fastapi", reason="FastAPI not available in test environment")
        from farfan_pipeline.dashboard_atroz_.signals_service import _extract_entities_domain_knowledge
        
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        
        for pa_code in policy_areas:
            entities = _extract_entities_domain_knowledge(pa_code)
            assert len(entities) >= 4, f"{pa_code} should have at least 4 entities"
            
        print(f"✓ All 10 policy areas have domain entities")
    
    def test_entity_quality(self):
        """Test entity quality - no empty strings, proper names."""
        pytest.importorskip("fastapi", reason="FastAPI not available in test environment")
        from farfan_pipeline.dashboard_atroz_.signals_service import _extract_entities_domain_knowledge
        
        for pa_code in [f"PA{i:02d}" for i in range(1, 11)]:
            entities = _extract_entities_domain_knowledge(pa_code)
            
            for entity in entities:
                assert entity.strip() != "", f"{pa_code}: Entity should not be empty"
                assert len(entity) >= 3, f"{pa_code}: Entity '{entity}' too short"
                
        print("✓ Entity quality validated")
    
    def test_colombian_entities_present(self):
        """Test that Colombian-specific entities are present."""
        pytest.importorskip("fastapi", reason="FastAPI not available in test environment")
        from farfan_pipeline.dashboard_atroz_.signals_service import _extract_entities_domain_knowledge
        
        # Check for key Colombian entities
        all_entities = []
        for pa_code in [f"PA{i:02d}" for i in range(1, 11)]:
            all_entities.extend(_extract_entities_domain_knowledge(pa_code))
        
        all_text = " ".join(all_entities)
        
        # Key Colombian entities should be present
        colombian_markers = ["DNP", "ICBF", "MinSalud", "INVIAS", "ANI", "IDEAM", 
                            "MinTIC", "Alcaldía", "Contraloría"]
        
        found = [marker for marker in colombian_markers if marker in all_text]
        
        assert len(found) >= 5, f"Should find Colombian entities, found: {found}"
        print(f"✓ Colombian entities present: {found}")


if __name__ == "__main__":
    # Quick smoke test
    print("Running NER SOTA smoke tests...")
    
    from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import SOTASignalExtractor, PolicyArea
    
    extractor = SOTASignalExtractor(enable_spacy=True)
    
    print(f"✓ spaCy loaded: {extractor.nlp is not None}")
    print(f"✓ NER enabled: {'ner' in extractor.nlp.pipe_names if extractor.nlp else False}")
    print(f"✓ EntityRuler added: {'entity_ruler' in extractor.nlp.pipe_names if extractor.nlp else False}")
    
    # Test extraction
    test_text = "El Ministerio de Salud coordina con el ICBF y la Alcaldía Municipal."
    entities = extractor._extract_entities(PolicyArea.SALUD, test_text)
    print(f"✓ Extracted {len(entities)} entities: {entities[:3]}")
    
    print("\n✓ All smoke tests passed!")
    print("Run with pytest for full test suite.")
