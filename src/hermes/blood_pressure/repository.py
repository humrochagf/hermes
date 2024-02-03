from collections.abc import Callable
from functools import partial

from aiotinydb.database import AIOTinyDB
from pydantic_core import to_jsonable_python
from tinydb import Query

from hermes.blood_pressure.models import BloodPressure


class BloodPressureRepository:
    """
    Blood Pressure Repository
    """

    db_factory: Callable[[], AIOTinyDB]

    def __init__(self, connection_string: str) -> None:
        self.db_factory = partial(AIOTinyDB, connection_string)

    async def save_blood_pressure(self, blood_pressure: BloodPressure) -> None:
        async with self.db_factory() as db:
            db.insert(to_jsonable_python(blood_pressure))

    async def list_blood_pressures(self, username: str) -> list[BloodPressure]:
        async with self.db_factory() as db:
            bp_list = (
                BloodPressure(**d) for d in db.search(Query().username == username)
            )

        return sorted(bp_list, key=lambda k: k.measured_at)
