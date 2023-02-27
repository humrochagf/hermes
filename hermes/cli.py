import asyncio
import logging

import typer

from hermes.core import startup

app = typer.Typer()


@app.command()
def start():
    print("Starting Hermes...")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(startup())
