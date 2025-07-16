import logging
from datetime import datetime, timedelta

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from app.modules.content_library import ContentLibrary
from app.modules.ical_exporter import ICalExporter
from app.modules.notification_service import NotificationService
from app.modules.task_manager import TaskManager
from pollinations.text import Text

from .forms import PlannerForm

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

    if form.validate_on_submit() and request.form.get('form_context') == 'add_task':
        try:
            task_manager.add_task(title=form.learning_task.data)
            flash("Aufgabe erfolgreich hinzugefügt!", "success")
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            flash("Ein Fehler ist aufgetreten.", "error")
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


@main_bp.route('/send-reminder/<task_id>')
def send_reminder(task_id):
    task = task_manager.get_task(task_id)
    if task:
        notification_service.send_reminder(
            recipient=session.get('user_email', 'default@example.com'),
            message=f"Erinnerung für: {task.title}",
            event_time=datetime.now() + timedelta(minutes=15)
        )
        flash(f"Erinnerung für '{task.title}' gesendet.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))

logger = logging.getLogger(__name__)


@main_bp.route('/generate-text', methods=['POST'])
def generate_text():
    prompt = request.form.get('prompt')
    if prompt:
        try:
            text_generator = Text()
            generated_text = text_generator(prompt)
            session['generated_text'] = generated_text
        except (ConnectionError, TimeoutError):
            flash(
                "Verbindungsfehler bei der Textgenerierung. "
                "Bitte versuchen Sie es später erneut.",
                "error"
            )
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            flash(
                "Textgenerierung fehlgeschlagen. Bitte versuchen Sie es erneut.",
                "error"
            )
    return redirect(url_for('main.home'))
