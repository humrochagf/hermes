from __future__ import annotations

import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from hermes.core.helpers import utcnow
from hermes.settings import get_hermes_settings

BP_RE = re.compile(
    r"(?P<systolic>\d{1,3})/(?P<diastolic>\d{1,3})"
    r"\s(?P<heart_rate>\d{1,3})\s*(?P<notes>[\w\W]*)"
)


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
        bp_danger_s, bp_danger_d = get_hermes_settings().blood_pressure_danger
        bp_high_s, bp_high_d = get_hermes_settings().blood_pressure_danger
        bp_low_s, bp_low_d = get_hermes_settings().blood_pressure_danger

        if self.systolic >= bp_danger_s or self.diastolic >= bp_danger_d:
            return BloodLevel.danger
        elif self.systolic >= bp_high_s or self.diastolic >= bp_high_d:
            return BloodLevel.high
        elif self.systolic <= bp_low_s or self.diastolic <= bp_low_d:
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
