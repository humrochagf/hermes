import asyncio
from datetime import datetime

import pytz
import typer
from rich.console import Console

from hermes.blood_pressure.models import BloodPressure
from hermes.blood_pressure.service import get_blood_pressure_service
from hermes.settings import settings

cli = typer.Typer(short_help="Blood Pressure commands")
console = Console()


@cli.command()
def add(measurement: str, username: str, measured_at: str) -> None:
    console.print("Adding blood pressure measurement...")

    health_service = get_blood_pressure_service()
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
