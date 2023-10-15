from pydantic_core import to_jsonable_python
from tinydb import Query, TinyDB

from hermes.health.models import BloodPressure


class HealthService:
    db: TinyDB

    def __init__(self, connection_string: str) -> None:
        self.db = TinyDB(connection_string, create_dirs=True, encoding="utf-8")

    def save_blood_pressure(self, blood_pressure: BloodPressure) -> None:
        self.db.insert(to_jsonable_python(blood_pressure))

    def list_blood_pressures(self, username: str) -> list[BloodPressure]:
        bp_list = (
            BloodPressure(**d) for d in self.db.search(Query().username == username)
        )

        return sorted(bp_list, key=lambda k: k.measured_at)
