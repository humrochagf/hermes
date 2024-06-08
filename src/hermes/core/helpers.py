from datetime import datetime

import pytz

from hermes.settings import get_hermes_settings


def to_local_time(value: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    tz = pytz.timezone(get_hermes_settings().timezone)

    return value.replace(tzinfo=pytz.UTC).astimezone(tz).strftime(fmt)


def utcnow() -> datetime:
    return datetime.now(pytz.UTC)
