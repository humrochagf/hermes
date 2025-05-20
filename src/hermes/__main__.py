import asyncio

from rich.console import Console

from . import build_bot, build_cli

console = Console()
cli = build_cli()


@cli.command(short_help="Start Telegram bot")
def start_bot() -> None:
    bot, dispatcher = build_bot()

    console.print("Starting Hermes...")

    asyncio.run(dispatcher.start_polling(bot))
