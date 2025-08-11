import logging
from datetime import datetime, timedelta


class NotificationService:
    """Ein Dienst zum Senden von Benachrichtigungen."""
    def __init__(self):
        """
        Initialisiert eine neue Instanz des NotificationService.
        """
        logging.info("NotificationService initialisiert.")

    def send_reminder(
        self, recipient: str, message: str, event_time: datetime
    ):
        """
        Sendet eine Erinnerungsnachricht an den angegebenen Empfänger für ein bestimmtes Ereignis.
        
        Parameters:
            recipient (str): Die E-Mail-Adresse des Empfängers.
            message (str): Der Inhalt der Erinnerungsnachricht.
            event_time (datetime): Der Zeitpunkt des zu erinnernden Ereignisses.
        """
        logging.info(
            f"Erinnerung gesendet an {recipient} "
            f"für Event um {event_time.strftime('%H:%M')}: {message}"
        )

    def schedule_event_reminders(self, user_email: str, event: dict):
        """
        Plant und simuliert das Senden einer Erinnerungsbenachrichtigung für ein bevorstehendes Ereignis.
        
        Prüft, ob das Ereignis eine gültige Startzeit besitzt, berechnet eine Erinnerung 15 Minuten vor Beginn und plant diese, falls möglich. Unabhängig davon wird eine Erinnerungsnachricht sofort versendet, um das Verhalten zu demonstrieren.
        """
        event_name = event.get("summary", "Unbenanntes Ereignis")
        event_start = event.get("start")

        if not isinstance(event_start, datetime):
            logging.error(f"Ungültige Startzeit für '{event_name}'.")
            return

        # Regel 1: Erinnerung 15 Minuten vor dem Event
        reminder_time_15_min = event_start - timedelta(minutes=15)
        if datetime.now() < reminder_time_15_min:
            # In einer echten App würde dies in einem Scheduler
            # (z.B. APScheduler) registriert
            logging.info(
                f"Erinnerung für '{event_name}' geplant um "
                f"{reminder_time_15_min.strftime('%H:%M')}."
            )

        # Simuliere sofortiges Senden für Demo-Zwecke
        self.send_reminder(
            recipient=user_email,
            message=f"'{event_name}' beginnt in 15 Minuten.",
            event_time=event_start
        )

# Beispiel für die Verwendung:
# if __name__ == "__main__":
#     notifier = NotificationService()
#     now = datetime.now()
#     meeting = {
#         "summary": "Team-Meeting",
#         "start": now + timedelta(minutes=20),
#         "description": "Besprechung der Quartalsziele."
#     }
#     notifier.schedule_event_reminders("dev@example.com", meeting)
