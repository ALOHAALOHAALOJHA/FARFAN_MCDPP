# Sensitive Rules for Coding

This directory contains sensitive coding rules, specifications, and validation infrastructure for the F.A.R.F.A.N system.

## Contents

### 1. Canonical Notation (`canonical_notation/`)
Canonical notation specification for methods in the F.A.R.F.A.N policy analysis framework.

- **Purpose**: Define rigorous notation system for method classification
- **Key File**: `notation_metods` - Complete specification document
- **Usage**: Reference for method naming, layer assignments, and calibration status

### 2. Validation Suite (`validation_suite/`)
Comprehensive validation suite for F.A.R.F.A.N calibration system integrity.

**🔒 Classification: SENSITIVE**

- **Purpose**: Ensure calibration system mathematical correctness and schema compliance
- **Validators**: 6 core validators for layer completeness, fusion weights, anti-universality, intrinsic calibration, config files, and boundedness
- **Status**: Production Ready (v1.0.0)

#### Quick Start
```bash
# Run full validation suite
python -m sensitive_rules_for_coding.validation_suite.runner

# Run with detailed report
python -m sensitive_rules_for_coding.validation_suite.runner --detailed

# Run examples
python -m sensitive_rules_for_coding.validation_suite.examples
```

#### Documentation
- [Complete Guide](validation_suite/README.md) - Full user guide and API reference
- [Quick Reference](validation_suite/QUICK_REFERENCE.md) - Copy-paste commands
- [Manifest](validation_suite/MANIFEST.md) - System manifest and security classification
- [Index](validation_suite/INDEX.md) - Navigation and learning path

#### Key Features
✅ 6 comprehensive validators  
✅ Automated runner with pass/fail reporting  
✅ CLI interface with argparse  
✅ 21 test cases with pytest integration  
✅ Complete documentation (4 docs, 1,300 lines)  
✅ No external dependencies (stdlib only)  
✅ Type hints throughout  
✅ Production ready  

### 3. Policy Areas and Dimensions (`policy_areas_and_dimensions.json`)
Configuration file defining policy areas and analytical dimensions.

## Security Classification

### SENSITIVE Components
- **Validation Suite**: Contains critical system integrity checks
- **Canonical Notation**: Defines authoritative method classification

### Rationale
These components are marked SENSITIVE because:
1. Validate core calibration system integrity
2. Detect configuration corruption or tampering
3. Ensure mathematical soundness of aggregation
4. Guard against calibration collapse
5. Define authoritative system specifications

## Usage Guidelines

### For Developers
1. Review canonical notation before implementing methods
2. Run validation suite before committing configuration changes
3. Maintain sensitivity classification on all files
4. Follow security best practices

### For System Operators
1. Run validation suite as part of deployment checks
2. Store validation reports securely
3. Review validation failures before production deployment
4. Maintain audit trail of validation runs

### For CI/CD Integration
```bash
# Add to pipeline
python -m sensitive_rules_for_coding.validation_suite.runner --quiet
if [ $? -ne 0 ]; then
    echo "Validation failed - blocking deployment"
    exit 1
fi
```

## File Structure

```
sensitive_rules_for_coding/
├── README.md (this file)
├── canonical_notation/
│   ├── notation_metods
│   └── notation_questions/
├── validation_suite/
│   ├── __init__.py
│   ├── __main__.py
│   ├── validators.py
│   ├── runner.py
│   ├── examples.py
│   ├── README.md
│   ├── MANIFEST.md
│   ├── QUICK_REFERENCE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── INDEX.md
└── policy_areas_and_dimensions.json
```

## Recent Additions

### Validation Suite (2025-01-30)
Complete implementation of comprehensive validation infrastructure:
- 1,340 lines of implementation code
- 1,300 lines of documentation
- 420 lines of test code
- 6 production-ready validators
- Full CLI and Python API
- Extensive test coverage

## Dependencies

### Validation Suite
- Python 3.12+
- Standard library only (no external dependencies)
- pytest (for testing only)

### Canonical Notation
- No dependencies (documentation only)

## Maintenance

### Adding New Validators
1. Implement validator function in `validation_suite/validators.py`
2. Add to runner in `validation_suite/runner.py`
3. Write tests in `tests/test_validation_suite.py`
4. Update documentation

### Updating Canonical Notation
1. Review `canonical_notation/notation_metods`
2. Ensure compatibility with existing methods
3. Update layer requirements if needed
4. Run validation suite to verify changes

## Support

For questions or issues:
- See individual component documentation
- Follow F.A.R.F.A.N contribution guidelines
- Maintain sensitivity classification
- Respect security protocols

## Version Information

- **Validation Suite**: v1.0.0 (2025-01-30)
- **Canonical Notation**: Current specification
- **Directory Structure**: Stable

---

**Note**: This directory contains sensitive system specifications and validation infrastructure. Handle with appropriate security measures.
