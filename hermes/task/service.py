from pydantic_core import to_jsonable_python
from tinydb import TinyDB, Query

from .models import Task


class TaskService:
    db: TinyDB

    def __init__(self, connection_string: str) -> None:
        self.db = TinyDB(connection_string, create_dirs=True, encoding="utf-8")

    def save_task(self, username: str | None, description: str) -> None:
        task = Task(username=username, description=description)
        self.db.insert(to_jsonable_python(task))

    def list_tasks(self, username: str | None) -> list[Task]:
        tasks = (Task(**d) for d in self.db.search(Query().username == username))

        return sorted(tasks, key=lambda k: k.created_at)
