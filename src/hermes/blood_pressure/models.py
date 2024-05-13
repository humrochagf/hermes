from __future__ import annotations

import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from hermes.settings import settings
from hermes.core.helpers import utcnow

BP_RE = re.compile(
    r"(?P<systolic>\d{1,3})/(?P<diastolic>\d{1,3})"
    r"\s(?P<heart_rate>\d{1,3})\s*(?P<notes>[\w\W]*)"
)
BP_LOW_S, BP_LOW_D = settings.blood_pressure_low
BP_HIGH_S, BP_HIGH_D = settings.blood_pressure_high
BP_DANGER_S, BP_DANGER_D = settings.blood_pressure_danger


class BloodLevel(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    danger = "danger"


class BloodPressure(BaseModel):
    username: str | None = Field(default=None)
    systolic: int
    diastolic: int
    heart_rate: int
    notes: str = ""
    measured_at: datetime = Field(default_factory=utcnow)

    @property
    def level(self) -> BloodLevel:
        """
        Warning, this level parsing method is for personal information
        purposes only and does not have medical value.

        Please consult your physician for medical advice.
        """
        if self.systolic >= BP_DANGER_S or self.diastolic >= BP_DANGER_D:
            return BloodLevel.danger
        elif self.systolic >= BP_HIGH_S or self.diastolic >= BP_HIGH_D:
            return BloodLevel.high
        elif self.systolic <= BP_LOW_S or self.diastolic <= BP_LOW_D:
            return BloodLevel.low

        return BloodLevel.normal

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
