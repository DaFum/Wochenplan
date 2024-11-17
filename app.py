from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
import random
import os
import io
from dotenv import load_dotenv
from weasyprint import HTML
from datetime import datetime, timedelta
from flask import send_from_directory

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-default-secret-key')
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Konstanten für wiederholte Zeichenketten
WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
SUBJECTS = ["Mathe", "Deutsch", "Englisch", "Biologie", "Chemie", "Physik", "Geschichte", "Geografie", "Kunst", "Musik"]

# Database model
class PlannerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    subject1 = db.Column(db.String(100), nullable=False)
    material1 = db.Column(db.String(100))
    subject2 = db.Column(db.String(100), nullable=False)
    material2 = db.Column(db.String(100))
    learning_subject = db.Column(db.String(100))
    learning_task = db.Column(db.String(100))

    __table_args__ = (db.UniqueConstraint('day', 'week_start', name='_day_week_uc'),)

# Create the database within the app context
with app.app_context():
    db.create_all()
    db.Index('idx_week_start', PlannerEntry.week_start)
    db.Index('idx_day', PlannerEntry.day)

# Weekdays with specific text content
days_data = {
    "Montag": {
        "tasks": [
            "Los geht's! Starte die Woche mit viel Energie.",
            "Montagmorgen: Packe deine Schulsachen sorgfältig ein.",
            "Neue Woche, neues Abenteuer! Sei bereit.",
            "Beginne den Tag mit einem Lächeln.",
            "Zeit für frische Ideen! Was möchtest du diese Woche erreichen?",
            "Montag ist Superheldentag – Sei der Held deiner eigenen Geschichte!",
            "Bring deine Lieblingsbrotdose mit zur Schule.",
            "Übe heute ein neues Wort in einer Fremdsprache.",
            "Finde heraus, was deine Freunde am Wochenende gemacht haben.",
            "Male ein Bild von etwas, das du magst.",
            "Lies ein Kapitel in deinem Lieblingsbuch.",
            "Mach heute etwas Nettes für einen Mitschüler."
        ],
        "tips": [
            "Tipp: Schreibe deine Hausaufgaben sofort auf, damit du nichts vergisst.",
            "Motivation: Du kannst alles schaffen, wenn du an dich glaubst!",
            "Erinnerung: Ein gesundes Frühstück gibt dir Power für den Tag.",
            "Lernstrategie: Nutze farbenfrohe Notizen, um dir Dinge besser zu merken.",
            "Pausen-Tipp: Mach eine kurze Pause und strecke dich!",
            "Hinweis: Trinke genug Wasser, um fit zu bleiben.",
            "Motivation: Jeder Tag ist ein neues Abenteuer!",
            "Tipp: Frag deine Lehrer, wenn du etwas nicht verstehst.",
            "Lerntrick: Benutze lustige Eselsbrücken zum Merken.",
            "Erinnerung: Packe deine Sportsachen ein, wenn du Sportunterricht hast.",
            "Pausen-Tipp: Zeichne etwas Lustiges auf einen Notizzettel.",
            "Hinweis: Halte deinen Schreibtisch ordentlich für besseres Lernen."
        ]
    },
    "Dienstag": {
        "tasks": [
            "Zeit zu glänzen! Zeig, was in dir steckt.",
            "Entdecke etwas Neues in der Schule heute.",
            "Dienstag ist Wissens-Tag – Sammle so viel du kannst!",
            "Gemeinsam lernen macht Spaß – Frag einen Freund um Hilfe.",
            "Bleib neugierig und stelle Fragen.",
            "Heute ist ein guter Tag, um etwas zu meistern, das du gestern noch nicht konntest.",
            "Mach bei einem Schulspiel oder -projekt mit.",
            "Versuche, in der Pause ein neues Spiel zu spielen.",
            "Teile dein Pausenbrot mit jemandem.",
            "Schreibe einen kurzen Aufsatz über dein Lieblingstier.",
            "Lerne ein neues Lied oder Gedicht.",
            "Hilf einem Freund bei seinen Hausaufgaben."
        ],
        "tips": [
            "Lerntrick: Erkläre einem Freund, was du gelernt hast.",
            "Motivation: Jeder Tag ist eine neue Chance.",
            "Hinweis: Setze dir kleine Ziele und erreiche sie.",
            "Erinnerung: Packe einen gesunden Snack ein.",
            "Pausen-Tipp: Sing dein Lieblingslied!",
            "Tipp: Lächle – das macht alles besser.",
            "Motivation: Fehler sind okay – daraus lernst du!",
            "Hinweis: Schreibe mit bunten Stiften, um den Spaß zu erhöhen.",
            "Erinnerung: Frag deine Eltern nach ihrer Kindheit.",
            "Lerntrick: Mache Lernkarten für schwierige Wörter.",
            "Pausen-Tipp: Spring Seil oder hüpfe auf einem Bein.",
            "Tipp: Bereite deine Sachen für den nächsten Tag schon am Abend vor."
        ]
    },
    "Mittwoch": {
        "tasks": [
            "Halbzeit! Du hast schon viel geschafft.",
            "Mittwochspaß: Lerne etwas Cooles.",
            "Bleib dran! Die Woche ist halb vorbei.",
            "Teile dein Wissen mit einem Klassenkameraden.",
            "Mach heute etwas, das dich stolz macht.",
            "Feiere kleine Erfolge – du verdienst es!",
            "Schreibe eine Geschichte oder ein Gedicht.",
            "Erfinde ein neues Spiel mit deinen Freunden.",
            "Entdecke ein neues Hobby oder Interesse.",
            "Hilf zu Hause bei einer kleinen Aufgabe.",
            "Lerne ein paar Wörter in Gebärdensprache.",
            "Male ein Bild von deinem Traumurlaub."
        ],
        "tips": [
            "Motivation: Du bist auf dem richtigen Weg!",
            "Lernstrategie: Benutze lustige Eselsbrücken.",
            "Erinnerung: Bewegung hilft beim Denken – spring ein bisschen herum!",
            "Hinweis: Frag nach, wenn du etwas nicht verstehst.",
            "Pausen-Tipp: Male ein Bild in 5 Minuten.",
            "Tipp: Schreibe drei Dinge auf, die du gut kannst.",
            "Motivation: Jeder kann ein Held sein!",
            "Hinweis: Übe dein schönstes Schriftbild.",
            "Erinnerung: Verbringe Zeit mit deiner Familie.",
            "Lerntrick: Mach ein Mindmap zu einem Thema.",
            "Pausen-Tipp: Schau in den Himmel und finde Formen in den Wolken.",
            "Tipp: Hilf einem Geschwisterchen bei den Hausaufgaben."
        ]
    },
    "Donnerstag": {
        "tasks": [
            "Fast geschafft! Gib nochmal dein Bestes.",
            "Donnerstag-Entdecker: Lerne etwas Spannendes.",
            "Sei heute mutig und probiere etwas Neues aus.",
            "Arbeite mit jemandem zusammen – Teamwork ist toll!",
            "Stelle dir vor, was du alles erreichen kannst.",
            "Heute ist dein Tag, leuchte hell!",
            "Organisiere deine Schulsachen für morgen.",
            "Schreibe einen Brief an dein zukünftiges Ich.",
            "Versuche, heute besonders freundlich zu sein.",
            "Baue etwas aus Legosteinen oder Bauklötzen.",
            "Erfinde einen Superhelden mit besonderen Kräften.",
            "Lerne etwas über ein Tier, das dich interessiert."
        ],
        "tips": [
            "Motivation: Glaub an dich, du kannst es!",
            "Lerntrick: Mache ein Spiel aus deinen Aufgaben.",
            "Hinweis: Bleib organisiert – das hilft enorm.",
            "Erinnerung: Atme tief durch, wenn du gestresst bist.",
            "Pausen-Tipp: Tanz für 2 Minuten wild herum.",
            "Tipp: Belohne dich nach getaner Arbeit.",
            "Motivation: Jeder Tag ist eine neue Gelegenheit.",
            "Hinweis: Schreibe sauber und ordentlich.",
            "Erinnerung: Iss genug Obst und Gemüse.",
            "Lerntrick: Stelle dir schwierige Dinge als Bilder vor.",
            "Pausen-Tipp: Mach ein lustiges Gesicht im Spiegel.",
            "Tipp: Frag deine Eltern etwas über ihre Kindheit."
        ]
    },
    "Freitag": {
        "tasks": [
            "Hurra, Freitag! Letzter Schultag der Woche.",
            "Schließe die Woche mit Bravour ab.",
            "Freue dich auf das Wochenende, aber bleib konzentriert.",
            "Erledige deine Aufgaben, damit du entspannt sein kannst.",
            "Denke darüber nach, was du diese Woche gelernt hast.",
            "Mach heute etwas Nettes für jemanden.",
            "Plane etwas Spaßiges für das Wochenende.",
            "Zeige deinen Eltern stolz deine Schulprojekte.",
            "Lies ein spannendes Buch oder eine Geschichte.",
            "Verabrede dich mit einem Freund zum Spielen.",
            "Entspanne dich und genieße den Tag.",
            "Sei stolz auf dich – du hast die Woche gemeistert!"
        ],
        "tips": [
            "Motivation: Du hast die Woche toll gemeistert!",
            "Hinweis: Räume deinen Schreibtisch für Montag auf.",
            "Erinnerung: Plane etwas Spaßiges fürs Wochenende.",
            "Pausen-Tipp: Erfinde einen Witz und erzähle ihn jemandem.",
            "Tipp: Sei stolz auf dich – du bist spitze!",
            "Lernstrategie: Schreibe auf, was du nächste Woche erreichen möchtest.",
            "Motivation: Genieße deine freie Zeit – die hast du dir verdient!",
            "Hinweis: Sortiere deine Unterlagen für einen klaren Start.",
            "Erinnerung: Bedanke dich bei deinen Lehrern für die Woche.",
            "Pausen-Tipp: Schau dir lustige Videos an.",
            "Tipp: Mach dir eine Liste mit Dingen, die du am Wochenende tun möchtest.",
            "Lernstrategie: Wiederhole kurz deine Lerninhalte der Woche."
        ]
     }
}

# Flask-WTF form class
class PlannerForm(FlaskForm):
    subject1 = StringField('Fach 1', render_kw={"placeholder": "Fach 1"})
    material1 = StringField('Material 1', render_kw={"placeholder": "Material 1"})
    subject2 = StringField('Fach 2', render_kw={"placeholder": "Fach 2"})
    material2 = StringField('Material 2', render_kw={"placeholder": "Material 2"})
    learning_subject = StringField('Lernfach', render_kw={"placeholder": "Lernfach"})
    learning_task = StringField('Lernaufgabe', render_kw={"placeholder": "Lernaufgabe"})
    submit = SubmitField('Speichern')

def get_random_item(items, used_items):
    unused_items = list(set(items) - set(used_items))
    if not unused_items:
        used_items.clear()
        unused_items = items.copy()
    item = random.choice(unused_items)
    used_items.append(item)
    return item

def get_week_start(date=None):
    if date is None:
        date = datetime.now()
    return date - timedelta(days=date.weekday())

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            week_start = get_week_start()
            entries_to_update = []
            for day in WEEKDAYS:
                form = PlannerForm(meta={'csrf': False})
                form.subject1.data = request.form.get(f"subject1-{day}")
                form.material1.data = request.form.get(f"material1-{day}")
                form.subject2.data = request.form.get(f"subject2-{day}")
                form.material2.data = request.form.get(f"material2-{day}")
                form.learning_subject.data = request.form.get(f"learning-subject-{day}")
                form.learning_task.data = request.form.get(f"learning-task-{day}")

                if not all([form.subject1.data, form.subject2.data, form.learning_subject.data]):
                    flash(f"Bitte fülle alle erforderlichen Felder für {day} aus.", "error")
                    return redirect(url_for('home'))

                entry = PlannerEntry.query.filter_by(day=day, week_start=week_start).first()
                if entry:
                    entry.subject1 = form.subject1.data
                    entry.material1 = form.material1.data
                    entry.subject2 = form.subject2.data
                    entry.material2 = form.material2.data
                    entry.learning_subject = form.learning_subject.data
                    entry.learning_task = form.learning_task.data
                    entries_to_update.append(entry)
                else:
                    new_entry = PlannerEntry(
                        day=day,
                        week_start=week_start,
                        subject1=form.subject1.data,
                        material1=form.material1.data,
                        subject2=form.subject2.data,
                        material2=form.material2.data,
                        learning_subject=form.learning_subject.data,
                        learning_task=form.learning_task.data
                    )
                    db.session.add(new_entry)
            
            db.session.add_all(entries_to_update)
            db.session.commit()
            flash("Daten erfolgreich gespeichert!", "success")
        except Exception as e:
            flash(f"Ein Fehler ist aufgetreten: {str(e)}", "error")
        return redirect(url_for('home'))

    if 'tasks_used' not in session:
        session['tasks_used'] = {day: [] for day in WEEKDAYS}
    if 'tips_used' not in session:
        session['tips_used'] = {day: [] for day in WEEKDAYS}

    random_data = {
        day: {
            "task": get_random_item(days_data[day]['tasks'], session['tasks_used'][day]),
            "tip": get_random_item(days_data[day]['tips'], session['tips_used'][day])
        } for day in WEEKDAYS
    }

    return render_template('index.html', days=random_data, subjects=SUBJECTS)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/api/week-data')
def get_week_data():
    week_start = get_week_start()
    entries = PlannerEntry.query.filter_by(week_start=week_start).all()
    data = {entry.day: {
        'subject1': entry.subject1,
        'material1': entry.material1,
        'subject2': entry.subject2,
        'material2': entry.material2,
        'learning_subject': entry.learning_subject,
        'learning_task': entry.learning_task
    } for entry in entries}
    return jsonify(data)

# PDF download route
@app.route('/download-pdf')
def download_pdf():
    week_start = get_week_start()
    entries = PlannerEntry.query.filter_by(week_start=week_start).all()
    
    pdf_content = "<html><body>"
    for entry in entries:
        pdf_content += f"<h2>{entry.day}</h2>"
        pdf_content += f"<p>Fach 1: {entry.subject1} - Material: {entry.material1}</p>"
        pdf_content += f"<p>Fach 2: {entry.subject2} - Material: {entry.material2}</p>"
        pdf_content += f"<p>Lernfach: {entry.learning_subject} - Aufgabe: {entry.learning_task}</p>"
    pdf_content += "</body></html>"

    pdf_file = HTML(string=pdf_content).write_pdf()

    return send_file(
        io.BytesIO(pdf_file),
        as_attachment=True,
        download_name='wochenplan.pdf',
        mimetype='application/pdf'
    )

@app.route('/einstellungen', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Prozess zur Verwaltung benutzerdefinierter Fächer
        new_subject = request.form.get('new_subject')
        if new_subject and new_subject not in SUBJECTS:
            SUBJECTS.append(new_subject)
            flash("Neues Fach erfolgreich hinzugefügt!", "success")
        return redirect(url_for('settings'))
    
    return render_template('settings.html', subjects=SUBJECTS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)