# Wochenplan App
Die Wochenplan App ist eine einfache Anwendung, die es Benutzern ermöglicht, ihre wöchentlichen Aufgaben und Lerninhalte zu planen und zu verwalten. Die App verwendet Flask für das Backend, SQLAlchemy für die Datenbankverwaltung und Flask-WTF für die Formulare. Das Frontend ist mit HTML und CSS gestaltet.

## Features
Aufgabenplanung: Benutzer können tägliche Aufgaben und Lerninhalte für die Woche eingeben und speichern.
PDF-Download: Exportiere deine Wochenplanung als PDF.
Responsives Design: Benutzerfreundliche Oberfläche, die auf verschiedenen Geräten gut aussieht.
Dunkelmodus: Umschalten zwischen hellem und dunklem Modus für eine angenehme Nutzung bei unterschiedlichen Lichtverhältnissen.
Installation
## Repository klonen:

```
git clone https://github.com/DaFum/Wochenplan.git
cd Wochenplan
```
Virtuelle Umgebung erstellen:
```
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
Abhängigkeiten installieren:
```
pip install -r requirements.txt
```
Datenbank konfigurieren:

Setze die Umgebungsvariable DATABASE_URI oder nutze die voreingestellte SQLite-Datenbank.

Anwendung starten:
```
flask run
```

## Nutzung
Startseite: Auf der Startseite können Benutzer ihre Aufgaben und Lerninhalte für jeden Tag der Woche eingeben.
Aufgaben speichern: Nach dem Ausfüllen der Formulare können die Daten gespeichert werden.
PDF herunterladen: Die Wochenplanung kann als PDF-Datei heruntergeladen werden.
## Ordnerstruktur
app.py: Hauptanwendung und Routen.
static/styles.css: Stile für die Benutzeroberfläche.
templates/: index.html für die Seite.
### Lizenz
Dieses Projekt steht unter der MIT-Lizenz.
