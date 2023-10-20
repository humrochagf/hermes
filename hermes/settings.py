from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str = ""
    allowed_accounts: list[str | int] = []
    timezone: str = "America/Montreal"
    welcome_image: str | None = None
    health_service_db: str = "db/health_data.json"
    task_service_db: str = "db/task_data.json"

    model_config = SettingsConfigDict(
        env_prefix="hermes_", env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
