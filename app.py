from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
from flask_sqlalchemy import SQLAlchemy
import random
import os
from reportlab.pdfgen import canvas
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure secret key
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class PlannerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    subject1 = db.Column(db.String(100), nullable=False)
    material1 = db.Column(db.String(100))
    subject2 = db.Column(db.String(100), nullable=False)
    material2 = db.Column(db.String(100))
    learning_subject = db.Column(db.String(100))
    learning_task = db.Column(db.String(100))

# Create the database within the app context
with app.app_context():
    db.create_all()

# Weekdays with specific text content
days_data = {
    "Montag": {
        "tasks": ["Stark starten! Alles für einen produktiven Wochenbeginn vorbereiten."],
        "tips": [
            "Lernstrategie: Teste dich selbst oder quizze mit einem Freund!",
            "Motivation: Du kannst alles schaffen, wenn du Schritt für Schritt vorgehst!",
            "Brain Break: 5 Minuten Pause mit deinem Lieblingssong tanzen!"
        ]
    },
    "Dienstag": {
        "tasks": ["Voller Fokus! Zeit, die Woche voranzutreiben."],
        "tips": [
            "Heldentipp: Manchmal hilft es, laut zu wiederholen, was man lernt.",
            "Hinweis: Gehe schwierige Aufgaben zuerst an, dann wird der Rest leichter!",
            "Erinnerung: Brauchst du Hilfe? Frag jemanden!"
        ]
    },
    "Mittwoch": {
        "tasks": ["Halbzeitheld! Du bist auf der Hälfte zur Zielgeraden."],
        "tips": [
            "Tipp: Plane regelmäßige Pausen ein, um deine Konzentration zu steigern.",
            "Brain Break: 5 Minuten Dehnübungen, um den Kopf frei zu bekommen.",
            "Motivation: Halte durch! Der Rest der Woche wird einfacher."
        ]
    },
    "Donnerstag": {
        "tasks": ["Wissensritter! Heute wird das Wissen vertieft."],
        "tips": [
            "Hinweis: Wiederhole den Stoff, den du nicht ganz verstanden hast.",
            "Heldentipp: Übe mit einem Freund, um die Inhalte zu festigen.",
            "Motivation: Mach eine kurze Pause nach jeder Stunde intensiven Lernens!"
        ]
    },
    "Freitag": {
        "tasks": ["Fast geschafft! Bereite dich aufs Wochenende vor."],
        "tips": [
            "Tipp: Schließe alle offenen Aufgaben ab, um entspannt ins Wochenende zu gehen.",
            "Motivation: Belohne dich mit etwas Schönem, wenn du alles erledigt hast!",
            "Brain Break: Mach einen Spaziergang, um den Kopf freizubekommen."
        ]
     }
}

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            for day in days_data.keys():
                subject1 = request.form.get(f"subject1-{day}")
                material1 = request.form.get(f"material1-{day}")
                subject2 = request.form.get(f"subject2-{day}")
                material2 = request.form.get(f"material2-{day}")
                learning_subject = request.form.get(f"learning-subject-{day}")
                learning_task = request.form.get(f"learning-task-{day}")

                if not subject1 or not subject2 or not learning_subject:
                    flash(f"Please fill in all required fields for {day}.", "error")
                    return redirect(url_for('home'))

                entry = PlannerEntry(day=day, subject1=subject1, material1=material1, subject2=subject2, material2=material2, learning_subject=learning_subject, learning_task=learning_task)
                db.session.add(entry)
            db.session.commit()
            flash("Data saved successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('home'))

    random_data = {day: {"task": random.choice(data["tasks"]), "tip": random.choice(data["tips"])} for day, data in days_data.items()}
    return render_template('index.html', days=random_data)

# PDF download route
@app.route('/download-pdf')
def download_pdf():
    file_path = 'planner.pdf'
    c = canvas.Canvas(file_path)
    c.setFont("Helvetica", 12)
    y = 800

    entries = PlannerEntry.query.all()
    for entry in entries:
        c.drawString(50, y, f"{entry.day}:")
        c.drawString(70, y-20, f"Fach 1: {entry.subject1} - Material: {entry.material1}")
        c.drawString(70, y-40, f"Fach 2: {entry.subject2} - Material: {entry.material2}")
        c.drawString(70, y-60, f"Lernfach: {entry.learning_subject} - Aufgabe: {entry.learning_task}")
        y -= 100

    c.save()
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    csrf.init_app(app)
    app.run(debug=True)