from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from typer import Typer

from .blood_pressure.pod import blood_pressure_pod
from .core.pod import core_pod
from .wheke import Hermes


def build_hermes() -> Hermes:
    hermes = Hermes()
    hermes.add_pod(core_pod)
    hermes.add_pod(blood_pressure_pod)

    return hermes


def build_cli() -> Typer:
    return build_hermes().create_cli()


def build_bot() -> tuple[Bot, Dispatcher]:
    return build_hermes().create_bot()


def build_app() -> FastAPI:
    return build_hermes().create_app()
