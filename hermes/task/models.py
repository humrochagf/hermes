from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str | None
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)
