from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable
from uuid import UUID

import pytz
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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


class TaskActionCallback(CallbackData, prefix="ta"):
    chat_id: int
    action: TaskAction


class TaskSelectionCallback(CallbackData, prefix="ts"):
    chat_id: int
    task_id: UUID


class SelectedTaskAction(str, Enum):
    complete = "complete"
    edit = "edit"
    delete = "delete"


class SelectedTaskActionCallback(CallbackData, prefix="sta"):
    chat_id: int
    task_id: UUID
    action: SelectedTaskAction


class TaskStates(StatesGroup):
    add = State()
    edit = State()


@router.message(Command(commands=["task"]))
async def task_command_start_handler(message: Message) -> None:
    """
    Handler to manage tasks
    """
    builder = InlineKeyboardBuilder()

    for action in TaskAction:
        builder.button(
            text=action.value.title(),
            callback_data=TaskActionCallback(action=action, chat_id=message.chat.id),
        )

    await message.answer("Choose a task action:", reply_markup=builder.as_markup())


@router.callback_query(TaskActionCallback.filter(F.action == TaskAction.add))
async def task_add_callback(
    callback_query: CallbackQuery,
    callback_data: TaskActionCallback,
    bot: Bot,
    state: FSMContext,
) -> None:
    await callback_query.answer("Adding a new task")

    await state.set_state(TaskStates.add)

    await bot.send_message(text="Enter your task:", chat_id=callback_data.chat_id)


@router.message(TaskStates.add)
async def add_task(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if message.from_user and text:
        hermes.task_service.create_task(message.from_user.username, text)
        await message.reply("Task Recorded with Success!")
    else:
        await message.reply("Action canceled")

    await state.clear()


@router.callback_query(TaskActionCallback.filter(F.action == TaskAction.list))
async def task_list_callback(
    callback_query: CallbackQuery, callback_data: TaskActionCallback, bot: Bot
) -> None:
    await callback_query.answer("Listing Tasks")

    builder = InlineKeyboardBuilder()

    if callback_query.from_user:
        for task in hermes.task_service.list_tasks(callback_query.from_user.username):
            builder.button(
                text=task.description,
                callback_data=TaskSelectionCallback(
                    chat_id=callback_data.chat_id, task_id=task.id
                ),
            )

    builder.adjust(1)

    await bot.send_message(
        text="Tasks:",
        chat_id=callback_data.chat_id,
        reply_markup=builder.as_markup(),
    )


@router.callback_query(TaskSelectionCallback.filter())
async def task_selection_callback(
    callback_query: CallbackQuery, callback_data: TaskSelectionCallback, bot: Bot
) -> None:
    await callback_query.answer("Task Selected")

    builder = InlineKeyboardBuilder()
    task = hermes.task_service.retrieve_task(callback_data.task_id)

    for action in SelectedTaskAction:
        builder.button(
            text=action.value.title(),
            callback_data=SelectedTaskActionCallback(
                chat_id=callback_data.chat_id, task_id=task.id, action=action
            ),
        )

    await bot.send_message(
        text=task.description,
        chat_id=callback_data.chat_id,
        reply_markup=builder.as_markup(),
    )


@router.callback_query(
    SelectedTaskActionCallback.filter(F.action == SelectedTaskAction.complete)
)
async def task_complete_callback(
    callback_query: CallbackQuery,
    callback_data: TaskSelectionCallback,
    bot: Bot,
) -> None:
    await callback_query.answer("Completing a task")

    hermes.task_service.complete_task(callback_data.task_id)

    await bot.send_message(
        text="Task marked as completed!", chat_id=callback_data.chat_id
    )


@router.callback_query(
    SelectedTaskActionCallback.filter(F.action == SelectedTaskAction.edit)
)
async def task_edit_callback(
    callback_query: CallbackQuery,
    callback_data: TaskSelectionCallback,
    bot: Bot,
    state: FSMContext,
) -> None:
    await callback_query.answer("Editing a task")

    await state.set_state(TaskStates.edit)
    await state.update_data(task_id=callback_data.task_id)

    await bot.send_message(
        text="Enter a new text for this task:", chat_id=callback_data.chat_id
    )


@router.message(TaskStates.edit)
async def edit_task(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if text:
        data = await state.get_data()
        hermes.task_service.update_task(data["task_id"], text)
        await message.reply("Task Updated with Success!")
    else:
        await message.reply("Action canceled")

    await state.clear()


@router.callback_query(
    SelectedTaskActionCallback.filter(F.action == SelectedTaskAction.delete)
)
async def task_delete_callback(
    callback_query: CallbackQuery,
    callback_data: TaskSelectionCallback,
    bot: Bot,
) -> None:
    await callback_query.answer("Deleting a task")

    hermes.task_service.delete_task(callback_data.task_id)

    await bot.send_message(text="Task got deleted!", chat_id=callback_data.chat_id)


async def startup() -> None:
    dispatcher.include_router(router)
    bot = Bot(settings.token, parse_mode="HTML")

    await dispatcher.start_polling(bot)
