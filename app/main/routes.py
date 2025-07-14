from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import db
from app.models import PlannerEntry, Subject
from .forms import PlannerForm
from datetime import datetime, timedelta
import random
import io
import json
from weasyprint import HTML

main_bp = Blueprint('main', __name__)

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

def load_days_data():
    with open('config/weekday_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

days_data = load_days_data()

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
        'subject1': entry.subject1.name if entry.subject1 else '',
        'material1': entry.material1,
        'subject2': entry.subject2.name if entry.subject2 else '',
        'material2': entry.material2,
        'learning_subject': entry.learning_subject.name if entry.learning_subject else '',
        'learning_task': entry.learning_task
    } for entry in entries}
    return jsonify(data)

@main_bp.route('/download-pdf')
def download_pdf():
    week_start = get_week_start()
    entries = PlannerEntry.query.filter_by(week_start=week_start).all()
    
    try:
        pdf_content = render_template('pdf_template.html', entries=entries)
        pdf_file = HTML(string=pdf_content).write_pdf()
    except Exception as e:
        flash(f"Fehler bei der PDF-Generierung: {str(e)}", "error")
        return redirect(url_for('main.home'))

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
        if new_subject and new_subject.strip():
            new_subject = new_subject.strip()
            if len(new_subject) > 100:
                flash("Der Fachname darf maximal 100 Zeichen lang sein.", "error")
                return redirect(url_for('main.settings'))
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
