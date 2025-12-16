#!/bin/bash
#
# FARFAN Package Structure Creator
# ==================================
# Creates the unified farfan package structure
#
# Usage: bash scripts/create_structure.sh
#

set -e  # Exit on error

echo "🏗️  FARFAN ARCHITECTURAL TRANSFORMATION"
echo "======================================="
echo ""
echo "Phase 1: Creating package structure..."
echo ""

cd "$(dirname "$0")/.."  # Move to project root

# Create main farfan package
echo "Creating farfan/ package..."
mkdir -p src/farfan

# Create subpackages
echo "Creating core/ subpackages..."
mkdir -p src/farfan/core/orchestration

echo "Creating phases/ subpackages..."
mkdir -p src/farfan/phases/{phase_00_bootstrap,phase_01_ingestion,phase_02_analysis,phase_03_scoring,phase_04_aggregation,phase_09_reporting}

echo "Creating analysis/ subpackages..."
mkdir -p src/farfan/analysis/{methods,calibration,ontology,scoring}

echo "Creating infrastructure/ subpackages..."
mkdir -p src/farfan/infrastructure/{sisas,contracts,signals}

echo "Creating dashboard/ subpackages..."
mkdir -p src/farfan/dashboard/{aesthetics,static/{css,js,assets}}

echo "Creating processing/ subpackages..."
mkdir -p src/farfan/processing

echo "Creating utils/ subpackages..."
mkdir -p src/farfan/utils/{validation,concurrency}

# Create __init__.py files
echo ""
echo "Creating __init__.py files..."
find src/farfan -type d -exec touch {}/__init__.py \;

# Create version file
cat > src/farfan/__version__.py << 'EOF'
__version__ = '2.0.0'
__author__ = 'FARFAN Research Team'
__license__ = 'Proprietary'
EOF

echo "✓ Created __version__.py"

# Create main package __init__.py
cat > src/farfan/__init__.py << 'EOF'
"""
F.A.R.F.A.N: Framework for Analytical Research on Formulation and Assessment of Norms
======================================================================================

A mechanistic policy pipeline for analyzing 170 Colombian municipal development plans.

**Usage**:
    >>> from farfan.core.orchestration import Engine
    >>> engine = Engine()
    >>> result = engine.run()

**Version**: 2.0.0 (Major Architectural Restructure)
"""

from farfan.__version__ import __version__

__all__ = [
    '__version__',
    'core',
    'phases',
    'analysis',
    'infrastructure',
    'dashboard',
    'processing',
    'utils',
]
EOF

echo "✓ Created main __init__.py"

# Create README for each major package
cat > src/farfan/core/README.md << 'EOF'
# farfan.core

Core orchestration logic, types, and parameters.

## Modules

- `orchestration/`: Pipeline orchestration engine
- `types.py`: Canonical type definitions
- `parameters.py`: Configuration parameters
EOF

cat > src/farfan/phases/README.md << 'EOF'
# farfan.phases

Nine-phase analytical pipeline.

## Phases

0. Bootstrap: Configuration and determinism
1. Ingestion: Data loading and validation
2. Analysis: Method application
3. Scoring: Micro-level scoring
4. Aggregation: Meso-level aggregation
9. Reporting: Final report generation
EOF

cat > src/farfan/dashboard/README.md << 'EOF'
# farfan.dashboard

ATROZ-themed visualization dashboard.

## Aesthetic Protocol

ALL visualizations MUST comply with `ATROZ_AESTHETIC_PROTOCOL_ENFORCEMENT.md`:
- Canonical color palette
- Glassmorphism
- Bimodal typography
- Organic animations
EOF

echo "✓ Created READMEs"

# Create directory structure diagram
cat > DIRECTORY_STRUCTURE.txt << 'EOF'
src/farfan/
├── __init__.py
├── __version__.py
├── core/
│   ├── orchestration/
│   ├── types.py
│   └── parameters.py
├── phases/
│   ├── phase_00_bootstrap/
│   ├── phase_01_ingestion/
│   ├── phase_02_analysis/
│   ├── phase_03_scoring/
│   ├── phase_04_aggregation/
│   └── phase_09_reporting/
├── analysis/
│   ├── methods/
│   ├── calibration/
│   ├── ontology/
│   └── scoring/
├── infrastructure/
│   ├── sisas/
│   ├── contracts/
│   └── signals/
├── dashboard/
│   ├── aesthetics/
│   └── static/
├── processing/
└── utils/
    ├── validation/
    └── concurrency/
EOF

echo "✓ Created directory structure diagram"

echo ""
echo "✅ Package structure created successfully!"
echo ""
echo "Next steps:"
echo "  1. Review: cat DIRECTORY_STRUCTURE.txt"
echo "  2. Migrate files: bash scripts/migrate_files.sh"
echo "  3. Refactor imports: python scripts/refactor_imports.py"
echo ""
