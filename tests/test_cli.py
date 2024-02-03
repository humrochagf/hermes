from datetime import UTC, datetime

from typer import Typer
from typer.testing import CliRunner

runner = CliRunner()


def test_bp_add(cli: Typer) -> None:
    time_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")

    result = runner.invoke(
        cli,
        [
            "blood-pressure",
            "add",
            "120/80 65",
            "testuser",
            time_str,
        ],
    )

    assert result.exit_code == 0
