from pathlib import Path

from hermes.core.routes import router
from hermes.wheke import HermesPod

core_pod = HermesPod(
    "core",
    router=router,
    static_url="/core_static",
    static_path=Path(__file__).resolve().parent / "static",
)
