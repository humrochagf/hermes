from wheke import get_service

from hermes.blood_pressure.models import BloodPressure
from hermes.blood_pressure.repository import BloodPressureRepository
from hermes.settings import get_hermes_settings


class BloodPressureService:
    repository: BloodPressureRepository

    def __init__(self, repository: BloodPressureRepository) -> None:
        self.repository = repository

    async def save_blood_pressure(self, blood_pressure: BloodPressure) -> None:
        await self.repository.save_blood_pressure(blood_pressure)

    async def list_blood_pressures(self, username: str) -> list[BloodPressure]:
        return await self.repository.list_blood_pressures(username)


def blood_pressure_service_factory() -> BloodPressureService:
    return BloodPressureService(
        BloodPressureRepository(get_hermes_settings().blood_pressure_db)
    )


def get_blood_pressure_service() -> BloodPressureService:
    return get_service(BloodPressureService)
