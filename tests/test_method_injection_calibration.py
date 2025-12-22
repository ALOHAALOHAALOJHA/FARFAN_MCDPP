"""Test method-specific calibration parameter injection and registry integration."""
import pytest
from src.farfan_pipeline.core.canonical_specs import get_bayesian_prior


def test_method_specific_params_loaded():
    """Verify method-specific calibration parameters are loaded from canonical_specs."""
    # Test uniform prior methods
    prior = get_bayesian_prior("policy_processor")
    assert prior.alpha == 1.0
    assert prior.beta == 1.0
    assert "Uniform" in prior.strategy
    
    # Test symmetric prior method
    prior = get_bayesian_prior("bayesian_multilevel_system")
    assert prior.alpha == 2.0
    assert prior.beta == 2.0
    assert "Symmetric" in prior.strategy
    
    # Test asymmetric conservative prior
    prior = get_bayesian_prior("contradiction_deteccion")
    assert prior.alpha == 2.5
    assert prior.beta == 7.5
    assert prior.prior_expectation == 0.25  # 2.5/(2.5+7.5)


def test_question_specific_override():
    """Verify question-specific priors override method defaults."""
    # Derek beach has question-specific empirical priors
    prior = get_bayesian_prior("derek_beach_default", "D6-Q8")
    assert prior.alpha == 1.2
    assert prior.beta == 15.0
    assert prior.prior_expectation == pytest.approx(0.074, rel=0.01)  # ~7% success rate
    
    prior = get_bayesian_prior("derek_beach_default", "D5-Q5")
    assert prior.alpha == 1.8
    assert prior.beta == 10.5
    assert prior.prior_expectation == pytest.approx(0.146, rel=0.01)  # ~15% success rate


def test_method_calibration_params_in_methods():
    """Verify all 8 method files have calibration_params attribute."""
    from src.farfan_pipeline.methods import policy_processor
    from src.farfan_pipeline.methods import semantic_chunking_policy
    from src.farfan_pipeline.methods import contradiction_deteccion
    from src.farfan_pipeline.methods import analyzer_one
    from src.farfan_pipeline.methods import teoria_cambio
    from src.farfan_pipeline.methods import bayesian_multilevel_system
    from src.farfan_pipeline.methods import embedding_policy
    from src.farfan_pipeline.methods import financiero_viabilidad_tablas
    
    # Check IndustrialPolicyProcessor has calibration_params
    assert hasattr(policy_processor.IndustrialPolicyProcessor, 'calibration_params')
    params = policy_processor.IndustrialPolicyProcessor.calibration_params
    assert params['domain'] == 'policy_semantics'
    assert params['prior_alpha'] == 1.0
    assert params['prior_beta'] == 1.0
    assert params['unit_of_analysis_aware'] is True
    
    # Check all have unit_of_analysis_aware flag
    for module in [semantic_chunking_policy, contradiction_deteccion, analyzer_one, 
                   teoria_cambio, bayesian_multilevel_system, embedding_policy]:
        # Get the main class from each module
        classes = [cls for name, cls in vars(module).items() 
                  if isinstance(cls, type) and hasattr(cls, 'calibration_params')]
        assert len(classes) > 0, f"No class with calibration_params in {module.__name__}"
        for cls in classes:
            assert 'unit_of_analysis_aware' in cls.calibration_params


def test_pdm_specific_patterns_in_text_methods():
    """Verify text-sensitive methods have PDM-specific expected_content_patterns."""
    from src.farfan_pipeline.methods import semantic_chunking_policy
    from src.farfan_pipeline.methods import analyzer_one
    from src.farfan_pipeline.methods import embedding_policy
    
    # These methods should have PDM structure awareness
    for module in [semantic_chunking_policy, analyzer_one, embedding_policy]:
        classes = [cls for name, cls in vars(module).items() 
                  if isinstance(cls, type) and hasattr(cls, 'calibration_params')]
        for cls in classes:
            params = cls.calibration_params
            # Should have expected_content_patterns for PDM/PDET domain
            assert 'expected_content_patterns' in params or 'pdm_structure_aware' in str(params)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
