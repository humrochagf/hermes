from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    welcome_image: str | None = None
    timezone: str = "America/Montreal"

    bot_token: str = ""
    bot_allowed_accounts: list[str | int] = []

    blood_pressure_db: str = "db/blood_pressure.json"
    blood_pressure_low: tuple[int, int] = (90, 60)
    blood_pressure_high: tuple[int, int] = (140, 90)
    blood_pressure_danger: tuple[int, int] = (180, 110)

    model_config = SettingsConfigDict(
        env_prefix="hermes_", env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
