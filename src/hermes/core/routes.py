from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from hermes.blood_pressure.helpers import level_to_color
from hermes.blood_pressure.service import (
    BloodPressureService,
    get_blood_pressure_service,
)
from hermes.core.helpers import to_local_time
from hermes.settings import settings

router = APIRouter(tags=["core"], include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

templates.env.filters["to_local_time"] = to_local_time
templates.env.filters["level_to_color"] = level_to_color


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
