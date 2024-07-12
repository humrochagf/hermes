from wheke import ServiceConfig

from hermes.blood_pressure.bot import bot_router
from hermes.blood_pressure.cli import cli
from hermes.blood_pressure.service import (
    BloodPressureService,
    blood_pressure_service_factory,
)
from hermes.wheke import HermesPod

blood_pressure_pod = HermesPod(
    "blood-pressure",
    services=[ServiceConfig(BloodPressureService, blood_pressure_service_factory)],
    cli=cli,
    bot_router=bot_router,
)
