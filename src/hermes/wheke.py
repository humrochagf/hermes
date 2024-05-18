from pathlib import Path
from typing import Any, Awaitable, Callable

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from fastapi import APIRouter
from typer import Typer
from wheke import Pod, ServiceList, Wheke

from hermes.settings import settings

dispatcher = Dispatcher()


@dispatcher.message.outer_middleware  # type: ignore
async def allowed_accounts_middleware(
    handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: dict[str, Any],
) -> Any:
    user = data["event_from_user"]

    if (
        user.id in settings.bot_allowed_accounts
        or user.username in settings.bot_allowed_accounts
    ):
        return await handler(event, data)
    else:
        await event.answer("You are not allowed to use this bot")


class HermesPod(Pod):
    bot_router: Router | None

    def __init__(
        self,
        name: str,
        *,
        router: APIRouter | None = None,
        static_url: str | None = None,
        static_path: str | Path | None = None,
        services: ServiceList | None = None,
        cli: Typer | None = None,
        bot_router: Router | None = None,
    ) -> None:
        self.bot_router = bot_router

        super().__init__(
            name,
            router=router,
            static_url=static_url,
            static_path=static_path,
            services=services,
            cli=cli,
        )


class Hermes(Wheke):
    """
    Entry point for Hermes.
    """

    def create_bot(self) -> tuple[Bot, Dispatcher]:
        """
        Create a Telegram bot with all plugged pods.
        """
        bot = Bot(settings.bot_token, parse_mode="HTML")

        for pod in self.pods:
            if isinstance(pod, HermesPod) and pod.bot_router:
                dispatcher.include_router(pod.bot_router)

        return bot, dispatcher
