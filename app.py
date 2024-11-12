from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import random
import os
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-default-secret-key')  # Use a fixed secret key
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class PlannerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False, unique=True)
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

# Flask-WTF form class
class PlannerForm(FlaskForm):
    subject1 = StringField('Subject 1')
    material1 = StringField('Material 1')
    subject2 = StringField('Subject 2')
    material2 = StringField('Material 2')
    learning_subject = StringField('Learning Subject')
    learning_task = StringField('Learning Task')
    submit = SubmitField('Submit')

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    forms = {}
    if request.method == 'POST':
        try:
            for day in days_data.keys():
                form = PlannerForm(meta={'csrf': False})
                form.subject1.data = request.form.get(f"subject1-{day}")
                form.material1.data = request.form.get(f"material1-{day}")
                form.subject2.data = request.form.get(f"subject2-{day}")
                form.material2.data = request.form.get(f"material2-{day}")
                form.learning_subject.data = request.form.get(f"learning-subject-{day}")
                form.learning_task.data = request.form.get(f"learning-task-{day}")

                if not form.subject1.data or not form.subject2.data or not form.learning_subject.data:
                    flash(f"Please fill in all required fields for {day}.", "error")
                    return redirect(url_for('home'))

                # Check if an entry for this day already exists
                entry = PlannerEntry.query.filter_by(day=day).first()
                if entry:
                    # Update existing entry
                    entry.subject1 = form.subject1.data
                    entry.material1 = form.material1.data
                    entry.subject2 = form.subject2.data
                    entry.material2 = form.material2.data
                    entry.learning_subject = form.learning_subject.data
                    entry.learning_task = form.learning_task.data
                else:
                    # Create new entry
                    entry = PlannerEntry(
                        day=day,
                        subject1=form.subject1.data,
                        material1=form.material1.data,
                        subject2=form.subject2.data,
                        material2=form.material2.data,
                        learning_subject=form.learning_subject.data,
                        learning_task=form.learning_task.data
                    )
                    db.session.add(entry)
            db.session.commit()
            flash("Data saved successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('home'))

    random_data = {
        day: {
            "task": random.choice(data["tasks"]),
            "tip": random.choice(data["tips"])
        } for day, data in days_data.items()
    }
    return render_template('index.html', days=random_data)

# PDF download route
@app.route('/download-pdf')
def download_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750

    entries = PlannerEntry.query.all()
    for entry in entries:
        c.drawString(50, y, f"{entry.day}:")
        c.drawString(70, y - 20, f"Fach 1: {entry.subject1} - Material: {entry.material1}")
        c.drawString(70, y - 40, f"Fach 2: {entry.subject2} - Material: {entry.material2}")
        c.drawString(70, y - 60, f"Lernfach: {entry.learning_subject} - Aufgabe: {entry.learning_task}")
        y -= 100

        if y <= 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750

    c.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name='planner.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)