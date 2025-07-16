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
        """
        Initialisiert eine neue Instanz des TaskManager.
        """
        logging.info("TaskManager initialisiert.")

    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Task:
        """
        Erstellt eine neue Aufgabe mit Titel, optionaler Beschreibung, Priorität sowie optionalem Start- und Endzeitpunkt und speichert sie in der Datenbank.
        
        Parameters:
            title (str): Titel der Aufgabe. Darf nicht leer sein.
            description (Optional[str]): Optionale Beschreibung der Aufgabe.
            priority (TaskPriority): Priorität der Aufgabe (Standard: MEDIUM).
            start_time (Optional[datetime]): Optionaler Startzeitpunkt.
            end_time (Optional[datetime]): Optionaler Endzeitpunkt.
        
        Returns:
            Task: Das erstellte Aufgabenobjekt.
        
        Raises:
            ValueError: Wenn der Titel leer ist.
        """
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
        """
        Gibt eine Aufgabe mit der angegebenen ID zurück, falls vorhanden.
        
        Parameters:
            task_id (str): Die eindeutige ID der Aufgabe.
        
        Returns:
            Optional[Task]: Die gefundene Aufgabe oder None, wenn keine Aufgabe mit dieser ID existiert.
        """
        return Task.query.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        Setzt den Status einer Aufgabe anhand ihrer ID auf den angegebenen Wert.
        
        Gibt True zurück, wenn die Aufgabe gefunden und aktualisiert wurde, andernfalls False.
        """
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
        """
        Gibt eine Liste aller Aufgaben im System zurück.
        
        Returns:
            List[Task]: Alle gespeicherten Aufgaben als Liste von Task-Objekten.
        """
        return Task.query.all()
