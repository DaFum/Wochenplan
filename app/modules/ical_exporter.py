import logging
from typing import Any, Dict, List, Optional

from ics import Calendar, Event


class ICalExporter:
    """Exportiert eine Liste von Ereignissen in eine .ics-Kalenderdatei."""
    def __init__(self):
        """
        Initialisiert eine neue Instanz des ICalExporter.
        """
        logging.info("ICalExporter initialisiert.")

    def export_to_memory(self, events: List[Dict[str, Any]]) -> Optional[str]:
        """
        Exportiert eine Liste von Ereignis-Wörterbüchern als iCalendar-String.
        
        Verarbeitet die übergebene Liste von Ereignissen, erstellt daraus einen iCal-Kalender und gibt diesen als String zurück. Ungültige Ereignisse ohne die erforderlichen Schlüssel ("summary", "start", "end") werden übersprungen.
        
        Parameter:
            events (List[Dict[str, Any]]): Liste von Ereignis-Wörterbüchern mit mindestens den Schlüsseln "summary", "start" und "end".
        
        Returns:
            Optional[str]: Der iCalendar-String, oder None, wenn keine gültigen Ereignisse exportiert werden konnten.
        """
        cal = Calendar()
        for event_data in events:
            if not all(k in event_data for k in ["summary", "start", "end"]):
                print(f"Warnung: Überspringe ungültiges Ereignis: {event_data}")
                continue

            event = Event()
            event.name = event_data["summary"]
            event.begin = event_data["start"]
            event.end = event_data["end"]
            if "description" in event_data:
                event.description = event_data["description"]
            
            # Add UID and DTSTAMP if provided
            event.uid = event_data.get("uid") or f"event-{id(event_data)}@wochenplan"
            if "dtstamp" in event_data:
                event.created = event_data["dtstamp"]
            
            cal.events.add(event)

        if not cal.events:
            logging.error("Keine gültigen Ereignisse zum Exportieren gefunden.")
            return None

        return str(cal)

# Beispiel für die Verwendung:
# if __name__ == "__main__":
#     exporter = ICalExporter()
#     now = datetime.now()
#     my_events = [
#         {
#             "summary": "Morgen-Workout",
#             "start": now.replace(hour=7, minute=0, second=0),
#             "end": now.replace(hour=8, minute=0, second=0)
#         },
#         {
#             "summary": "Projekt-Meeting",
#             "start": now.replace(hour=10, minute=0, second=0),
#             "end": now.replace(hour=11, minute=30, second=0),
#             "description": "Diskussion über den nächsten Meilenstein."
#         }
#     ]
#     exporter.export_to_file(my_events, "mein_wochenplan.ics")
