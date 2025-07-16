import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional


class TaskStatus(Enum):
    """Definiert den Status einer Aufgabe."""
    OPEN = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


class TaskPriority(Enum):
    """Definiert die Priorität einer Aufgabe."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """Stellt eine einzelne Aufgabe dar."""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.OPEN
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class TaskManager:
    """Verwaltet einen Satz von Aufgaben."""
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
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
            title=title,
            description=description,
            priority=priority,
            start_time=start_time,
            end_time=end_time
        )
        self._tasks[new_task.id] = new_task
        logging.info(f"Aufgabe hinzugefügt: '{title}' (ID: {new_task.id})")
        return new_task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Ruft eine Aufgabe anhand ihrer ID ab."""
        return self._tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Aktualisiert den Status einer Aufgabe."""
        task = self.get_task(task_id)
        if task:
            task.status = status
            logging.info(
                f"Status von Aufgabe {task_id} auf {status.name} geändert."
            )
            return True
        logging.error(f"Aufgabe mit ID {task_id} nicht gefunden.")
        return False

    def list_tasks(self) -> List[Task]:
        """Listet alle Aufgaben auf."""
        return list(self._tasks.values())

# Beispiel für die Verwendung:
# if __name__ == "__main__":
#     manager = TaskManager()
#     task1 = manager.add_task("Wochenplan-App refaktorisieren", "Code für Modularität optimieren", TaskPriority.HIGH)
#     task2 = manager.add_task("Dokumentation schreiben", priority=TaskPriority.MEDIUM)
#     manager.update_task_status(task1.id, TaskStatus.IN_PROGRESS)
#     print("\nAktuelle Aufgaben:")
#     for t in manager.list_tasks():
#         print(f"- {t.title} [{t.status.name}]")
