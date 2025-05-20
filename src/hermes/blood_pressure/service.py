from typing import Annotated

from fastapi import Depends
from svcs import Container
from svcs.fastapi import DepContainer
from wheke import get_service

from ..settings import settings
from .models import BloodPressure
from .repository import BloodPressureRepository


class BloodPressureService:
    repository: BloodPressureRepository

    def __init__(self, repository: BloodPressureRepository) -> None:
        self.repository = repository

    async def save_blood_pressure(self, blood_pressure: BloodPressure) -> None:
        await self.repository.save_blood_pressure(blood_pressure)

    async def list_blood_pressures(self, username: str) -> list[BloodPressure]:
        return await self.repository.list_blood_pressures(username)


def blood_pressure_service_factory(_: Container) -> BloodPressureService:
    return BloodPressureService(BloodPressureRepository(settings.blood_pressure_db))


def get_blood_pressure_service(container: Container) -> BloodPressureService:
    return get_service(container, BloodPressureService)


def _blood_pressure_service_injection(container: DepContainer) -> BloodPressureService:
    return get_blood_pressure_service(container)


BloodPressureServiceInjection = Annotated[
    BloodPressureService, Depends(_blood_pressure_service_injection)
]
