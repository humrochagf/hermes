from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer import Typer

from hermes import build_app, build_cli
from hermes.settings import settings


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient]:
    settings.blood_pressure_db = str(tmp_path / "blood-pressure.db")

    with TestClient(build_app()) as client:
        yield client


@pytest.fixture
def cli(tmp_path: Path) -> Typer:
    settings.blood_pressure_db = str(tmp_path / "blood-pressure.db")

    return build_cli()
