from pathlib import Path

from hermes.health.models import BloodPressure
from hermes.health.service import HealthService


def test_parse_blood_pressure() -> None:
    blood_pressure = BloodPressure.from_str("120/80 60")

    assert blood_pressure
    assert blood_pressure.systolic == 120
    assert blood_pressure.diastolic == 80
    assert blood_pressure.heart_rate == 60

    blood_pressure = BloodPressure.from_str("140/90 70 Some notes")

    assert blood_pressure
    assert blood_pressure.systolic == 140
    assert blood_pressure.diastolic == 90
    assert blood_pressure.heart_rate == 70
    assert blood_pressure.notes == "Some notes"

    blood_pressure = BloodPressure.from_str("110/70 80\nMulti line\nnotes\n")

    assert blood_pressure
    assert blood_pressure.systolic == 110
    assert blood_pressure.diastolic == 70
    assert blood_pressure.heart_rate == 80
    assert blood_pressure.notes == "Multi line\nnotes"


def test_health_service(tmp_path: Path) -> None:
    service = HealthService(str(tmp_path / "testdb.json"))
    blood_pressure = BloodPressure.from_str("120/80 65")

    assert blood_pressure

    blood_pressure.username = "testuser"

    service.save_blood_pressure(blood_pressure)

    blood_pressures = service.list_blood_pressures("testuser")

    assert len(blood_pressures) == 1

    blood_pressures = service.list_blood_pressures("otheruser")

    assert len(blood_pressures) == 0
