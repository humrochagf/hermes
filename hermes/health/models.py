from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field

BP_RE = re.compile(
    r"(?P<systolic>\d{1,3})/(?P<diastolic>\d{1,3})"
    r"\s(?P<heart_rate>\d{1,3})\s*(?P<notes>[\w\W]*)"
)


class BloodPressure(BaseModel):
    username: str | None = Field(default=None)
    systolic: int
    diastolic: int
    heart_rate: int
    notes: str = ""
    measured_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_str(cls, value: str) -> BloodPressure | None:
        if match := BP_RE.match(value):
            groupdict = match.groupdict()

            return BloodPressure(
                systolic=int(groupdict["systolic"]),
                diastolic=int(groupdict["diastolic"]),
                heart_rate=int(groupdict["heart_rate"]),
                notes=groupdict.get("notes", "").strip(),
            )

        return None
