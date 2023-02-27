from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message

from hermes.settings import Settings

settings = Settings()
router = Router()


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    if message.from_user:
        await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")
    else:
        await message.answer("Hello!")


@router.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward received message back to the sender

    By default, message handler will handle all message
    types (like text, photo, sticker and etc.)
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def startup() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(settings.token, parse_mode="HTML")

    await dp.start_polling(bot)
