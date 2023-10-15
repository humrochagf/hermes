import asyncio
import logging
from datetime import datetime

import pytz
import typer

from hermes.core import startup
from hermes.health.models import BloodPressure
from hermes.health.service import HealthService
from hermes.settings import settings

app = typer.Typer()


@app.command()
def start() -> None:
    print("Starting Hermes...")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(startup())


@app.command()
def addbp(measurement: str, username: str, measured_at: str) -> None:
    print("Adding blood pressure measurement...")

    health_service = HealthService(settings.health_service_db)
    blood_pressure = BloodPressure.from_str(measurement)

    if blood_pressure:
        blood_pressure.username = username

        if measured_at:
            measured_at_dt = datetime.strptime(measured_at, "%Y-%m-%d %H:%M")
            measured_at_dt = measured_at_dt.replace(
                tzinfo=pytz.timezone(settings.timezone)
            ).astimezone(pytz.UTC)

            blood_pressure.measured_at = measured_at_dt

        health_service.save_blood_pressure(blood_pressure)

        print("Blood pressure recorded with success!")
    else:
        print("Failed to parse measurement.")
