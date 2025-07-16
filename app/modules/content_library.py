# [UPDATES] Dieses Modul führt eine Bibliothek für vordefinierte Fächer und Aufgaben ein.
# [IDEAS] Zukünftig könnte die Bibliothek durch benutzerdefinierte Vorlagen erweitert oder aus externen Konfigurationsdateien (JSON/YAML) geladen werden.
# [ISSUES] Die aktuelle Inhaltsliste ist statisch und auf den deutschen Bildungskontext zugeschnitten. Eine Internationalisierung (i18n) wäre ein logischer nächster Schritt.
# [PRAISE] Die Nutzung des Singleton-Patterns ist hier eine ausgezeichnete Wahl, um eine konsistente und ressourcenschonende Datenquelle zu gewährleisten.

from typing import List, Dict, Optional

class ContentLibrary:
    """
    Stellt als Singleton eine Bibliothek mit vordefinierten Fächern und Aufgaben bereit.
    """
    _instance: Optional['ContentLibrary'] = None

    _SUBJECTS: List[str] = [
        "Mathematik", "Deutsch", "Englisch", "Physik", "Chemie", "Biologie",
        "Geschichte", "Geographie", "Informatik", "Kunst", "Musik", "Sport"
    ]

    _TASKS_BY_SUBJECT: Dict[str, List[str]] = {
        "Mathematik": ["Hausaufgaben erledigen", "Formeln wiederholen", "Für Test lernen"],
        "Deutsch": ["Lektüre lesen", "Aufsatz schreiben", "Grammatik üben"],
        "Englisch": ["Vokabeln lernen", "Text zusammenfassen", "Präsentation vorbereiten"],
        "Physik": ["Experiment protokollieren", "Theorie zusammenfassen"],
        "Chemie": ["Reaktionsgleichungen üben", "Laborbericht schreiben"],
        "Biologie": ["Zellstrukturen zeichnen", "Fachbegriffe lernen"],
        "Informatik": ["Programmieraufgabe lösen", "Algorithmen analysieren"],
        "Allgemein": ["Lernplan erstellen", "Mitschriften ordnen", "Recherche für Referat"]
    }

    def __new__(cls) -> 'ContentLibrary':
        if cls._instance is None:
            cls._instance = super(ContentLibrary, cls).__new__(cls)
            print("ContentLibrary Singleton initialisiert.")
        return cls._instance

    def get_subjects(self) -> List[str]:
        """Gibt eine Liste aller vordefinierten Fächer zurück."""
        return self._SUBJECTS

    def get_tasks_for_subject(self, subject: str) -> List[str]:
        """
        Gibt eine Liste vordefinierter Aufgaben für ein bestimmtes Fach zurück.
        Fallenback auf allgemeine Aufgaben, wenn das Fach nicht existiert.
        """
        if not isinstance(subject, str):
            raise TypeError("Subject muss ein String sein.")

        if subject not in self._SUBJECTS:
            # Use logging instead of print for production
            return self._TASKS_BY_SUBJECT.get("Allgemein", [])

        specific_tasks = self._TASKS_BY_SUBJECT.get(subject, [])
        general_tasks = self._TASKS_BY_SUBJECT.get("Allgemein", [])
        # Kombiniert spezifische und allgemeine Aufgaben, um eine umfassendere Liste zu bieten.
        return specific_tasks + general_tasks

    def get_all_preset_tasks(self) -> Dict[str, List[str]]:
        """Gibt alle vordefinierten Aufgaben, gruppiert nach Fach, zurück."""
        return self._TASKS_BY_SUBJECT

# Beispiel für die Verwendung:
# if __name__ == "__main__":
#     # Das Singleton-Pattern stellt sicher, dass beide Variablen auf dieselbe Instanz verweisen.
#     library_1 = ContentLibrary()
#     library_2 = ContentLibrary()
#     assert library_1 is library_2, "Singleton-Instanzen müssen identisch sein."
#
#     print("\nVerfügbare Fächer:")
#     subjects = library_1.get_subjects()
#     print(f"-> {', '.join(subjects)}")
#
#     print("\nBeispielhafte Aufgaben für 'Mathematik':")
#     math_tasks = library_1.get_tasks_for_subject("Mathematik")
#     for task in math_tasks:
#         print(f"- {task}")
#
#     print("\nBeispielhafte Aufgaben für ein nicht existierendes Fach ('Philosophie'):")
#     philosophy_tasks = library_1.get_tasks_for_subject("Philosophie")
#     for task in philosophy_tasks:
#         print(f"- {task}")
