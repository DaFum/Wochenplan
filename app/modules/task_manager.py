import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from app.models import Task
from app import db


class TaskStatus(Enum):
    """Definiert den Status einer Aufgabe."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskPriority(Enum):
    """Definiert die Priorität einer Aufgabe."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskManager:
    """Verwaltet einen Satz von Aufgaben."""
    def __init__(self):
        logging.info("TaskManager initialisiert.")

    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Task:
        """Fügt eine neue Aufgabe hinzu und gibt sie zurück."""
        if not title:
            raise ValueError("Der Titel darf nicht leer sein.")

        new_task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority.name,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(new_task)
        db.session.commit()
        logging.info(f"Aufgabe hinzugefügt: '{title}' (ID: {new_task.id})")
        return new_task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Ruft eine Aufgabe anhand ihrer ID ab."""
        return Task.query.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Aktualisiert den Status einer Aufgabe."""
        task = self.get_task(task_id)
        if task:
            task.status = status.name
            db.session.commit()
            logging.info(
                f"Status von Aufgabe {task_id} auf {status.name} geändert."
            )
            return True
        logging.error(f"Aufgabe mit ID {task_id} nicht gefunden.")
        return False

    def list_tasks(self) -> List[Task]:
        """Listet alle Aufgaben auf."""
        return Task.query.all()
