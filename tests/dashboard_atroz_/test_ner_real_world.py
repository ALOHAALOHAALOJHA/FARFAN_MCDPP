"""
Real-world validation tests for SOTA NER implementation.

Tests the NER system with actual Colombian municipal policy document samples
to validate production readiness and accuracy.
"""

import pytest

# Real Colombian municipal policy document samples
REAL_WORLD_SAMPLES = {
    "PA01_ordenamiento": """
    El Departamento Nacional de Planeación (DNP), en coordinación con el Instituto 
    Geográfico Agustín Codazzi (IGAC) y la Secretaría de Planeación Municipal, 
    ha elaborado el nuevo Plan de Ordenamiento Territorial (POT). El Concejo Municipal 
    aprobó mediante Acuerdo 015 de 2024 la actualización. La Curaduría Urbana número 1 
    será responsable de la implementación.
    """,
    
    "PA02_salud": """
    El Ministerio de Salud y Protección Social, a través de la Superintendencia Nacional 
    de Salud (Supersalud), implementará el programa de atención primaria. El Instituto 
    Nacional de Salud (INS) coordinará con las Secretarías de Salud departamentales y 
    las EPS e IPS locales. Los Hospitales Locales y Centros de Salud deberán reportar 
    mensualmente al SISPRO.
    """,
    
    "PA03_educacion": """
    El Ministerio de Educación Nacional (MEN) y el Instituto Colombiano de Bienestar 
    Familiar (ICBF) lanzan programa conjunto de primera infancia. La Secretaría de 
    Educación municipal coordina con instituciones educativas oficiales. El SENA y el 
    ICETEX apoyan con formación técnica y financiación estudiantil respectivamente.
    """,
    
    "PA04_infraestructura": """
    El Instituto Nacional de Vías (INVIAS) y la Agencia Nacional de Infraestructura (ANI) 
    ejecutarán obras de mejoramiento vial. FINDETER financiará el proyecto de acueducto 
    municipal. El Ministerio de Transporte supervisa y el Ministerio de Vivienda, Ciudad 
    y Territorio coordina con la Empresa de Servicios Públicos (ESP) local.
    """,
    
    "PA05_desarrollo": """
    El Ministerio de Comercio, Industria y Turismo, junto con la Cámara de Comercio y 
    BANCOLDEX, promueven el emprendimiento regional. El Banco Agrario y FINAGRO apoyan 
    el sector rural. El SENA ofrece capacitación técnica. La DIAN facilita trámites 
    tributarios para nuevas empresas.
    """,
    
    "PA06_ambiente": """
    El Ministerio de Ambiente y Desarrollo Sostenible, las Corporaciones Autónomas 
    Regionales (CAR), el IDEAM y la Autoridad Nacional de Licencias Ambientales (ANLA) 
    coordinan la política ambiental. Parques Nacionales Naturales de Colombia protege 
    las áreas del Sistema de Parques. El Instituto Humboldt apoya con investigación.
    """,
    
    "PA07_seguridad": """
    El Ministerio del Interior y el Ministerio de Defensa Nacional coordinan con la 
    Policía Nacional el plan de seguridad. La Fiscalía General de la Nación investiga 
    casos prioritarios. La Defensoría del Pueblo y la Personería Municipal velan por 
    derechos humanos. Las Comisarías de Familia atienden violencia intrafamiliar.
    """,
    
    "PA08_victimas": """
    La Unidad para la Atención y Reparación Integral a las Víctimas (UARIV) implementa 
    programas de reparación. El Centro Nacional de Memoria Histórica documenta el 
    conflicto. La Jurisdicción Especial para la Paz (JEP) adelanta procesos judiciales. 
    La Comisión de la Verdad y la Unidad de Búsqueda de Personas Desaparecidas (UBPD) 
    trabajan en esclarecimiento.
    """,
    
    "PA09_institucional": """
    La Alcaldía Municipal, bajo supervisión de la Contraloría General de la República 
    y la Procuraduría General de la Nación, ejecuta el plan de transparencia. El 
    Departamento Administrativo de la Función Pública (DAFP) apoya modernización. 
    La Escuela Superior de Administración Pública (ESAP) capacita funcionarios. 
    Las Veedurías Ciudadanas monitorean gestión pública.
    """,
    
    "PA10_tic": """
    El Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC) 
    implementa estrategia de Gobierno Digital. La Agencia Nacional del Espectro (ANE) 
    gestiona frecuencias. La Comisión de Regulación de Comunicaciones (CRC) regula 
    el sector. Los Puntos Vive Digital ofrecen acceso a tecnología. La Secretaría TIC 
    municipal coordina localmente.
    """
}


class TestRealWorldNER:
    """Validation with real Colombian municipal documents."""
    
    @pytest.fixture
    def extractor(self):
        """Create SOTA signal extractor."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import SOTASignalExtractor
        return SOTASignalExtractor(enable_spacy=True)
    
    def test_pa01_ordenamiento_extraction(self, extractor):
        """Test entity extraction from real PA01 document."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = REAL_WORLD_SAMPLES["PA01_ordenamiento"]
        entities = extractor._extract_entities(PolicyArea.FISCAL, text)
        
        # Expected key entities
        expected = ["DNP", "IGAC", "Planeación", "Concejo Municipal", "Curaduría"]
        found = [exp for exp in expected if any(exp in ent for ent in entities)]
        
        assert len(found) >= 2, f"Should find key PA01 entities, found: {found}"
        print(f"✓ PA01 Real World: {len(entities)} entities, including {found}")
    
    def test_pa02_salud_extraction(self, extractor):
        """Test entity extraction from real PA02 document."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = REAL_WORLD_SAMPLES["PA02_salud"]
        entities = extractor._extract_entities(PolicyArea.SALUD, text)
        
        # Expected key entities
        expected = ["Ministerio de Salud", "Supersalud", "INS", "Secretarías de Salud"]
        found = [exp for exp in expected if any(exp in ent for ent in entities)]
        
        assert len(found) >= 2, f"Should find key PA02 entities, found: {found}"
        print(f"✓ PA02 Real World: {len(entities)} entities, including {found}")
    
    def test_pa03_educacion_extraction(self, extractor):
        """Test entity extraction from real PA03 document."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = REAL_WORLD_SAMPLES["PA03_educacion"]
        entities = extractor._extract_entities(PolicyArea.EDUCACIÓN, text)
        
        # Expected key entities
        expected = ["MEN", "ICBF", "Educación", "SENA", "ICETEX"]
        found = [exp for exp in expected if any(exp in ent for ent in entities)]
        
        assert len(found) >= 2, f"Should find key PA03 entities, found: {found}"
        print(f"✓ PA03 Real World: {len(entities)} entities, including {found}")
    
    def test_pa06_ambiente_extraction(self, extractor):
        """Test entity extraction from real PA06 document."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = REAL_WORLD_SAMPLES["PA06_ambiente"]
        entities = extractor._extract_entities(PolicyArea.AMBIENTE, text)
        
        # Expected key entities
        expected = ["Ministerio de Ambiente", "CAR", "IDEAM", "ANLA", "Parques Nacionales"]
        found = [exp for exp in expected if any(exp in ent for ent in entities)]
        
        assert len(found) >= 2, f"Should find key PA06 entities, found: {found}"
        print(f"✓ PA06 Real World: {len(entities)} entities, including {found}")
    
    def test_pa08_victimas_extraction(self, extractor):
        """Test entity extraction from real PA08 document."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = REAL_WORLD_SAMPLES["PA08_victimas"]
        entities = extractor._extract_entities(PolicyArea.FISCAL, text)
        
        # Expected key entities (specialized peace process entities)
        expected = ["UARIV", "Memoria Histórica", "JEP", "Comisión", "UBPD"]
        found = [exp for exp in expected if any(exp in ent for ent in entities)]
        
        assert len(found) >= 1, f"Should find key PA08 entities, found: {found}"
        print(f"✓ PA08 Real World: {len(entities)} entities, including {found}")
    
    def test_entity_precision_across_samples(self, extractor):
        """Test precision: extracted entities should be real organizations."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Combine all samples
        all_text = " ".join(REAL_WORLD_SAMPLES.values())
        entities = extractor._extract_entities(PolicyArea.FISCAL, all_text)
        
        # Check that entities are not generic words
        generic_words = ["el", "la", "los", "de", "y", "para", "con", "en"]
        invalid = [e for e in entities if e.lower() in generic_words]
        
        assert len(invalid) == 0, f"Should not extract generic words: {invalid}"
        
        # Check minimum entity length (real organizations are longer)
        short_entities = [e for e in entities if len(e) < 3]
        assert len(short_entities) / len(entities) < 0.1, "Most entities should be meaningful"
        
        print(f"✓ Precision check: {len(entities)} entities, 0 generic words")
    
    def test_entity_recall_comprehensive(self, extractor):
        """Test recall: should find key Colombian entities across documents."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Test individual samples for better recall
        key_tests = {
            "PA02_salud": (["Ministerio de Salud", "Supersalud", "INS"], PolicyArea.SALUD),
            "PA03_educacion": (["ICBF", "SENA"], PolicyArea.EDUCACIÓN),
            "PA06_ambiente": (["IDEAM", "ANLA"], PolicyArea.AMBIENTE),
        }
        
        total_found = 0
        total_expected = 0
        
        for sample_key, (expected_entities, policy_area) in key_tests.items():
            text = REAL_WORLD_SAMPLES[sample_key]
            entities = extractor._extract_entities(policy_area, text)
            entities_text = " ".join(entities).upper()
            
            found = [e for e in expected_entities if any(e.upper() in ent.upper() for ent in entities)]
            total_found += len(found)
            total_expected += len(expected_entities)
        
        recall = total_found / total_expected if total_expected > 0 else 0
        # Should find at least 50% across targeted samples
        assert recall >= 0.5, f"Should find key entities. Found {total_found}/{total_expected} ({recall:.1%})"
        
        print(f"✓ Recall: {total_found}/{total_expected} key entities found ({recall:.1%})")
    
    def test_colombian_specific_entities(self, extractor):
        """Test that Colombian-specific entities are recognized."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Test each sample
        colombian_markers = {
            "PA01_ordenamiento": ["IGAC", "DNP", "POT"],
            "PA02_salud": ["Supersalud", "INS", "SISPRO"],
            "PA03_educacion": ["ICBF", "ICETEX"],
            "PA08_victimas": ["UARIV", "JEP", "UBPD"],
        }
        
        for sample_key, markers in colombian_markers.items():
            text = REAL_WORLD_SAMPLES[sample_key]
            entities = extractor._extract_entities(PolicyArea.FISCAL, text)
            entities_text = " ".join(entities).upper()
            
            found = [m for m in markers if m.upper() in entities_text]
            assert len(found) >= 1, f"{sample_key}: Should find Colombian markers, got {found}"
        
        print("✓ Colombian-specific entities recognized across all samples")
    
    def test_entity_ranking_quality(self, extractor):
        """Test that important entities rank higher."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Text with clear entity hierarchy
        text = REAL_WORLD_SAMPLES["PA02_salud"]
        entities = extractor._extract_entities(PolicyArea.SALUD, text)
        
        # "Ministerio de Salud" should rank very high (appears early, important)
        top_5 = entities[:5]
        has_ministry = any("Ministerio" in e or "Salud" in e for e in top_5)
        
        assert has_ministry, f"Important ministry should be in top 5: {top_5}"
        print(f"✓ Entity ranking quality validated. Top 5: {top_5}")


class TestEdgeCases:
    """Test edge cases and robustness."""
    
    @pytest.fixture
    def extractor(self):
        """Create SOTA signal extractor."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import SOTASignalExtractor
        return SOTASignalExtractor(enable_spacy=True)
    
    def test_empty_text(self, extractor):
        """Test extraction from empty text."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        entities = extractor._extract_entities(PolicyArea.FISCAL, "")
        assert isinstance(entities, list), "Should return empty list for empty text"
        assert len(entities) == 0, "Should not extract from empty text"
    
    def test_very_long_text(self, extractor):
        """Test extraction from very long text."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        # Repeat sample text to create long document
        long_text = REAL_WORLD_SAMPLES["PA02_salud"] * 100
        entities = extractor._extract_entities(PolicyArea.SALUD, long_text)
        
        assert isinstance(entities, list), "Should handle long text"
        assert len(entities) > 0, "Should extract from long text"
        # Should not return hundreds of duplicates
        assert len(entities) <= 50, "Should deduplicate entities"
    
    def test_text_with_special_characters(self, extractor):
        """Test extraction with special characters."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = """
        El Ministerio de Salud & la Secretaría (SDS) coordinan con el I.C.B.F.
        También participan: EPS/IPS, Hospital Local #1, Centro de Salud - Rural.
        """
        
        entities = extractor._extract_entities(PolicyArea.SALUD, text)
        assert len(entities) > 0, "Should handle special characters"
    
    def test_mixed_case_entities(self, extractor):
        """Test extraction with mixed case."""
        from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import PolicyArea
        
        text = "El MINISTERIO de salud, la secretaría de EDUCACIÓN y el IcBf coordinan."
        entities = extractor._extract_entities(PolicyArea.SALUD, text)
        
        assert len(entities) > 0, "Should handle mixed case"


if __name__ == "__main__":
    print("Running real-world validation tests...")
    
    from farfan_pipeline.dashboard_atroz_.signal_extraction_sota import SOTASignalExtractor, PolicyArea
    
    extractor = SOTASignalExtractor(enable_spacy=True)
    
    # Quick test on real PA02 text
    text = REAL_WORLD_SAMPLES["PA02_salud"]
    entities = extractor._extract_entities(PolicyArea.SALUD, text)
    
    print(f"\n✓ Real-world PA02 extraction:")
    print(f"  Input: {len(text)} characters")
    print(f"  Output: {len(entities)} entities")
    print(f"  Top 5: {entities[:5]}")
    
    print("\n✓ Real-world validation ready!")
    print("Run with pytest for full validation suite.")
