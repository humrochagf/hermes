import asyncio
from datetime import datetime

import pytz
import typer
from rich.console import Console
from typer import Context
from wheke import get_container

from ..settings import settings
from .models import BloodPressure
from .service import get_blood_pressure_service

cli = typer.Typer(short_help="Blood Pressure commands")
console = Console()


@cli.command()
def add(ctx: Context, measurement: str, username: str, measured_at: str) -> None:
    console.print("Adding blood pressure measurement...")
    container = get_container(ctx)

    health_service = get_blood_pressure_service(container)
    blood_pressure = BloodPressure.from_str(measurement)

    if blood_pressure:
        blood_pressure.username = username

        if measured_at:
            measured_at_dt = (
                datetime.strptime(measured_at, "%Y-%m-%d %H:%M")
                .replace(tzinfo=pytz.timezone(settings.timezone))
                .astimezone(pytz.UTC)
            )

            blood_pressure.measured_at = measured_at_dt

        asyncio.run(health_service.save_blood_pressure(blood_pressure))

        console.print("Blood pressure recorded with success!")
    else:
        console.print("Failed to parse measurement.")

        raise typer.Abort()
