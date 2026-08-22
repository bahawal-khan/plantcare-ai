"""Phase 01 sanity tests: verify the repository structure agreed in
ARCHITECTURE.md exists. No ML/API behavior is exercised here.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_DIRS = [
    "ml/configs",
    "ml/src/data",
    "ml/src/preprocessing",
    "ml/src/models",
    "ml/src/training",
    "ml/src/evaluation",
    "ml/src/explainability",
    "ml/src/inference",
    "ml/scripts",
    "ml/artifacts",
    "ml/notebooks",
    "data/raw",
    "data/processed",
    "backend/app/api",
    "backend/app/core",
    "backend/app/schemas",
    "backend/app/services",
    "backend/tests",
    "frontend",
    "tests",
    "docs",
    "phases",
    "ui-references",
]

EXPECTED_FILES = [
    "CLAUDE.md",
    "PROJECT_SPEC.md",
    "README.md",
    "data/disease_info.json",
    "data/class_mapping.json",
    "backend/app/main.py",
    "backend/requirements.txt",
    "ml/requirements.txt",
    ".gitignore",
]


def test_expected_directories_exist():
    missing = [d for d in EXPECTED_DIRS if not (ROOT / d).is_dir()]
    assert not missing, f"Missing expected directories: {missing}"


def test_expected_files_exist():
    missing = [f for f in EXPECTED_FILES if not (ROOT / f).is_file()]
    assert not missing, f"Missing expected files: {missing}"
