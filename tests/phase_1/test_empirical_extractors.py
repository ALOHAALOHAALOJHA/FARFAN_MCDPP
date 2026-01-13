
import pytest
import sys
from pathlib import Path

# Ensure src is in path
sys.path.append("src")

from farfan_pipeline.infrastructure.extractors.financial_chain_extractor import FinancialChainExtractor, extract_financial_chains
from farfan_pipeline.infrastructure.extractors.causal_verb_extractor import CausalVerbExtractor, extract_causal_links
from farfan_pipeline.infrastructure.extractors.institutional_ner_extractor import InstitutionalNERExtractor, extract_institutional_entities


class TestFinancialChainExtractor:
    def test_extract_monto_normalization(self):
        text = "Se asignan $1.5 millones para salud y 2.500 millones para educación."
        extractor = FinancialChainExtractor()
        result = extractor.extract(text)
        
        assert len(result.matches) >= 2
        
        # Check first match: 1.5 millones -> 1,500,000
        m1 = next(m for m in result.matches if "1.5" in m["monto"]["text"])
        assert m1["monto"]["valor_normalizado"] == 1_500_000
        
        # Check second match: 2.500 millones -> 2,500,000,000 ?? 
        # Wait, 2.500 millions is 2.5 billion? Or 2500 millions?
        # In Colombia, "2.500 millones" usually means 2500 * 10^6 = 2.5 * 10^9.
        # My heuristic logic: 2.500 with one dot -> remove dot -> 2500. 
        # Then apply "millones" -> 2500 * 10^6.
        m2 = next(m for m in result.matches if "2.500" in m["monto"]["text"])
        assert m2["monto"]["valor_normalizado"] == 2_500_000_000

    def test_extract_billones(self):
        text = "El presupuesto total es de $15.3 billones de pesos."
        extractor = FinancialChainExtractor()
        result = extractor.extract(text)
        
        assert len(result.matches) >= 1
        m = result.matches[0]
        # 15.3 billones -> 15.3 * 10^12
        assert m["monto"]["valor_normalizado"] == 15_300_000_000_000

    def test_link_components(self):
        text = """
        Programa: Salud para Todos
        Vigencia 2024-2027
        Se destinan $500 millones del SGP para este fin.
        """
        extractor = FinancialChainExtractor()
        result = extractor.extract(text)
        
        assert len(result.matches) >= 1
        chain = result.matches[0]
        
        assert chain["is_complete"]  # Monto + Fuente
        assert chain["monto"]["valor_normalizado"] == 500_000_000
        assert chain["fuente"]["fuente_type"] == "SGP"
        assert chain["programa"]["text"] == "Salud para Todos"
        assert chain["periodo"]["año_inicio"] == 2024


class TestCausalVerbExtractor:
    def test_causal_chain_extraction(self):
        text = "Se busca fortalecer la infraestructura educativa con el fin de mejorar la calidad."
        extractor = CausalVerbExtractor()
        result = extractor.extract(text)
        
        assert len(result.matches) >= 1
        link = result.matches[0]
        
        assert link["verb"] == "fortalecer"
        assert "infraestructura educativa" in link["object"]
        assert "mejorar la calidad" in link["outcome"]
        assert link["causal_strength"] == "medium"

    def test_connector_support(self):
        text = "Implementar programas mediante la asignación de recursos."
        extractor = CausalVerbExtractor()
        result = extractor.extract(text)
        
        assert len(result.matches) >= 1
        link = result.matches[0]
        
        assert link["verb"] == "Implementar"
        assert "programas" in link["object"]
        assert "la asignación de recursos" in link["outcome"]

    def test_hierarchy_link(self):
        text = "Garantizar derechos."
        context = {"programa": "Derechos Humanos", "policy_area": "PA01"}
        extractor = CausalVerbExtractor()
        result = extractor.extract(text, context)
        
        assert len(result.matches) >= 1
        link = result.matches[0]
        
        assert link["programmatic_link"] is not None
        assert link["programmatic_link"]["program"] == "Derechos Humanos"


class TestInstitutionalNERExtractor:
    def test_entity_extraction(self):
        text = "El DNP y el DANE trabajarán juntos."
        extractor = InstitutionalNERExtractor()
        result = extractor.extract(text)
        
        assert len(result.matches) >= 2
        entities = [m["canonical_name"] for m in result.matches]
        assert "Departamento Nacional de Planeación" in entities
        assert "Departamento Administrativo Nacional de Estadística" in entities

    def test_relationship_extraction(self):
        text = "La Alcaldía de Quibdó en coordinación con el ICBF realizará acciones."
        extractor = InstitutionalNERExtractor()
        result = extractor.extract(text)
        
        # Should find Alcaldía and ICBF
        matches = result.matches
        alcaldia = next(m for m in matches if "Alcaldía" in m["detected_as"])
        icbf = next(m for m in matches if "ICBF" in m["detected_as"])
        
        # Check relationship in Alcaldía
        assert len(alcaldia["relationships"]) > 0
        rel = alcaldia["relationships"][0]
        assert rel["related_entity_id"] == icbf["entity_id"]
        assert rel["type"] == "coordination"

