# ============================================================
# Task Manager Module
# ============================================================

import logging
from datetime import datetime
from typing import List, Optional

from app.models import Task, TaskPriority, TaskStatus
from app import db


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
        due_date: Optional[datetime] = None,
    ) -> Task:
        """
        Erstellt eine neue Aufgabe mit Titel, optionaler Beschreibung, Priorität sowie optionalem Fälligkeitsdatum und speichert sie in der Datenbank.

        Parameters:
            title (str): Titel der Aufgabe. Darf nicht leer sein.
            description (Optional[str]): Optionale Beschreibung der Aufgabe.
            priority (TaskPriority): Priorität der Aufgabe (Standard: MEDIUM).
            due_date (Optional[datetime]): Optionales Fälligkeitsdatum.

        Returns:
            Task: Das erstellte Aufgabenobjekt.

        Raises:
            ValueError: Wenn der Titel leer ist.
        """
        if not title:
            raise ValueError("Der Titel darf nicht leer sein.")

        max_order = db.session.query(db.func.max(Task.order)).scalar() or 0
        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            order=max_order + 1,
        )
        db.session.add(new_task)
        db.session.commit()
        logging.info(f"Aufgabe hinzugefügt: '{title}' (ID: {new_task.id})")
        return new_task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Gibt eine Aufgabe mit der angegebenen ID zurück, falls vorhanden.
        
        Parameters:
            task_id (int): Die eindeutige ID der Aufgabe.
        
        Returns:
            Optional[Task]: Die gefundene Aufgabe oder None, wenn keine Aufgabe mit dieser ID existiert.
        """
        return Task.query.get(task_id)

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """
        Setzt den Status einer Aufgabe anhand ihrer ID auf den angegebenen Wert.

        Gibt True zurück, wenn die Aufgabe gefunden und aktualisiert wurde, andernfalls False.
        """
        task = self.get_task(task_id)
        if task:
            task.status = status
            db.session.commit()
            logging.info(
                f"Status von Aufgabe {task_id} auf {status.name} geändert."
            )
            return True
        logging.error(f"Aufgabe mit ID {task_id} nicht gefunden.")
        return False

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        due_date: Optional[datetime] = None,
    ) -> bool:
        """Aktualisiert eine bestehende Aufgabe.

        Übergebene Parameter überschreiben die vorhandenen Werte. Nicht
        angegebene Felder bleiben unverändert. Gibt ``True`` zurück, wenn die
        Aufgabe gefunden und gespeichert wurde, andernfalls ``False``.
        """
        task = self.get_task(task_id)
        if not task:
            logging.error(f"Aufgabe mit ID {task_id} nicht gefunden.")
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        db.session.commit()
        logging.info(f"Aufgabe {task_id} aktualisiert.")
        return True

    def delete_task(self, task_id: int) -> bool:
        """Löscht eine Aufgabe anhand ihrer ID.

        Rückgabewert ist ``True``, wenn die Aufgabe existierte und entfernt
        wurde, sonst ``False``.
        """
        task = self.get_task(task_id)
        if not task:
            logging.error(f"Aufgabe mit ID {task_id} nicht gefunden.")
            return False
        db.session.delete(task)
        db.session.commit()
        logging.info(f"Aufgabe {task_id} gelöscht.")
        return True

    def list_tasks(self) -> List[Task]:
        """
        Gibt eine Liste aller Aufgaben im System zurück.

        Returns:
            List[Task]: Alle gespeicherten Aufgaben als Liste von Task-Objekten.
        """
        return Task.query.order_by(Task.order).all()

    def reorder_task(self, task_id: int, new_position: int) -> bool:
        """Verschiebt eine Aufgabe an eine neue Position (0-basiert von der UI)."""
        task = self.get_task(task_id)
        if not task:
            logging.warning(f"Versuch, eine nicht existierende Aufgabe zu verschieben: {task_id}")
            return False
        if new_position < 0:
            logging.error(f"Ungültige Position: {new_position} (muss >= 0 sein)")
            return False

        total = Task.query.count()
        if total == 0:
            return False

        new_order = min(new_position + 1, total)  # 1-basiert
        old_order = task.order
        if old_order == new_order:
            return True

        if new_order > old_order:
            # Nach unten verschieben: betroffene um 1 nach oben ziehen
            affected_tasks = Task.query.filter(
                Task.order > old_order, Task.order <= new_order
            ).all()
            for t in affected_tasks:
                t.order -= 1
        else:
            # Nach oben verschieben: betroffene um 1 nach unten schieben
            affected_tasks = Task.query.filter(
                Task.order >= new_order, Task.order < old_order
            ).all()
            for t in affected_tasks:
                t.order += 1

        task.order = new_order
        db.session.commit()
        logging.info(f"Aufgabe {task_id} wurde an Position {new_position} verschoben.")
        return True
        
