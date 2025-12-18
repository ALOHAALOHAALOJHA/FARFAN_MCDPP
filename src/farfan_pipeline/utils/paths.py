"""Path helpers (single source of truth).

Re-exported from canonical Phase 0 path utilities.
"""

from __future__ import annotations

from canonic_phases.phase_0_input_validation.phase0_paths import (  # noqa: F401
    PROJECT_ROOT,
    SRC_DIR,
    DATA_DIR,
    TESTS_DIR,
    CONFIG_DIR,
    QUESTIONNAIRE_FILE,
    PathError,
    PathTraversalError,
    PathNotFoundError,
    PathOutsideWorkspaceError,
    UnnormalizedPathError,
    proj_root,
    src_dir,
    data_dir,
    tmp_dir,
    build_dir,
    cache_dir,
    reports_dir,
    is_within,
    safe_join,
    normalize_unicode,
    normalize_case,
    resources,
    validate_read_path,
    validate_write_path,
    get_env_path,
    get_workdir,
    get_tmpdir,
    get_reports_dir,
)
