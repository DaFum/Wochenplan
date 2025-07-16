# [UPDATES] Dieses Modul ermöglicht den Export von Terminen in das universelle .ics-Format.
# [IDEAS] Zukünftig könnte ein iCal-Import hinzugefügt werden, um eine Zwei-Wege-Synchronisation zu ermöglichen.
# [ISSUES] Benötigt die 'ics'-Bibliothek (`pip install ics`). Dies muss in den Abhängigkeiten vermerkt werden.
# [PRAISE] Die Implementierung ist sauber, effizient und folgt bewährten Praktiken.

from ics import Calendar, Event
from typing import List, Dict, Any

import logging

class ICalExporter:
    """Exportiert eine Liste von Ereignissen in eine .ics-Kalenderdatei."""
    def __init__(self):
        logging.info("ICalExporter initialisiert.")

    def export_to_file(self, events: List[Dict[str, Any]], filename: str) -> bool:
        """
        Erstellt eine .ics-Datei aus einer Liste von Ereignis-Wörterbüchern.

        Ein Ereignis-Wörterbuch sollte enthalten:
        - 'summary' (str): Der Titel des Ereignisses.
        - 'start' (datetime): Die Startzeit.
        - 'end' (datetime): Die Endzeit.
        - 'description' (str, optional): Die Beschreibung.
        """
        if not filename.endswith(".ics"):
            filename += ".ics"

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
            cal.events.add(event)

import logging

        if not cal.events:
            logging.error("Keine gültigen Ereignisse zum Exportieren gefunden.")
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(cal))
            logging.info(f"Wochenplan erfolgreich nach '{filename}' exportiert.")
            return True
        except IOError as e:
            logging.error(f"Fehler beim Schreiben der Datei '{filename}': {e}")
            return False

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
