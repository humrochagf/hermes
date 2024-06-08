from pydantic import Field
from pydantic_settings import SettingsConfigDict
from wheke import WhekeSettings, get_settings


class HermesSettings(WhekeSettings):
    welcome_image: str | None = None
    timezone: str = "America/Montreal"

    bot_token: str = ""
    bot_allowed_accounts: list[str | int] = Field(default_factory=list)

    blood_pressure_db: str = "db/blood_pressure.json"
    blood_pressure_low: tuple[int, int] = (90, 60)
    blood_pressure_high: tuple[int, int] = (140, 90)
    blood_pressure_danger: tuple[int, int] = (180, 110)

    model_config = SettingsConfigDict(
        env_prefix="hermes_", env_file=".env", env_file_encoding="utf-8"
    )


def get_hermes_settings() -> HermesSettings:
    return get_settings(HermesSettings)
