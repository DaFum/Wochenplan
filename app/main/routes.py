from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import db
from app.models import PlannerEntry, Subject
from .forms import PlannerForm
from datetime import datetime, timedelta
import random
import io
from weasyprint import HTML

main_bp = Blueprint('main', __name__)

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

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

@main_bp.route('/', methods=['GET', 'POST'])
def home():
    form = PlannerForm()
    if form.validate_on_submit():
        try:
            week_start = get_week_start()
            for day in WEEKDAYS:
                entry = PlannerEntry.query.filter_by(day=day, week_start=week_start).first()
                if entry:
                    entry.subject1 = form.subject1.data
                    entry.material1 = form.material1.data
                    entry.subject2 = form.subject2.data
                    entry.material2 = form.material2.data
                    entry.learning_subject = form.learning_subject.data
                    entry.learning_task = form.learning_task.data
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
            db.session.commit()
            flash("Daten erfolgreich gespeichert!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Ein Fehler ist aufgetreten: {str(e)}", "error")
        return redirect(url_for('main.home'))

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

    return render_template('index.html', days=random_data, subjects=Subject.query.all(), form=form)

@main_bp.route('/api/week-data')
def get_week_data():
    week_start = get_week_start()
    entries = PlannerEntry.query.filter_by(week_start=week_start).all()
    data = {entry.day: {
        'subject1': entry.subject1.name,
        'material1': entry.material1,
        'subject2': entry.subject2.name,
        'material2': entry.material2,
        'learning_subject': entry.learning_subject.name,
        'learning_task': entry.learning_task
    } for entry in entries}
    return jsonify(data)

@main_bp.route('/download-pdf')
def download_pdf():
    week_start = get_week_start()
    entries = PlannerEntry.query.filter_by(week_start=week_start).all()
    
    pdf_content = render_template('pdf_template.html', entries=entries)
    pdf_file = HTML(string=pdf_content).write_pdf()

    return send_file(
        io.BytesIO(pdf_file),
        as_attachment=True,
        download_name='wochenplan.pdf',
        mimetype='application/pdf'
    )

@main_bp.route('/einstellungen', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        new_subject = request.form.get('new_subject')
        if new_subject:
            existing_subject = Subject.query.filter_by(name=new_subject).first()
            if not existing_subject:
                subject = Subject(name=new_subject)
                db.session.add(subject)
                db.session.commit()
                flash("Neues Fach erfolgreich hinzugefügt!", "success")
            else:
                flash("Das Fach existiert bereits.", "error")
        return redirect(url_for('main.settings'))
    subjects = Subject.query.all()
    return render_template('settings.html', subjects=subjects)
