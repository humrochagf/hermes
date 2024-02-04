from datetime import datetime

import pytz

from hermes.settings import settings

tz = pytz.timezone(settings.timezone)


def to_local_time(value: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return value.replace(tzinfo=pytz.UTC).astimezone(tz).strftime(fmt)
