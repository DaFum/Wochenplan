from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import db
from app.models import PlannerEntry, Subject
from .forms import PlannerForm
from datetime import datetime, timedelta
import random
import io
import json
from weasyprint import HTML
from src.modules.content_library import ContentLibrary
from src.modules.task_manager import TaskManager, TaskStatus
from src.modules.ical_exporter import ICalExporter
from src.modules.notification_service import NotificationService

main_bp = Blueprint('main', __name__)

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

content_library = ContentLibrary()
task_manager = TaskManager()
ical_exporter = ICalExporter()
notification_service = NotificationService()

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
            # For simplicity, we'll create a single task from the form
            title = form.learning_subject.data.name if form.learning_subject.data else "Lernaufgabe"
            description = form.learning_task.data
            task_manager.add_task(title=title, description=description)
            flash("Aufgabe erfolgreich hinzugefügt!", "success")
        except Exception as e:
            flash(f"Ein Fehler ist aufgetreten: {str(e)}", "error")
        return redirect(url_for('main.home'))

    if 'tasks_used' not in session:
        session['tasks_used'] = {day: [] for day in WEEKDAYS}

    random_data = {
        day: {
            "task": get_random_item(content_library.get_tasks_for_subject("Allgemein"), session['tasks_used'][day]),
            "tip": ""  # Tips are not available in the content library
        } for day in WEEKDAYS
    }

    tasks = task_manager.list_tasks()
    return render_template('index.html', tasks=tasks, subjects=content_library.get_subjects(), form=form)

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
        # The ability to add new subjects is removed as we now use the content library
        flash("Das Hinzufügen neuer Fächer ist nicht mehr möglich.", "info")
        return redirect(url_for('main.settings'))

    subjects = content_library.get_subjects()
    return render_template('settings.html', subjects=subjects)

@main_bp.route('/download-ical')
def download_ical():
    tasks = task_manager.list_tasks()
    events = []
    for task in tasks:
        events.append({
            "summary": task.title,
            "start": datetime.now(),
            "end": datetime.now() + timedelta(hours=1),
            "description": task.description
        })

    file_path = "wochenplan.ics"
    ical_exporter.export_to_file(events, file_path)

    return send_file(
        file_path,
        as_attachment=True,
        download_name='wochenplan.ics',
        mimetype='text/calendar'
    )

@main_bp.route('/send-reminder/<task_id>')
def send_reminder(task_id):
    task = task_manager.get_task(task_id)
    if task:
        notification_service.send_reminder(
            recipient="user@example.com",  # In a real app, this would be the logged-in user's email
            message=f"Erinnerung für: {task.title}",
            event_time=datetime.now() + timedelta(minutes=15) # Placeholder time
        )
        flash(f"Erinnerung für '{task.title}' gesendet.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))
