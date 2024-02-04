from datetime import datetime
from pathlib import Path
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from hermes.blood_pressure.service import (
    BloodPressureService,
    get_blood_pressure_service,
)
from hermes.settings import settings

tz = pytz.timezone(settings.timezone)
router = APIRouter(tags=["core"], include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


def to_local_time(value: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return value.replace(tzinfo=pytz.UTC).astimezone(tz).strftime(fmt)


templates.env.filters["to_local_time"] = to_local_time


@router.get("/")
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            "page_title": "Home",
            "accounts": settings.bot_allowed_accounts,
        },
    )


@router.get("/{account}")
async def account_metrics(
    service: Annotated[BloodPressureService, Depends(get_blood_pressure_service)],
    request: Request,
    account: str,
) -> HTMLResponse:
    blood_pressures = await service.list_blood_pressures(account)

    return templates.TemplateResponse(
        name="account_metrics.html",
        request=request,
        context={
            "page_title": f"Metrics: {account}",
            "blood_pressures": blood_pressures,
        },
    )
