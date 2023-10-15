from pathlib import Path
from typing import Any, Awaitable, Callable

import pytz
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from hermes.health.models import BP_RE, BloodPressure
from hermes.health.service import HealthService
from hermes.settings import settings

router = Router()
dispatcher = Dispatcher()


class Hermes:
    _health_service: HealthService | None = None

    welcome_image_id: str | None = None

    @property
    def health_service(self) -> HealthService:
        if self._health_service is None:
            self._health_service = HealthService(settings.health_service_db)

        return self._health_service


hermes = Hermes()


@dispatcher.message.outer_middleware  # type: ignore
async def allowed_accounts_middleware(
    handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: dict[str, Any],
) -> Any:
    user = data["event_from_user"]
    if (
        user.id in settings.allowed_accounts
        or user.username in settings.allowed_accounts
    ):
        return await handler(event, data)
    else:
        await event.answer("You are not allowed to use this bot")


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    if hermes.welcome_image_id:
        await message.answer_photo(hermes.welcome_image_id)
    elif settings.welcome_image and Path(settings.welcome_image).is_file():
        welcome_image = FSInputFile(settings.welcome_image)
        response = await message.answer_photo(welcome_image)

        if response.photo:
            hermes.welcome_image_id = response.photo[0].file_id
    else:
        await message.answer("Welcome to Hermes Bot!")


@router.message(F.text.regexp(BP_RE))
async def save_blood_pressure(message: Message) -> None:
    """
    Handler to record a blood pressure measurement.
    """
    blood_pressure = BloodPressure.from_str(message.text or "")

    if message.from_user and blood_pressure:
        blood_pressure.username = message.from_user.username

        hermes.health_service.save_blood_pressure(blood_pressure)

        await message.answer("Blood pressure recorded with success!")


@router.message(Command(commands=["bp"]))
async def list_blood_preassures(message: Message) -> None:
    """
    This handler lists previously saved blood pressure measurements.
    """
    tz = pytz.timezone(settings.timezone)
    username = ""
    measurements = []

    if message.from_user:
        username = message.from_user.username or ""

    for bp in hermes.health_service.list_blood_pressures(username):
        measured_at = bp.measured_at.replace(tzinfo=pytz.UTC).astimezone(tz)

        measurements.append(
            f"{measured_at:%d/%m %H:%M} - {bp.systolic}/{bp.diastolic} {bp.heart_rate}"
        )

    await message.answer("Previous Measurements:\n{}".format("\n".join(measurements)))


async def startup() -> None:
    dispatcher.include_router(router)
    bot = Bot(settings.token, parse_mode="HTML")

    await dispatcher.start_polling(bot)
