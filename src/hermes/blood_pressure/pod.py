from wheke import ServiceConfig

from ..wheke import HermesPod
from .bot import bot_router
from .cli import cli
from .service import (
    BloodPressureService,
    blood_pressure_service_factory,
)

blood_pressure_pod = HermesPod(
    "blood-pressure",
    services=[ServiceConfig(BloodPressureService, blood_pressure_service_factory)],
    cli=cli,
    bot_router=bot_router,
)
