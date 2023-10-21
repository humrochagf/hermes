from datetime import datetime
from uuid import UUID

from pydantic_core import to_jsonable_python
from tinydb import Query, TinyDB, where

from .models import Task


class TaskService:
    db: TinyDB

    def __init__(self, connection_string: str) -> None:
        self.db = TinyDB(connection_string, create_dirs=True, encoding="utf-8")

    def list_tasks(self, username: str | None) -> list[Task]:
        tasks = (
            Task(**d)
            for d in self.db.search(
                Query().fragment({"username": username, "completed_at": None})
            )
        )

        return sorted(tasks, key=lambda k: k.created_at)

    def create_task(self, username: str | None, description: str) -> None:
        task = Task(username=username, description=description)
        self.db.insert(to_jsonable_python(task))

    def retrieve_task(self, id: UUID) -> Task:
        return Task(**self.db.search(where("id") == str(id))[0])

    def update_task(self, id: UUID, description: str) -> None:
        self.db.update({"description": description}, where("id") == str(id))

    def delete_task(self, id: UUID) -> None:
        self.db.remove(where("id") == str(id))

    def complete_task(self, id: UUID) -> None:
        task = self.retrieve_task(id)
        task.completed_at = datetime.utcnow()

        self.db.update(to_jsonable_python(task), where("id") == str(id))
