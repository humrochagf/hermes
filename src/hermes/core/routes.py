from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

router = APIRouter(tags=["core"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


@router.get("/", include_in_schema=False)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")
