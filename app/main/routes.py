from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import db
from .forms import PlannerForm
from datetime import datetime, timedelta
import io
from weasyprint import HTML
from app.modules.content_library import ContentLibrary
from app.modules.task_manager import TaskManager, TaskStatus
from app.modules.ical_exporter import ICalExporter
from app.modules.notification_service import NotificationService
from pollinations.text import Text

main_bp = Blueprint('main', __name__)

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

content_library = ContentLibrary()
task_manager = TaskManager()
ical_exporter = ICalExporter()
notification_service = NotificationService()



@main_bp.route('/', methods=['GET', 'POST'])
def home():
    form = PlannerForm()
    try:
        form.learning_subject.choices = content_library.get_subjects()
    except Exception as e:
        logger.error(f"Failed to load subjects: {e}")
        form.learning_subject.choices = []
        flash("Fächer konnten nicht geladen werden.", "warning")

    if form.validate_on_submit():
        try:
            task_manager.add_task(title=form.learning_task.data)
            flash("Aufgabe erfolgreich hinzugefügt!", "success")
        except Exception as e:
            flash(f"Ein Fehler ist aufgetreten: {str(e)}", "error")
        return redirect(url_for('main.home'))

    tasks = task_manager.list_tasks()
    generated_text = session.pop('generated_text', None)
    return render_template(
        'index.html',
        tasks=tasks,
        subjects=content_library.get_subjects(),
        form=form,
        generated_text=generated_text
    )


@main_bp.route('/einstellungen', methods=['GET'])
def settings():
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
        events.append({
            "summary": task.title,
            "start": task_start,
            "end": task_end,
            "description": getattr(task, 'description', '') or ''
        })
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

@main_bp.route('/generate-text', methods=['POST'])
def generate_text():
    prompt = request.form.get('prompt')
    if prompt:
        try:
            text_generator = Text()
            generated_text = text_generator(prompt)
            session['generated_text'] = generated_text
        except (ConnectionError, TimeoutError) as e:
            flash("Verbindungsfehler bei der Textgenerierung. Bitte versuchen Sie es später erneut.", "error")
        except Exception as e:
            flash("Textgenerierung fehlgeschlagen. Bitte versuchen Sie es erneut.", "error")
            # Log the actual error for debugging
            logger.error(f"Text generation failed: {e}")
    return redirect(url_for('main.home'))
