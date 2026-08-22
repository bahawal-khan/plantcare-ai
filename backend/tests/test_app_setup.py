"""Phase 01 sanity tests: the backend app scaffold imports and is
configured correctly. Endpoint behavior is tested starting Phase 08.
"""

from fastapi import FastAPI

from app.core.config import settings
from app.main import app


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)


def test_app_uses_configured_name_and_version():
    assert app.title == settings.app_name
    assert app.version == settings.app_version


def test_cors_origins_list_parses_from_csv_string():
    assert settings.cors_origins_list == ["http://localhost:3000"]
