"""Phase 12 sanity tests: deployment configuration/documentation exists
and is internally consistent. Mirrors tests/test_repo_structure.py's
approach -- no ML/API behavior is exercised here, only static structure.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_FILES = [
    "backend/Dockerfile",
    "frontend/Dockerfile",
    "frontend/.dockerignore",
    "docker-compose.yml",
    ".dockerignore",
    "deploy/nginx.conf.example",
    "docs/DEPLOYMENT.md",
]


def test_expected_deployment_files_exist():
    missing = [f for f in EXPECTED_FILES if not (ROOT / f).is_file()]
    assert not missing, f"Missing expected deployment files: {missing}"


def test_backend_dockerfile_runs_production_asgi_command():
    text = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
    assert "uvicorn backend.app.main:app" in text
    assert "--host 0.0.0.0" in text


def test_backend_dockerfile_does_not_bake_in_artifacts_or_data():
    """Model artifacts/data are git-ignored binaries -- docs/DEPLOYMENT.md
    documents them as bind-mounted volumes at runtime, not COPYed into the
    image (see docker-compose.yml)."""
    text = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY ml/artifacts" not in text
    assert "COPY data" not in text


def test_frontend_dockerfile_accepts_api_base_url_as_build_arg():
    text = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
    assert "ARG NEXT_PUBLIC_API_BASE_URL" in text
    assert "ENV NEXT_PUBLIC_API_BASE_URL" in text


def test_next_config_uses_standalone_output_for_docker():
    text = (ROOT / "frontend" / "next.config.ts").read_text(encoding="utf-8")
    assert re.search(r'output:\s*"standalone"', text)


def test_docker_compose_defines_both_services_with_health_relevant_wiring():
    text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert re.search(r"^\s*backend:", text, re.MULTILINE)
    assert re.search(r"^\s*frontend:", text, re.MULTILINE)
    # Model artifacts/data mounted read-only, never baked into the image.
    assert "ml/artifacts:/app/ml/artifacts:ro" in text
    assert "./data:/app/data:ro" in text


def test_no_env_files_are_committed():
    """CLAUDE.md rule 6 / DEPLOYMENT_SPEC.md 'Security': no secrets in
    Git. Real .env files may exist on disk for local development, but
    git must be configured to ignore every one of them; only the
    .example templates are meant to be tracked."""
    import subprocess

    real_env_files = [
        p
        for p in ROOT.glob("**/.env*")
        if ".git" not in p.parts
        and "node_modules" not in p.parts
        and not p.name.endswith(".example")
    ]
    for path in real_env_files:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", str(path)],
            cwd=ROOT,
            check=False,
        )
        assert result.returncode == 0, f"{path} is not covered by .gitignore"


def test_deployment_doc_documents_model_artifact_strategy_and_health_check():
    text = (ROOT / "docs" / "DEPLOYMENT.md").read_text(encoding="utf-8")
    assert "Model Artifact Strategy" in text or "Model artifact strategy" in text
    assert "/health" in text
    assert "Hostinger" in text


def test_evaluation_metrics_file_is_valid_json_with_required_keys():
    """The README cites accuracy/F1 from this file; guard against it
    silently going stale or malformed (CLAUDE.md rule 5: never invent
    metrics -- they must come from this report)."""
    metrics_path = ROOT / "ml" / "artifacts" / "evaluation" / "metrics.json"
    if not metrics_path.is_file():
        return  # optional artifact; ModelService/model-info handle its absence
    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    for key in ("accuracy", "macro", "weighted", "num_classes"):
        assert key in data
