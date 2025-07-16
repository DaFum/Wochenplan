-from typing import Dict, List, Optional
+from typing import Dict, List


class ContentLibrary:
    """
    Stellt als Singleton eine Bibliothek mit vordefinierten Fächern und
    Aufgaben bereit.
    """
    _SUBJECTS: List[str] = [
        "Mathematik", "Deutsch", "Englisch", "Physik", "Chemie", "Biologie",
        "Geschichte", "Geographie", "Informatik", "Kunst", "Musik", "Sport"
    ]

    _TASKS_BY_SUBJECT: Dict[str, List[str]] = {
        "Mathematik": [
            "Hausaufgaben erledigen", "Formeln wiederholen", "Für Test lernen"
        ],
        "Deutsch": ["Lektüre lesen", "Aufsatz schreiben", "Grammatik üben"],
        "Englisch": [
            "Vokabeln lernen", "Text zusammenfassen",
            "Präsentation vorbereiten"
        ],
        "Physik": ["Experiment protokollieren", "Theorie zusammenfassen"],
        "Chemie": ["Reaktionsgleichungen üben", "Laborbericht schreiben"],
        "Biologie": ["Zellstrukturen zeichnen", "Fachbegriffe lernen"],
        "Informatik": ["Programmieraufgabe lösen", "Algorithmen analysieren"],
        "Allgemein": [
            "Lernplan erstellen", "Mitschriften ordnen",
            "Recherche für Referat"
        ]
    }

    def get_subjects(self) -> List[str]:
        """
        Gibt die Liste aller vordefinierten Schulfächer zurück.
        
        Returns:
            List[str]: Eine Liste mit den Namen aller verfügbaren Fächer.
        """
        return self._SUBJECTS

    def get_tasks_for_subject(self, subject: str) -> List[str]:
        """
        Gibt eine kombinierte Liste vordefinierter Aufgaben für das angegebene Fach zurück.
        
        Wenn das Fach nicht in der Bibliothek vorhanden ist, werden nur die allgemeinen Aufgaben zurückgegeben. Bei gültigen Fächern werden fachbezogene und allgemeine Aufgaben zusammengeführt.
        
        Parameters:
            subject (str): Name des gewünschten Fachs.
        
        Returns:
            List[str]: Liste der Aufgaben für das angegebene Fach.
        """
        if not isinstance(subject, str):
            raise TypeError("Subject muss ein String sein.")

        if subject not in self._SUBJECTS:
            # Use logging instead of print for production
            return self._TASKS_BY_SUBJECT.get("Allgemein", [])

        specific_tasks = self._TASKS_BY_SUBJECT.get(subject, [])
        general_tasks = self._TASKS_BY_SUBJECT.get("Allgemein", [])
        # Kombiniert spezifische und allgemeine Aufgaben, um eine
        # umfassendere Liste zu bieten.
        return specific_tasks + general_tasks

    def get_all_preset_tasks(self) -> Dict[str, List[str]]:
        """
        Gibt das vollständige Wörterbuch aller vordefinierten Aufgaben nach Fach gruppiert zurück.
        
        Returns:
            Dict[str, List[str]]: Ein Wörterbuch, das jedem Fach eine Liste von Aufgaben zuordnet.
        """
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
