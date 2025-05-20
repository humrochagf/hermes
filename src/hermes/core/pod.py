from pathlib import Path

from ..wheke import HermesPod
from .routes import router

core_pod = HermesPod(
    "core",
    router=router,
    static_url="/core_static",
    static_path=Path(__file__).resolve().parent / "static",
)
