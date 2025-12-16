# F.A.R.F.A.N ARCHITECTURAL TRANSFORMATION: MASTER PLAN
## Unified Package Restructure + Aesthetic Protocol Enforcement + Complete Documentation

**Version**: 1.0  
**Authority**: Technical Architecture Team  
**Enforcement Level**: MANDATORY  
**Target Completion**: 2026-Q1

---

## 🎯 EXECUTIVE SUMMARY

This document provides a **surgical plan** to transform the F.A.R.F.A.N pipeline from a fragmented, inconsistently-named collection of modules into a **unified, industrial-grade Python package** while simultaneously enforcing the **ATROZ aesthetic protocol** across all visual components and establishing **comprehensive documentation**.

### The Triple Mandate

1. **RESTRUCTURE**: Consolidate 10 top-level packages → 1 canonical `farfan` package
2. **ENFORCE**: Apply ATROZ aesthetic protocol to all dashboard components
3. **DOCUMENT**: Create living, comprehensive documentation for all systems

---

## I. CURRENT STATE ANALYSIS

### 1.1 Critical Issues Identified

#### **Namespace Pollution (10 Top-Level Packages)**
```
src/
├── batch_concurrence/          ❌ Orphaned utility
├── calibration/                ❌ Should be under analysis
├── canonic_phases/             ❌ Core logic, not integrated
├── core/                       ❌ Empty or redundant
├── cross_cutting_infrastructure/ ❌ Typo in imports everywhere
├── dashboard_atroz_/           ❌ Trailing underscore, aesthetic debt
├── farfan_pipeline/            ✅ Intended package (underutilized)
├── methods_dispensary/         ❌ Kitchen sink pattern
├── ontology/                   ❌ Should be under analysis
└── orchestration/              ❌ Should be in core
```

**Impact**: 
- Cannot install as proper package (`pip install -e .` requires hacks)
- Imports are verbose and disconnected
- `sys.path` manipulation required everywhere

#### **Naming Chaos**
```python
# Inconsistent case and format
from canonic_phases.Phase_one import ...         # TitleCase
from canonic_phases.Phase_four_five_six_seven... # Merged phases
from orchestration.orchestrator import ...       # snake_case

# Spanglish/typos
from cross_cutting_infrastrucuture import ...    # Typo (missing 't')
import contradiction_deteccion                   # Spanish suffix

# Backup files committed
import financiero_viabilidad_tablas copy         # "copy" in filename
```

#### **Import Typo Crisis**
```bash
# The typo that breaks everything
$ grep -r "cross_cutting_infrastrucuture" tests/ | wc -l
      47

# Correct spelling exists in filesystem
$ ls src/
cross_cutting_infrastructure  # ← Correct

# Result: 47 test files fail to import unless patched
```

#### **Test Disorganization**
```
tests/
├── choquet_tests.py           # Root level, no organization
├── test_phase0_complete.py    # Root level
├── canonic_phases/            # Partially mirrored
│   └── Phase_one/            # Incomplete
└── calibration/               # Random placement
```

#### **Aesthetic Debt (Dashboard)**
```javascript
// dashboard.html contains:
window.pdetRegions = [
    { id: 'arauca', score: 85, ... }  // ❌ HARDCODED MOCK DATA
];

const score = Math.random();  // ❌ NO REAL AGGREGATION

// ❌ No connection to ATROZ_AESTHETIC_PROTOCOL_ENFORCEMENT.md
// ❌ Colors don't match canonical palette
// ❌ Glassmorphism missing on panels
```

---

## II. TARGET ARCHITECTURE

### 2.1 Unified Package Structure

```
src/
└── farfan/                           # Single canonical package
    ├── __init__.py
    ├── __version__.py
    │
    ├── core/                         # Core domain logic
    │   ├── __init__.py
    │   ├── orchestration/            # ← orchestration/ moved here
    │   │   ├── __init__.py
    │   │   ├── engine.py             # ← orchestrator.py renamed
    │   │   ├── memory_safety.py
    │   │   └── synchronization.py
    │   ├── types.py                  # ← farfan_pipeline/core/types.py
    │   ├── parameters.py             # ← farfan_pipeline/core/parameters.py
    │   ├── config.py
    │   └── events.py
    │
    ├── phases/                       # ← canonic_phases/ moved here
    │   ├── __init__.py
    │   ├── phase_00_bootstrap/       # ← Phase_zero renamed
    │   │   ├── __init__.py
    │   │   ├── bootstrap.py
    │   │   ├── determinism.py
    │   │   ├── seed_factory.py
    │   │   └── paths.py
    │   ├── phase_01_ingestion/       # ← Phase_one renamed
    │   │   ├── __init__.py
    │   │   ├── validation.py
    │   │   └── extraction.py
    │   ├── phase_02_analysis/        # ← Phase_two renamed
    │   ├── phase_03_scoring/         # ← Phase_three renamed
    │   ├── phase_04_aggregation/     # ← Phase_four_five_six_seven split
    │   │   ├── __init__.py
    │   │   ├── adaptive_meso.py
    │   │   ├── choquet_aggregator.py
    │   │   └── provenance.py
    │   └── phase_09_reporting/       # ← Phase_nine renamed
    │
    ├── analysis/                     # ← methods_dispensary + calibration
    │   ├── __init__.py
    │   ├── methods/                  # Specific analysis methods
    │   │   ├── __init__.py
    │   │   ├── bayesian.py
    │   │   ├── contradiction.py      # ← contradiction_deteccion.py
    │   │   ├── derek_beach.py        # Keep name (methodology)
    │   │   └── financial.py          # ← financiero_viabilidad_tablas.py
    │   ├── calibration/              # ← calibration/ moved
    │   │   ├── __init__.py
    │   │   └── ...
    │   ├── ontology/                 # ← ontology/ moved
    │   │   ├── __init__.py
    │   │   └── ...
    │   └── scoring/                  # ← farfan_pipeline/analysis/scoring
    │       ├── __init__.py
    │       ├── scoring.py
    │       └── mathematical_foundation.py
    │
    ├── infrastructure/               # ← cross_cutting_infrastructure
    │   ├── __init__.py
    │   ├── sisas/
    │   │   ├── __init__.py
    │   │   └── ...
    │   ├── contracts/
    │   │   ├── __init__.py
    │   │   └── ...
    │   └── signals/
    │       ├── __init__.py
    │       └── ...
    │
    ├── dashboard/                    # ← dashboard_atroz_ renamed
    │   ├── __init__.py
    │   ├── app.py                    # Flask application
    │   ├── data_service.py
    │   ├── aesthetics/               # NEW: Aesthetic enforcement
    │   │   ├── __init__.py
    │   │   ├── enforcer.py           # ATROZ protocol enforcer
    │   │   ├── plotly_theme.py
    │   │   └── validators.py
    │   └── static/
    │       ├── css/
    │       │   └── atroz_protocol.css  # Canonical CSS
    │       ├── js/
    │       │   ├── atroz_theme.js
    │       │   └── constellation.js
    │       └── index.html
    │
    ├── processing/                   # ← farfan_pipeline/processing
    │   ├── __init__.py
    │   ├── aggregation_provenance.py
    │   ├── choquet_adapter.py
    │   └── uncertainty_quantification.py
    │
    └── utils/                        # Shared utilities
        ├── __init__.py
        ├── paths.py                  # Centralized path resolution
        ├── concurrency.py            # ← batch_concurrence/ moved
        ├── cpp_adapter.py
        └── validation/
            ├── __init__.py
            └── schema_validator.py
```

### 2.2 Test Structure (Mirrored)

```
tests/
├── __init__.py
├── conftest.py                       # Global fixtures
│
├── core/
│   ├── conftest.py
│   ├── test_orchestration.py
│   └── test_parameters.py
│
├── phases/
│   ├── test_phase_00_bootstrap.py
│   ├── test_phase_01_ingestion.py
│   ├── test_phase_03_scoring.py
│   └── test_phase_04_aggregation.py
│
├── analysis/
│   ├── test_bayesian.py
│   ├── test_contradiction.py
│   └── calibration/
│       └── test_calibration.py
│
├── infrastructure/
│   ├── test_sisas.py
│   └── test_contracts.py
│
├── dashboard/
│   ├── test_data_service.py
│   └── aesthetics/
│       ├── test_enforcer.py
│       └── test_validators.py
│
└── integration/
    ├── test_full_pipeline.py
    └── test_orchestrator_flow.py
```

---

## III. IMPLEMENTATION ROADMAP

### Phase 1: Preparation (Week 1)

#### 1.1 Audit Current State
```bash
# Generate complete import map
python scripts/analyze_imports.py > import_map_current.txt

# Count typo occurrences
grep -r "cross_cutting_infrastrucuture" . | wc -l > typo_count.txt

# List all Phase directories
find src/canonic_phases -type d -name "Phase_*" > phase_list.txt
```

#### 1.2 Create Backup
```bash
# Create git branch
git checkout -b feature/architectural-transformation
git push -u origin feature/architectural-transformation

# Tag current state
git tag pre-restructure-$(date +%Y%m%d)
git push --tags
```

#### 1.3 Generate Migration Scripts
```python
# scripts/generate_migration_plan.py
"""
Generates file-by-file migration commands
"""
import os
from pathlib import Path

MIGRATIONS = {
    'src/orchestration': 'src/farfan/core/orchestration',
    'src/canonic_phases/Phase_zero': 'src/farfan/phases/phase_00_bootstrap',
    'src/canonic_phases/Phase_one': 'src/farfan/phases/phase_01_ingestion',
    # ... (complete mapping)
}

def generate_migration_script():
    with open('migrate_files.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('set -e\n\n')
        
        for old_path, new_path in MIGRATIONS.items():
            f.write(f'mkdir -p {new_path}\n')
            f.write(f'cp -r {old_path}/* {new_path}/\n')
            f.write(f'echo "✓ Migrated {old_path}"\n\n')
```

### Phase 2: Structure Creation (Week 1-2)

#### 2.1 Create New Package Structure
```bash
#!/bin/bash
# scripts/create_structure.sh

cd src

# Create farfan package
mkdir -p farfan/{core,phases,analysis,infrastructure,dashboard,processing,utils}

# Create subpackages
mkdir -p farfan/core/orchestration
mkdir -p farfan/phases/{phase_00_bootstrap,phase_01_ingestion,phase_02_analysis,phase_03_scoring,phase_04_aggregation,phase_09_reporting}
mkdir -p farfan/analysis/{methods,calibration,ontology,scoring}
mkdir -p farfan/infrastructure/{sisas,contracts,signals}
mkdir -p farfan/dashboard/{aesthetics,static/{css,js}}
mkdir -p farfan/utils/validation

# Create __init__.py files
find farfan -type d -exec touch {}/__init__.py \;

echo "✓ Package structure created"
```

#### 2.2 Initialize Package Metadata
```python
# src/farfan/__init__.py
"""
F.A.R.F.A.N: Framework for Analytical Research on Formulation and Assessment of Norms

A mechanistic policy pipeline for analyzing 170 Colombian municipal development plans
using macro-meso-micro analytical framework.
"""

from farfan.__version__ import __version__

__all__ = [
    '__version__',
    'core',
    'phases',
    'analysis',
    'infrastructure',
    'dashboard',
]
```

```python
# src/farfan/__version__.py
__version__ = '2.0.0'  # Major restructuring
__author__ = 'FARFAN Research Team'
__license__ = 'Proprietary'
```

### Phase 3: File Migration (Week 2-3)

#### 3.1 Automated File Movement
```bash
#!/bin/bash
# scripts/migrate_files.sh

echo "🚀 Starting file migration..."

# Function to move and log
move_and_log() {
    local src=$1
    local dest=$2
    
    if [ -f "$src" ] || [ -d "$src" ]; then
        mkdir -p "$(dirname "$dest")"
        mv "$src" "$dest"
        echo "✓ $src → $dest"
    else
        echo "⚠️  Skipped $src (not found)"
    fi
}

# Core orchestration
move_and_log "src/orchestration/orchestrator.py" "src/farfan/core/orchestration/engine.py"
move_and_log "src/orchestration/memory_safety.py" "src/farfan/core/orchestration/memory_safety.py"

# Phases (with renaming)
move_and_log "src/canonic_phases/Phase_zero" "src/farfan/phases/phase_00_bootstrap"
move_and_log "src/canonic_phases/Phase_one" "src/farfan/phases/phase_01_ingestion"
move_and_log "src/canonic_phases/Phase_two" "src/farfan/phases/phase_02_analysis"
move_and_log "src/canonic_phases/Phase_three" "src/farfan/phases/phase_03_scoring"
move_and_log "src/canonic_phases/Phase_four_five_six_seven" "src/farfan/phases/phase_04_aggregation"
move_and_log "src/canonic_phases/Phase_nine" "src/farfan/phases/phase_09_reporting"

# Analysis methods
move_and_log "src/methods_dispensary" "src/farfan/analysis/methods"
move_and_log "src/calibration" "src/farfan/analysis/calibration"
move_and_log "src/ontology" "src/farfan/analysis/ontology"

# Infrastructure (TYPO FIX)
move_and_log "src/cross_cutting_infrastructure" "src/farfan/infrastructure"

# Dashboard
move_and_log "src/dashboard_atroz_" "src/farfan/dashboard"

# Utilities
move_and_log "src/batch_concurrence" "src/farfan/utils/concurrency"

echo "✅ File migration complete"
```

#### 3.2 Rename Files (Snake Case)
```bash
#!/bin/bash
# scripts/rename_files.sh

cd src/farfan

# Fix Spanish/typo names
mv analysis/methods/contradiction_deteccion.py analysis/methods/contradiction.py
mv analysis/methods/financiero_viabilidad_tablas.py analysis/methods/financial.py

# Remove "copy" files
find . -name "*copy.py" -delete
find . -name "*copy 2.py" -delete

echo "✓ File renaming complete"
```

### Phase 4: Import Refactoring (Week 3-4)

#### 4.1 Automated Import Replacement
```python
# scripts/refactor_imports.py
"""
Systematically replaces all old imports with new structure
"""
import re
import os
from pathlib import Path

IMPORT_MAPPINGS = {
    # Orchestration
    r'from orchestration import (.+)': r'from farfan.core.orchestration import \1',
    r'from orchestration\.orchestrator import (.+)': r'from farfan.core.orchestration.engine import \1',
    
    # Phases
    r'from canonic_phases\.Phase_zero import (.+)': r'from farfan.phases.phase_00_bootstrap import \1',
    r'from canonic_phases\.Phase_one import (.+)': r'from farfan.phases.phase_01_ingestion import \1',
    r'from canonic_phases\.Phase_three import (.+)': r'from farfan.phases.phase_03_scoring import \1',
    r'from canonic_phases\.Phase_four_five_six_seven import (.+)': r'from farfan.phases.phase_04_aggregation import \1',
    
    # TYPO FIX (critical)
    r'from cross_cutting_infrastrucuture import (.+)': r'from farfan.infrastructure import \1',
    r'from cross_cutting_infrastructure import (.+)': r'from farfan.infrastructure import \1',
    
    # Methods
    r'from methods_dispensary import (.+)': r'from farfan.analysis.methods import \1',
    
    # Dashboard
    r'from dashboard_atroz_ import (.+)': r'from farfan.dashboard import \1',
}

def refactor_file(filepath: Path):
    """Refactor imports in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
        content = re.sub(old_pattern, new_pattern, content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def refactor_all():
    """Refactor all Python files"""
    project_root = Path('src/farfan')
    modified_count = 0
    
    for py_file in project_root.rglob('*.py'):
        if refactor_file(py_file):
            print(f"✓ Refactored {py_file}")
            modified_count += 1
    
    print(f"\n✅ Modified {modified_count} files")

if __name__ == '__main__':
    refactor_all()
```

#### 4.2 Test Import Refactoring
```bash
#!/bin/bash
# scripts/refactor_test_imports.sh

cd tests

# Apply same import mappings to tests
python ../scripts/refactor_imports.py --target tests

echo "✓ Test imports refactored"
```

### Phase 5: Aesthetic Protocol Integration (Week 4-5)

#### 5.1 Install Aesthetic Enforcer
```bash
# Copy enforcer from implementation kit
cp /Users/recovered/dashboard_implementation_kit/aesthetics_enforcer.py \
   src/farfan/dashboard/aesthetics/enforcer.py

# Update imports
sed -i '' 's/from aesthetics_enforcer/from farfan.dashboard.aesthetics.enforcer/g' \
   src/farfan/dashboard/*.py
```

#### 5.2 Apply Protocol to Dashboard
```python
# src/farfan/dashboard/data_service.py (updated)
from farfan.dashboard.aesthetics.enforcer import (
    apply_atroz_theme,
    create_atroz_radar,
    create_atroz_heatmap,
    ATROZ_COLORS
)

class DashboardDataService:
    """Data service with ATROZ aesthetic enforcement"""
    
    def get_municipality_radar(self, municipality_id: str):
        """
        Returns Plotly radar chart with ATROZ theme enforced
        """
        scores = self.bridge.compute_municipality_scores(municipality_id)
        
        # MANDATORY: Use aesthetic enforcer
        fig = create_atroz_radar(
            data=scores['meso_scores'],
            name=municipality_id
        )
        
        return fig.to_json()
    
    def get_question_heatmap(self, municipality_id: str):
        """
        Returns heatmap with canonical color palette
        """
        scores = self.bridge.compute_municipality_scores(municipality_id)
        matrix = self._reshape_scores(scores['micro_scores'])
        
        # MANDATORY: Use aesthetic enforcer
        fig = create_atroz_heatmap(
            matrix=matrix,
            x_labels=['Governance', 'Social', 'Economic', 'Environmental'],
            y_labels=[f'Q{i*4+1}-Q{i*4+4}' for i in range(11)],
            title=f'{municipality_id}: Question Matrix'
        )
        
        return fig.to_json()
```

#### 5.3 Update Frontend CSS
```css
/* src/farfan/dashboard/static/css/atroz_protocol.css */

/* CANONICAL COLOR PALETTE (from ATROZ_AESTHETIC_PROTOCOL_ENFORCEMENT.md) */
:root {
    --atroz-red-900: #3A0E0E;
    --atroz-red-700: #7A0F0F;
    --atroz-red-500: #C41E3A;
    --atroz-blue-electric: #00D4FF;
    --atroz-green-toxic: #39FF14;
    --atroz-copper-500: #B2642E;
    --atroz-copper-700: #7B3F1D;
    --atroz-copper-oxide: #17A589;
    --ink: #E5E7EB;
    --bg: #0A0A0A;
}

/* MANDATORY: Glassmorphism on all panels */
.data-panel, .overlay, .modal, .card {
    background: rgba(4, 16, 26, 0.85);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(178, 100, 46, 0.3);
    box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.05),
        0 20px 60px rgba(0, 0, 0, 0.5);
}

/* MANDATORY: Bimodal typography */
.data-value, .metric, .score, code, pre {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    letter-spacing: 0.05em;
}

h1, h2, h3, h4, .headline, .label {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* MANDATORY: Organic pulse animation */
@keyframes organicPulse {
    0%, 100% {
        transform: scale(1) rotate(0deg);
        opacity: 0.7;
    }
    25% {
        transform: scale(1.02) rotate(0.5deg);
        opacity: 0.8;
    }
    50% {
        transform: scale(0.98) rotate(-0.5deg);
        opacity: 0.6;
    }
    75% {
        transform: scale(1.01) rotate(0.3deg);
        opacity: 0.9;
    }
}

.constellation-map, .viz-card {
    animation: organicPulse 15s ease-in-out infinite;
}
```

### Phase 6: Documentation Generation (Week 5-6)

#### 6.1 Package-Level Documentation
```python
# src/farfan/__init__.py (enhanced)
"""
F.A.R.F.A.N: Framework for Analytical Research on Formulation and Assessment of Norms
======================================================================================

A mechanistic policy pipeline analyzing 170 Colombian municipal development plans
using a macro-meso-micro analytical framework.

**Architecture**:
    - Core: Orchestration engine, types, parameters
    - Phases: 9-phase pipeline (bootstrap → reporting)
    - Analysis: Methods, calibration, scoring, ontology
    - Infrastructure: SISAS, contracts, signals
    - Dashboard: ATROZ-themed visualization dashboard
    - Processing: Aggregation, uncertainty quantification
    - Utils: Shared utilities

**Key Concepts**:
    - Macro: Municipality-level composite scores
    - Meso: 4-cluster aggregation (governance, social, economic, environmental)
    - Micro: 44-question detailed analysis
    
**Data Scale**:
    - 170 municipalities
    - 44 questions per municipality
    - 51,000 sub-answers (evidence-based)
    - 16 PDET subregions

**Usage**:
    >>> from farfan.core.orchestration import Engine
    >>> engine = Engine(config_path='config/production.yaml')
    >>> result = engine.run_full_pipeline()
    
    >>> from farfan.dashboard import app
    >>> app.run(debug=True)

**Aesthetic Protocol**:
    All visualizations MUST comply with ATROZ_AESTHETIC_PROTOCOL_ENFORCEMENT.md
    - Canonical color palette
    - Glassmorphism + organic animations
    - Bimodal typography (JetBrains Mono for data)
    - Risk spectrum: Cyan → Copper → Crimson → Toxic Green

**Version**: 2.0.0 (Major Architectural Restructure)
**License**: Proprietary
**Contact**: FARFAN Research Team
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
```

#### 6.2 Generate API Documentation
```bash
#!/bin/bash
# scripts/generate_docs.sh

pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Initialize Sphinx
cd docs
sphinx-quickstart

# Configure
cat > source/conf.py << 'EOF'
import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'F.A.R.F.A.N'
copyright = '2025, FARFAN Research Team'
author = 'FARFAN Research Team'
version = '2.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]

html_theme = 'sphinx_rtd_theme'
EOF

# Generate API docs
sphinx-apidoc -o source/ ../src/farfan

# Build HTML
make html

echo "✓ Documentation generated in docs/build/html"
```

#### 6.3 Create Architecture Diagrams
```python
# scripts/generate_architecture_diagram.py
"""
Generates visual architecture diagram using Graphviz
"""
from graphviz import Digraph

def create_architecture_diagram():
    dot = Digraph('farfan_architecture', comment='FARFAN Package Architecture')
    dot.attr(rankdir='TB', splines='ortho')
    
    # Packages
    dot.node('farfan', 'farfan\n(root package)', shape='folder', style='filled', fillcolor='#00D4FF')
    
    # Core
    dot.node('core', 'core\n(orchestration, types)', shape='box', style='filled', fillcolor='#BFEFCB')
    dot.edge('farfan', 'core')
    
    # Phases
    dot.node('phases', 'phases\n(9 pipeline phases)', shape='box', style='filled', fillcolor='#B2642E')
    dot.edge('farfan', 'phases')
    
    # Analysis
    dot.node('analysis', 'analysis\n(methods, scoring)', shape='box', style='filled', fillcolor='#17A589')
    dot.edge('farfan', 'analysis')
    
    # Infrastructure
    dot.node('infra', 'infrastructure\n(SISAS, contracts)', shape='box', style='filled', fillcolor='#7A0F0F')
    dot.edge('farfan', 'infra')
    
    # Dashboard
    dot.node('dashboard', 'dashboard\n(ATROZ aesthetic)', shape='box', style='filled', fillcolor='#39FF14')
    dot.edge('farfan', 'dashboard')
    
    # Dependencies
    dot.edge('core', 'phases', style='dashed', label='orchestrates')
    dot.edge('phases', 'analysis', style='dashed', label='uses')
    dot.edge('phases', 'infra', style='dashed', label='requires')
    dot.edge('dashboard', 'core', style='dashed', label='queries')
    
    dot.render('docs/architecture', format='png', cleanup=True)
    print("✓ Architecture diagram generated: docs/architecture.png")

if __name__ == '__main__':
    create_architecture_diagram()
```

### Phase 7: Configuration Updates (Week 6)

#### 7.1 Update setup.py
```python
# setup.py (complete rewrite)
from setuptools import setup, find_packages
from pathlib import Path

# Read version
version = {}
with open('src/farfan/__version__.py') as f:
    exec(f.read(), version)

# Read README
long_description = (Path(__file__).parent / 'README.md').read_text()

setup(
    name='farfan-pipeline',
    version=version['__version__'],
    description='Framework for Analytical Research on Formulation and Assessment of Norms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='FARFAN Research Team',
    author_email='technical@farfan-research.org',
    url='https://github.com/farfan-research/pipeline',
    license='Proprietary',
    
    # CRITICAL: Single package, properly configured
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        'farfan': ['**/*.yaml', '**/*.json', '**/*.css', '**/*.js'],
        'farfan.dashboard': ['static/**/*', 'templates/**/*'],
    },
    
    # Dependencies
    install_requires=[
        'numpy>=1.26.0',
        'pandas>=2.1.0',
        'plotly>=5.18.0',
        'dash>=2.14.0',
        'flask>=3.0.0',
        'flask-socketio>=5.3.0',
        'scipy>=1.11.0',
        'pyyaml>=6.0',
    ],
    
    # Development dependencies
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'mypy>=1.5.0',
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.3.0',
        ],
        'dashboard': [
            'gunicorn>=21.0.0',
            'gevent>=23.9.0',
        ],
    },
    
    # Entry points
    entry_points={
        'console_scripts': [
            'farfan=farfan.core.orchestration.engine:main',
            'farfan-dashboard=farfan.dashboard.app:main',
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    
    python_requires='>=3.10',
)
```

#### 7.2 Update pyproject.toml
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "farfan-pipeline"
dynamic = ["version"]
description = "Framework for Analytical Research on Formulation and Assessment of Norms"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Proprietary"}
authors = [
    {name = "FARFAN Research Team", email = "technical@farfan-research.org"}
]

[project.urls]
Homepage = "https://github.com/farfan-research/pipeline"
Documentation = "https://farfan-pipeline.readthedocs.io"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=farfan --cov-report=html"

[tool.black]
line-length = 100
target-version = ['py310', 'py311']
include = '\.pyi?$'

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

#### 7.3 Update pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=farfan
    --cov-report=html:htmlcov
    --cov-report=term-missing

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    aesthetic: marks tests for aesthetic protocol validation
```

### Phase 8: Validation & Testing (Week 7)

#### 8.1 Import Validation
```bash
#!/bin/bash
# scripts/validate_imports.sh

echo "🔍 Validating all imports..."

cd src

# Try importing main package
python -c "import farfan; print(f'✓ Package version: {farfan.__version__}')"

# Try importing all subpackages
python -c "from farfan import core; print('✓ core')"
python -c "from farfan import phases; print('✓ phases')"
python -c "from farfan import analysis; print('✓ analysis')"
python -c "from farfan import infrastructure; print('✓ infrastructure')"
python -c "from farfan import dashboard; print('✓ dashboard')"

# Check for typo imports (should fail)
if python -c "from farfan.infrastructure import cross_cutting_infrastrucuture" 2>/dev/null; then
    echo "❌ TYPO STILL EXISTS!"
    exit 1
else
    echo "✓ Typo eliminated"
fi

echo "✅ All imports valid"
```

#### 8.2 Aesthetic Protocol Validation
```bash
#!/bin/bash
# scripts/validate_aesthetics.sh

echo "🎨 Validating ATROZ aesthetic protocol..."

cd src/farfan/dashboard

# Run aesthetic enforcer tests
python -m pytest tests/dashboard/aesthetics/ -v

# Validate CSS colors
python aesthetics/validators.py --check-css static/css/atroz_protocol.css

# Check forbidden colors
if grep -r "#FFFFFF\|#000000" static/css/ | grep -v "comment"; then
    echo "❌ Forbidden colors detected!"
    exit 1
fi

echo "✅ Aesthetic protocol validated"
```

#### 8.3 Run Full Test Suite
```bash
#!/bin/bash
# scripts/run_tests.sh

echo "🧪 Running full test suite..."

# Unit tests
pytest tests/core tests/phases tests/analysis -m "unit" -v

# Integration tests
pytest tests/integration -m "integration" -v

# Aesthetic tests
pytest tests/dashboard/aesthetics -m "aesthetic" -v

# Coverage report
pytest --cov=farfan --cov-report=html --cov-report=term-missing

echo "✅ Test suite complete"
```

### Phase 9: Deployment (Week 8)

#### 9.1 Package Installation
```bash
# Install in development mode
pip install -e ".[dev,dashboard]"

# Verify installation
python -c "import farfan; print(farfan.__version__)"

# Run dashboard
farfan-dashboard --host 0.0.0.0 --port 8000
```

#### 9.2 Generate Distribution
```bash
# Build package
python -m build

# Verify dist/
ls -lh dist/
# Should show:
# farfan_pipeline-2.0.0-py3-none-any.whl
# farfan-pipeline-2.0.0.tar.gz
```

---

## IV. SUCCESS METRICS

### 4.1 Technical Metrics

| Metric | Before | Target | Validation |
|--------|--------|--------|------------|
| Top-level packages | 10 | 1 | `ls src/` |
| Import errors (typo) | 47 | 0 | `pytest tests/` |
| Consistent naming | 30% | 100% | Manual audit |
| Documentation coverage | 10% | 90% | Sphinx |
| Aesthetic compliance | 0% | 100% | Validator |
| Test organization | Chaotic | Mirrored | `ls tests/` |

### 4.2 Developer Experience

- **Before**: "Where does X go?" → 5+ minutes searching
- **After**: "Where does X go?" → Instant (`farfan.{core|phases|analysis}`)

### 4.3 Installation Success

```bash
# Before (FAILS)
pip install -e .
# ImportError: No module named 'orchestration'

# After (WORKS)
pip install -e .
import farfan
# Success!
```

---

## V. ROLLBACK PLAN

If issues arise, rollback is simple:

```bash
#!/bin/bash
# scripts/rollback.sh

git checkout main
git branch -D feature/architectural-transformation
git tag -d pre-restructure-*

echo "⏪ Rolled back to main branch"
```

---

## VI. DOCUMENTATION DELIVERABLES

### 6.1 Core Documentation Files

```
docs/
├── README.md                          # User-facing quick start
├── ARCHITECTURE.md                    # This document
├── AESTHETIC_PROTOCOL.md              # ATROZ enforcement rules
├── CONTRIBUTING.md                    # Developer guidelines
├── CHANGELOG.md                       # Version history
│
├── api/                               # Sphinx-generated API docs
│   ├── farfan.core.html
│   ├── farfan.phases.html
│   ├── farfan.analysis.html
│   └── ...
│
├── guides/                            # User guides
│   ├── getting_started.md
│   ├── pipeline_overview.md
│   ├── dashboard_usage.md
│   └── aesthetic_customization.md
│
├── diagrams/                          # Visual documentation
│   ├── architecture.png
│   ├── data_flow.png
│   └── phase_sequence.png
│
└── examples/                          # Code examples
    ├── basic_usage.py
    ├── custom_analysis.py
    └── dashboard_theming.py
```

### 6.2 Inline Documentation Standards

**Every module MUST have**:
```python
"""
Module one-line description.

Extended description explaining purpose, key concepts, and usage.

**Key Classes**:
    - ClassName: Brief description

**Key Functions**:
    - function_name: Brief description

**Usage**:
    >>> from farfan.module import Class
    >>> instance = Class()
    >>> result = instance.method()

**Related**:
    - farfan.other.module: Cross-reference

**Version**: Added in v2.0.0
"""
```

---

## VII. AESTHETIC PROTOCOL INTEGRATION CHECKLIST

Before ANY dashboard code is deployed:

### ✅ **Visual Compliance**
- [ ] All colors from `ATROZ_COLORS` palette
- [ ] Glassmorphism on panels (`backdrop-filter: blur(20px)`)
- [ ] Bimodal typography (JetBrains Mono for data)
- [ ] Organic pulse animation (15s cycle)
- [ ] Directional shadows (lower-right 45°)
- [ ] Hover states with tactile feedback

### ✅ **Code Compliance**
- [ ] `from farfan.dashboard.aesthetics.enforcer import *`
- [ ] All Plotly charts use `apply_atroz_theme()`
- [ ] Color mapping via `get_state_color()`
- [ ] No forbidden colors (#FFFFFF, #000000)
- [ ] All transitions use cubic-bezier easing

### ✅ **Philosophical Compliance**
- [ ] Dashboard "sutures" data wounds (Salcedo)
- [ ] Interface shows data materiality (de Sagazan)
- [ ] Design questions its own biases (Adorno)

---

## VIII. TIMELINE SUMMARY

```
Week 1: Preparation & Structure Creation
  ├── Audit current state
  ├── Create backups
  └── Generate migration scripts

Week 2-3: File Migration & Renaming
  ├── Move files to new structure
  ├── Rename to snake_case
  └── Fix typos (infrastrucuture → infrastructure)

Week 3-4: Import Refactoring
  ├── Automated regex replacement
  ├── Update all test imports
  └── Validate no broken imports

Week 4-5: Aesthetic Integration
  ├── Install aesthetic enforcer
  ├── Apply ATROZ theme to dashboard
  └── Update CSS/JS with canonical palette

Week 5-6: Documentation Generation
  ├── Package-level docstrings
  ├── Sphinx API docs
  └── Architecture diagrams

Week 6: Configuration Updates
  ├── Rewrite setup.py
  ├── Update pyproject.toml
  └── Configure pytest

Week 7: Validation & Testing
  ├── Import validation
  ├── Aesthetic validation
  └── Full test suite

Week 8: Deployment
  ├── Package installation
  └── Distribution generation
```

---

## IX. FINAL DELIVERABLES

Upon completion, the repository will have:

1. ✅ **Unified Package**: Single `farfan` namespace
2. ✅ **Consistent Naming**: All snake_case, descriptive
3. ✅ **Zero Typos**: `infrastrucuture` eliminated
4. ✅ **Aesthetic Enforcement**: ATROZ protocol applied
5. ✅ **Complete Documentation**: Sphinx + guides + diagrams
6. ✅ **Proper Installation**: `pip install -e .` works
7. ✅ **Organized Tests**: Mirrored structure
8. ✅ **Type Hints**: mypy-compliant
9. ✅ **Entry Points**: CLI tools (`farfan`, `farfan-dashboard`)
10. ✅ **Living Architecture**: This document as reference

---

## X. GOVERNANCE

### 10.1 Change Control

**All future changes MUST**:
1. Follow naming conventions (snake_case)
2. Stay within `farfan` namespace
3. Comply with aesthetic protocol
4. Include documentation
5. Pass all tests

### 10.2 Review Process

```
Developer → Branch → PR → Review → Tests → Merge
                      ↓
                  Aesthetic validation
                  Import validation
                  Test coverage check
```

---

## XI. CONCLUSION

This transformation is not optional. It is **essential** for:

1. **Maintainability**: Clear structure = easy maintenance
2. **Scalability**: Room to grow without chaos
3. **Professionalism**: Industrial-grade Python package
4. **Aesthetic Justice**: Data visualization as ethical act
5. **Documentation**: Living knowledge base

**Every file, every import, every color is an act of intentional design.**

---

**Status**: 🟢 **APPROVED FOR EXECUTION**  
**Priority**: **CRITICAL**  
**Timeline**: 8 weeks  
**Risk**: Low (reversible via git)  
**ROI**: Infinite (transforms chaos → clarity)

---

**Next Command**: `bash scripts/create_structure.sh`

**Let's build a masterpiece.** 🎨⚡🏗️
