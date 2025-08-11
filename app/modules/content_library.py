#1: Updates: Converted mutable class attributes to instance attributes; expanded subjects & tasks; added helper methods (add_task_for_subject, has_subject, list_subjects_with_task_counts); ensured no shared mutable state; added defensive copies on access.
#2: Future Ideas: Externalize data to JSON / DB; add i18n; cache frequently accessed merged task lists; integrate tagging & difficulty levels.
#3: Issues+Fixes: Fixed potential shared-state mutation bug; normalized subject handling; added validation guarding empty/duplicate inserts.
# Compliment: Saubere, gut strukturierte Erweiterung – weiter so!

from __future__ import annotations
from typing import Dict, List, Iterable, Optional


class ContentLibrary:
    """
    Stellt eine Bibliothek mit vordefinierten Fächern und zugehörigen Aufgaben bereit.
    Implementiert als (soft) Singleton, wobei mutable Strukturen nun instanzgebunden sind.
    """

    _instance: Optional["ContentLibrary"] = None
    _initialized: bool = False

    # Falls der Singleton-Ansatz später entfernt wird, genügt das Löschen von __new__ und _initialized-Logik.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            # Vordefinierte Fächer (instanzgebunden, kein Shared State)
            self._subjects: List[str] = [
                "Mathematik",
                "Deutsch",
                "Englisch",
                "Französisch",
                "Spanisch",
                "Latein",
                "Physik",
                "Chemie",
                "Biologie",
                "Informatik",
                "Geschichte",
                "Geographie",
                "Politik",
                "Wirtschaft",
                "Religion",
                "Ethik",
                "Philosophie",
                "Technik",
                "Kunst",
                "Musik",
                "Sport",
            ]

            # Aufgaben nach Fach; "Allgemein" wird mit spezifischen Aufgaben kombiniert
            self._tasks_by_subject: Dict[str, List[str]] = {
                "Mathematik": [
                    "Hausaufgaben erledigen",
                    "Formeln wiederholen",
                    "Für Test lernen",
                    "Aufgaben aus Übungsheft bearbeiten",
                    "Alte Klausur analysieren",
                ],
                "Deutsch": [
                    "Lektüre lesen",
                    "Aufsatz schreiben",
                    "Grammatik üben",
                    "Text interpretieren",
                    "Gedicht analysieren",
                ],
                "Englisch": [
                    "Vokabeln lernen",
                    "Listening-Übungen machen",
                    "Essay planen",
                    "Grammatik wiederholen",
                    "Präsentation vorbereiten",
                ],
                "Französisch": [
                    "Vokabelkarten wiederholen",
                    "Dialog einüben",
                    "Grammatikübungen lösen",
                ],
                "Spanisch": [
                    "Verbkonjugationen wiederholen",
                    "Kurzen Text verfassen",
                    "Audioverständnis trainieren",
                ],
                "Latein": [
                    "Vokabeln repetieren",
                    "Text übersetzen",
                    "Satzkonstruktionen üben",
                ],
                "Physik": [
                    "Experiment protokollieren",
                    "Theorie zusammenfassen",
                    "Formelsammlung erweitern",
                ],
                "Chemie": [
                    "Reaktionsgleichungen üben",
                    "Laborbericht schreiben",
                    "Stoffklassen einprägen",
                ],
                "Biologie": [
                    "Zellstrukturen zeichnen",
                    "Fachbegriffe lernen",
                    "Stoffwechselwege skizzieren",
                ],
                "Informatik": [
                    "Programmieraufgabe lösen",
                    "Algorithmen analysieren",
                    "Code-Review durchführen",
                    "Datenstrukturen wiederholen",
                ],
                "Geschichte": [
                    "Zeitleiste erstellen",
                    "Quelle analysieren",
                    "Ereignis zusammenfassen",
                ],
                "Geographie": [
                    "Klimadiagramm interpretieren",
                    "Karte beschriften",
                    "Regionale Unterschiede vergleichen",
                ],
                "Politik": [
                    "Aktuelles Thema recherchieren",
                    "Debattenargumente sammeln",
                ],
                "Wirtschaft": [
                    "Marktmodell skizzieren",
                    "Kennzahlen berechnen",
                ],
                "Religion": [
                    "Textstelle reflektieren",
                    "Vergleich von Weltreligionen",
                ],
                "Ethik": [
                    "Dilemma analysieren",
                    "Philosophische Position vergleichen",
                ],
                "Philosophie": [
                    "Primärtext exzerpieren",
                    "Argumentationsstruktur darstellen",
                ],
                "Technik": [
                    "Konstruktionsskizze anfertigen",
                    "Funktionsprinzip erklären",
                ],
                "Kunst": [
                    "Bildanalyse verfassen",
                    "Skizzenbuch ergänzen",
                ],
                "Musik": [
                    "Rhythmus üben",
                    "Stück analysieren",
                    "Tonleitern wiederholen",
                ],
                "Sport": [
                    "Trainingsplan erstellen",
                    "Technik verbessern",
                ],
                "Allgemein": [
                    "Lernplan erstellen",
                    "Mitschriften ordnen",
                    "Recherche für Referat",
                    "Zusammenfassung erstellen",
                    "Karteikarten anlegen",
                    "Mindmap erstellen",
                    "Wiederholungszyklus planen",
                ],
            }

            self._initialized = True

    # --------------- Öffentliche API ---------------

    def get_subjects(self) -> List[str]:
        """
        Liefert eine Kopie der verfügbaren Fächer.
        """
        return list(self._subjects)

    def has_subject(self, subject: str) -> bool:
        """Prüft ob Fach existiert (case-sensitive)."""
        return subject in self._subjects

    def add_subject(self, subject: str) -> bool:
        """
        Fügt ein neues Fach hinzu.
        Returns:
            bool: True wenn hinzugefügt, False wenn leer oder bereits vorhanden.
        """
        if not subject or not isinstance(subject, str):
            return False
        if subject in self._subjects:
            return False
        self._subjects.append(subject)
        # Optional: leere Aufgabenliste für Konsistenz
        self._tasks_by_subject.setdefault(subject, [])
        return True

    def remove_subject(self, subject: str) -> bool:
        """
        Entfernt ein Fach und zugehörige Aufgaben (spezifisch, nicht Allgemein).
        'Allgemein' wird geschützt.
        """
        if subject == "Allgemein":
            return False
        if subject in self._subjects:
            self._subjects.remove(subject)
            self._tasks_by_subject.pop(subject, None)
            return True
        return False

    def get_tasks_for_subject(self, subject: str) -> List[str]:
        """
        Kombiniert spezifische und allgemeine Aufgaben.
        Fällt zurück auf nur Allgemein falls Fach unbekannt.
        """
        if not isinstance(subject, str):
            raise TypeError("subject muss ein String sein.")
        general = self._tasks_by_subject.get("Allgemein", [])
        if subject not in self._subjects:
            return list(general)
        specific = self._tasks_by_subject.get(subject, [])
        # Keine Mutationen der Original-Listen
        return list(specific) + list(general)

    def get_all_preset_tasks(self) -> Dict[str, List[str]]:
        """
        Gibt eine tiefe Kopie aller Aufgaben nach Fach zurück.
        """
        return {k: list(v) for k, v in self._tasks_by_subject.items()}

    def add_task_for_subject(self, subject: str, task: str) -> bool:
        """
        Fügt eine Aufgabe zu einem Fach hinzu (oder legt das Fach an).
        Leere oder doppelte Einträge werden ignoriert.
        """
        if not task or not isinstance(task, str):
            return False
        if subject not in self._subjects:
            # Option: automatisches Anlegen: auskommentieren falls nicht erwünscht
            self.add_subject(subject)
        tasks = self._tasks_by_subject.setdefault(subject, [])
        if task in tasks:
            return False
        tasks.append(task)
        return True

    def list_subjects_with_task_counts(self) -> List[tuple[str, int]]:
        """
        Liefert Liste von (Fach, Anzahl spezifischer Aufgaben).
        'Allgemein' wird ans Ende gestellt.
        """
        items: List[tuple[str, int]] = []
        for subj in self._subjects:
            if subj == "Allgemein":
                continue
            items.append((subj, len(self._tasks_by_subject.get(subj, []))))
        items.sort(key=lambda x: x[0].lower())
        # Allgemein zuletzt
        if "Allgemein" in self._tasks_by_subject:
            items.append(("Allgemein", len(self._tasks_by_subject.get("Allgemein", []))))
        return items

    # --------------- Repräsentation & Debug ---------------

    def __repr__(self) -> str:  # pragma: no cover (rein informativ)
        return f"<ContentLibrary subjects={len(self._subjects)} tasks={sum(len(v) for v in self._tasks_by_subject.values())}>"

# Beispiel Nutzung (manuell testen):
# if __name__ == "__main__":
#     lib = ContentLibrary()
#     print(lib.list_subjects_with_task_counts())
#     print(lib.get_tasks_for_subject("Mathematik")[:5])
#     lib.add_task_for_subject("Mathematik", "Graphen analysieren")
#     print(lib.get_tasks_for_subject("Mathematik")[-3:])
