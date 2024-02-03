from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer import Typer

from hermes import hermes
from hermes.settings import settings


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    previous_db_path = settings.blood_pressure_db
    settings.blood_pressure_db = str(tmp_path / "blood-pressure.db")

    yield TestClient(hermes.create_app())

    settings.blood_pressure_db = previous_db_path


@pytest.fixture
def cli(tmp_path: Path) -> Generator[Typer, None, None]:
    previous_db_path = settings.blood_pressure_db
    settings.blood_pressure_db = str(tmp_path / "blood-pressure.db")

    yield hermes.create_cli()

    settings.blood_pressure_db = previous_db_path
