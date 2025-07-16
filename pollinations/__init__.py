# [UPDATES] Die `Text`-Klasse wurde in den Namespace des Pakets importiert, um den Zugriff gemäß dem Beispielcode zu ermöglichen.
# [IDEAS] Zukünftig könnte ein übergeordneter Client (`pollinations.Client`) eingeführt werden, der Instanzen von `Text`, `Image` etc. als Attribute bereitstellt.
# [ISSUES] Das direkte Importieren von Klassen kann bei einer großen Anzahl von Modulen zu einem überladenen Namespace führen.
# [PRAISE] Die Bereitstellung der Kernfunktionalität im `__init__`-Modul ist eine bewährte Praxis, die die Benutzerfreundlichkeit des SDKs maximiert.

"""
Pollinations Python SDK
"""
__version__ = "0.2.0" # Version erhöht, um neue Funktionalität abzubilden

from .text import Text

__all__ = [
    "Text"
]
