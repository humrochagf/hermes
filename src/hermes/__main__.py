import asyncio

from rich.console import Console

from hermes import hermes

console = Console()
cli = hermes.create_cli()


@cli.command(short_help="Start Telegram bot")
def start_bot() -> None:
    bot, dispatcher = hermes.create_bot()

    console.print("Starting Hermes...")

    asyncio.run(dispatcher.start_polling(bot))
