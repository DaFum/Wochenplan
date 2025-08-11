import logging
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)

from pollinations.text import Text

from .forms import PlannerForm
from app.modules.task_manager import TaskStatus


logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]


@main_bp.route('/', methods=['GET', 'POST'])
def home():
    """
    Zeigt die Startseite mit Aufgabenliste, Fächern, Formular und optional generiertem Text an.
    
    Bei Formularübermittlung mit Kontext 'add_task' wird eine neue Aufgabe hinzugefügt und eine entsprechende Rückmeldung angezeigt. Die Seite zeigt alle aktuellen Aufgaben, verfügbare Fächer, das Planungsformular sowie gegebenenfalls zuvor generierten Text an.
    """
    form = PlannerForm()
    try:
        form.learning_subject.choices = current_app.content_library.get_subjects()
    except Exception as e:
        logger.error(f"Failed to load subjects: {e}")
        form.learning_subject.choices = []
        flash("Fächer konnten nicht geladen werden.", "warning")

    if form.validate_on_submit() and request.form.get('form_context') == 'add_task':
        try:
            current_app.task_manager.add_task(title=form.learning_task.data)
            flash("Aufgabe erfolgreich hinzugefügt!", "success")
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            flash("Ein Fehler ist aufgetreten.", "error")
        return redirect(url_for('main.home'))

    tasks = current_app.task_manager.list_tasks()
    generated_text = session.pop('generated_text', None)
    return render_template(
        'index.html',
        tasks=tasks,
        subjects=current_app.content_library.get_subjects(),
        form=form,
        generated_text=generated_text
    )


@main_bp.route('/einstellungen', methods=['GET', 'POST'])
def settings():
    """
    Rendert die Einstellungsseite und ermöglicht das Hinzufügen oder Entfernen von Fächern.
    """
    if request.method == 'POST':
        action = request.form.get('action')
        subject = request.form.get('subject')
        if action == 'add' and subject:
            current_app.content_library.add_subject(subject)
        elif action == 'remove' and subject:
            current_app.content_library.remove_subject(subject)
        return redirect(url_for('main.settings'))

    subjects = current_app.content_library.get_subjects()
    return render_template('settings.html', subjects=subjects)


@main_bp.route('/task/<task_id>/reorder', methods=['POST'])
def reorder_task(task_id):
    """Aktualisiert die Reihenfolge der Aufgaben."""
    new_position = request.json.get('position')
    if new_position is None:
        return {'error': 'Position missing'}, 400
    if current_app.task_manager.reorder_task(task_id, int(new_position)):
        return {'status': 'ok'}
    return {'error': 'Task not found'}, 404


@main_bp.route('/task/<task_id>/update', methods=['POST'])
def update_task(task_id):
    """Aktualisiert Titel oder Beschreibung einer Aufgabe."""
    title = request.form.get('title')
    description = request.form.get('description')
    if current_app.task_manager.update_task(task_id, title=title, description=description):
        flash("Aufgabe aktualisiert.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))


@main_bp.route('/task/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Löscht eine Aufgabe."""
    if current_app.task_manager.delete_task(task_id):
        flash("Aufgabe gelöscht.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))


@main_bp.route('/task/<task_id>/status', methods=['POST'])
def change_status(task_id):
    """Ändert den Status einer Aufgabe."""
    status_name = request.form.get('status')
    try:
        status = TaskStatus[status_name]
    except KeyError:
        return {'error': 'Invalid status'}, 400
    if current_app.task_manager.update_task_status(task_id, status):
        flash("Status aktualisiert.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))


@main_bp.route('/send-reminder/<task_id>')
def send_reminder(task_id):
    """
    Sendet eine Erinnerungsbenachrichtigung für eine bestimmte Aufgabe an die im Nutzer-Session hinterlegte E-Mail-Adresse.
    
    Parameters:
        task_id (str): Die ID der Aufgabe, für die eine Erinnerung gesendet werden soll.
    
    Gibt eine Erfolgsmeldung aus, wenn die Aufgabe gefunden wurde und die Erinnerung gesendet wurde, andernfalls eine Fehlermeldung. Leitet anschließend zur Startseite weiter.
    """
    task = current_app.task_manager.get_task(task_id)
    if task:
        current_app.notification_service.send_reminder(
            recipient=session.get('user_email', 'default@example.com'),
            message=f"Erinnerung für: {task.title}",
            event_time=datetime.now() + timedelta(minutes=15)
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
            with Text() as text_generator:
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
