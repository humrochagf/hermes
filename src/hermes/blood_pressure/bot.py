from pathlib import Path

import pytz
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message

from ..settings import settings
from .models import BP_RE, BloodPressure
from .service import get_blood_pressure_service

bot_router = Router()

welcome_image_id: str | None = None


@bot_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    global welcome_image_id  # noqa

    if welcome_image_id:
        await message.answer_photo(welcome_image_id)
    elif settings.welcome_image and Path(settings.welcome_image).is_file():
        welcome_image = FSInputFile(settings.welcome_image)
        response = await message.answer_photo(welcome_image)

        if response.photo:
            welcome_image_id = response.photo[0].file_id
    else:
        await message.answer("Welcome to Hermes Bot!")


@bot_router.message(F.text.regexp(BP_RE))
async def save_blood_pressure(message: Message) -> None:
    """
    Handler to record a blood pressure measurement.
    """
    with settings.get_container() as container:
        service = get_blood_pressure_service(container)

    blood_pressure = BloodPressure.from_str(message.text or "")

    if message.from_user and blood_pressure:
        blood_pressure.username = message.from_user.username

        await service.save_blood_pressure(blood_pressure)

        await message.answer("Blood pressure recorded with success!")


@bot_router.message(Command(commands=["bp"]))
async def list_blood_preassures(message: Message) -> None:
    """
    This handler lists previously saved blood pressure measurements.
    """
    with settings.get_container() as container:
        service = get_blood_pressure_service(container)

    tz = pytz.timezone(settings.timezone)
    username = ""
    measurements = []

    if message.from_user:
        username = message.from_user.username or ""

    for bp in await service.list_blood_pressures(username):
        measured_at = bp.measured_at.replace(tzinfo=pytz.UTC).astimezone(tz)

        measurements.append(
            f"{measured_at:%d/%m %H:%M} - {bp.systolic}/{bp.diastolic} {bp.heart_rate}"
        )

    await message.answer("Previous Measurements:\n{}".format("\n".join(measurements)))
