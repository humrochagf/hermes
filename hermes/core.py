from pathlib import Path
from enum import Enum
from typing import Any, Awaitable, Callable
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import pytz
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from hermes.health.models import BP_RE, BloodPressure
from hermes.health.service import HealthService
from hermes.settings import settings
from hermes.task.service import TaskService

router = Router()
dispatcher = Dispatcher()


class Hermes:
    _health_service: HealthService | None = None
    _task_service: TaskService | None = None

    welcome_image_id: str | None = None

    @property
    def health_service(self) -> HealthService:
        if self._health_service is None:
            self._health_service = HealthService(settings.health_service_db)

        return self._health_service

    @property
    def task_service(self) -> TaskService:
        if self._task_service is None:
            self._task_service = TaskService(settings.task_service_db)

        return self._task_service


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


@router.message(CommandStart())
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


class TaskAction(str, Enum):
    add = "add"
    list = "list"


class TaskCallback(CallbackData, prefix="task"):
    action: TaskAction
    chat_id: int


class TaskStates(StatesGroup):
    add = State()


@router.message(Command(commands=["task"]))
async def task_command_start_handler(message: Message) -> None:
    """
    Handler to manage tasks
    """
    builder = InlineKeyboardBuilder()

    for action in TaskAction:
        builder.button(
            text=action.value.title(),
            callback_data=TaskCallback(action=action, chat_id=message.chat.id),
        )

    await message.answer("Choose a task action:", reply_markup=builder.as_markup())


@router.callback_query(TaskCallback.filter(F.action == TaskAction.add))
async def task_add_callback(message: Message, state: FSMContext) -> None:
    await state.set_state(TaskStates.add)
    await message.answer("Enter your task:")


@router.message(TaskStates.add)
async def process_task(message: Message, state: FSMContext) -> None:
    if message.from_user and message.text:
        hermes.task_service.save_task(message.from_user.username, message.text)
        await message.reply("Task Recorded with Success!")

    await state.clear()


@router.callback_query(TaskCallback.filter(F.action == TaskAction.list))
async def task_list_callback(
    callback_query: CallbackQuery, callback_data: TaskCallback, bot: Bot
) -> None:
    tasks = []
    if callback_query.from_user:
        tasks = [
            f"{t.id.hex[:7]} - {t.description}"
            for t in hermes.task_service.list_tasks(callback_query.from_user.username)
        ]

    await callback_query.answer("Listing tasks")
    await bot.send_message(
        text="Tasks:\n{}".format("\n".join(tasks)),
        chat_id=callback_data.chat_id,
    )


async def startup() -> None:
    dispatcher.include_router(router)
    bot = Bot(settings.token, parse_mode="HTML")

    await dispatcher.start_polling(bot)
