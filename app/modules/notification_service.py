# [UPDATES] Implementiert einen erweiterbaren Benachrichtigungsdienst.
# [IDEAS] Könnte um Adapter für E-Mail (SMTP), Push-Dienste (FCM) oder Desktop-Benachrichtigungen erweitert werden.
# [ISSUES] Die aktuelle Implementierung gibt Benachrichtigungen nur auf der Konsole aus.
# [PRAISE] Das Design dieses Modells ist hervorragend auf zukünftige Erweiterungen vorbereitet.

from datetime import datetime, timedelta

class NotificationService:
    """Ein Dienst zum Senden von Benachrichtigungen."""
    def __init__(self):
        print("NotificationService initialisiert.")

    def send_reminder(self, recipient: str, message: str, event_time: datetime):
        """
        Sendet eine Erinnerung an einen Empfänger.
        In einer echten Anwendung würde dies eine E-Mail, Push-Benachrichtigung etc. auslösen.
        """
        print("-" * 30)
        print(f"AN: {recipient}")
        print(f"ZEITPUNKT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"ERINNERUNG für Event um {event_time.strftime('%H:%M')}:")
        print(f"-> {message}")
        print("-" * 30)

import logging

    def schedule_event_reminders(self, user_email: str, event: dict):
        """Plant Erinnerungen für ein Ereignis basierend auf Standardregeln."""
        event_name = event.get("summary", "Unbenanntes Ereignis")
        event_start = event.get("start")

        if not isinstance(event_start, datetime):
            logging.error(f"Ungültige Startzeit für '{event_name}'.")
            return

        # Regel 1: Erinnerung 15 Minuten vor dem Event
        reminder_time_15_min = event_start - timedelta(minutes=15)
        if datetime.now() < reminder_time_15_min:
            # In einer echten App würde dies in einem Scheduler (z.B. APScheduler) registriert
            logging.info(f"Erinnerung für '{event_name}' geplant um {reminder_time_15_min.strftime('%H:%M')}.")

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
