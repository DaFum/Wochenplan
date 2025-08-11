# ============================================================
# Main Routes Module - Updated to address PR review feedback
# ============================================================
import logging
import os
from datetime import datetime, timedelta

import httpx
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
    jsonify,
)
from werkzeug.utils import secure_filename

from pollinations.text import Text
from pollinations.image import Image as PollinationsImage

from .forms import PlannerForm, SubjectForm
from app.modules.task_manager import TaskStatus
from app.models import TaskPriority


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
        subjects = current_app.content_library.get_subjects()
        form.learning_subject.choices = subjects
    except AttributeError as e:
        logger.error(f"Failed to load subjects: {e}")
        subjects = []
        form.learning_subject.choices = []
        flash("Fächer konnten nicht geladen werden.", "warning")

    if form.validate_on_submit() and request.form.get('form_context') == 'add_task':
        try:
            try:
                priority = TaskPriority[form.priority.data]
            except KeyError:
                flash("Ungültige Priorität ausgewählt.", "error")
                return redirect(url_for('main.home'))
            current_app.task_manager.add_task(
                title=form.learning_task.data,
                priority=priority,
                due_date=form.due_date.data,
            )
            flash("Aufgabe erfolgreich hinzugefügt!", "success")
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            flash("Ein Fehler ist aufgetreten.", "error")
        return redirect(url_for('main.home'))

    tasks = current_app.task_manager.list_tasks()
    # Add image URLs to tasks
    with PollinationsImage() as image_client:
        for t in tasks:
    for t in tasks:
            t.image_url = image_client.url(f"{t.title} icon", width=256, height=256)
            t.image_url = image_client.url(f"{t.title} icon", width=256, height=256)
    
    
    generated_text = session.pop('generated_text', None)
    return render_template(
        'index.html',
        tasks=tasks,
        subjects=subjects,
        days=WEEKDAYS,
        form=form,
        generated_text=generated_text
    )


@main_bp.route('/einstellungen', methods=['GET', 'POST'])
def settings():
    """Rendert die Einstellungsseite und ermöglicht das Hinzufügen oder Entfernen von Fächern."""
    form = SubjectForm()
    
    # Handle subject removal with proper CSRF protection
    if request.method == 'POST' and request.form.get('action') == 'remove':
        # This should be improved to use proper form validation
        subject = request.form.get('subject')
        try:
            if subject:
                current_app.content_library.remove_subject(subject)
                flash(f"Fach '{subject}' entfernt.", "success")
        except Exception as e:
            logger.error(f"Error managing subjects: {e}")
            flash("Fehler beim Verwalten der Fächer.", "error")
        return redirect(url_for('main.settings'))

    # Handle subject addition
    if form.validate_on_submit():
        subject = form.new_subject.data.strip()
        try:
            if current_app.content_library.add_subject(subject):
                image_generated = False
                try:
                    filename = secure_filename(f"{subject}.png")
                    folder = os.path.join(current_app.static_folder, 'subjects')
                    os.makedirs(folder, exist_ok=True)
                    path = os.path.join(folder, filename)
                    with PollinationsImage() as img_client:
                        img_client(
                            prompt=f"school subject {subject} icon",
                            save=True,
                            file=path,
                            width=256,
                            height=256,
                        )
                    image_generated = True
                except Exception as img_err:
                    logger.error(f"Image generation failed for subject {subject}: {img_err}")
                
                if image_generated:
                    flash(f"Fach '{subject}' hinzugefügt.", "success")
                else:
                    flash(f"Fach '{subject}' hinzugefügt, aber das Icon konnte nicht generiert werden.", "warning")
            else:
                flash("Fach konnte nicht hinzugefügt werden.", "error")
        except Exception as e:
            logger.error(f"Error managing subjects: {e}")
            flash("Fehler beim Verwalten der Fächer.", "error")
        return redirect(url_for('main.settings'))

    try:
        subjects = current_app.content_library.list_subjects_with_task_counts()
    except Exception as e:
        logger.error(f"Failed to load subjects: {e}")
        subjects = []
        flash("Fächer konnten nicht geladen werden.", "warning")
    return render_template('settings.html', subjects=subjects, form=form)


@main_bp.route('/task/<int:task_id>/reorder', methods=['POST'])
def reorder_task(task_id):
    """Aktualisiert die Reihenfolge der Aufgaben."""
    data = request.get_json(silent=True) or {}
    if 'position' not in data:
        return {'error': 'Position missing'}, 400
    try:
        new_position = int(data['position'])
    except (TypeError, ValueError):
        return {'error': 'Position must be an integer'}, 400
    if current_app.task_manager.reorder_task(task_id, new_position):
        return {'status': 'ok'}
    return {'error': 'Task not found'}, 404


@main_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Zeigt ein Formular zur Bearbeitung einer Aufgabe und speichert Änderungen."""
    task = current_app.task_manager.get_task(task_id)
    if not task:
        flash("Aufgabe nicht gefunden.", "error")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description')

        if not title:
            flash("Titel darf nicht leer sein.", "error")
            return redirect(url_for('main.edit_task', task_id=task_id))

        if current_app.task_manager.update_task(task_id, title=title, description=description):
            flash("Aufgabe aktualisiert.", "success")
        else:
            flash("Aktualisierung fehlgeschlagen.", "error")
        return redirect(url_for('main.home'))

    return render_template('edit_task.html', task=task)


@main_bp.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Löscht eine Aufgabe."""
    if current_app.task_manager.delete_task(task_id):
        flash("Aufgabe gelöscht.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))


@main_bp.route('/task/<int:task_id>/status', methods=['POST'])
def change_status(task_id):
    """Ändert den Status einer Aufgabe."""
    status_name = request.form.get('status')
    try:
        status = TaskStatus[status_name]
    except KeyError:
        flash("Ungültiger Status.", "error")
        return redirect(url_for('main.home'))
    if current_app.task_manager.update_task_status(task_id, status):
        flash("Status aktualisiert.", "success")
    else:
        flash("Aufgabe nicht gefunden.", "error")
    return redirect(url_for('main.home'))


@main_bp.route('/send-reminder/<int:task_id>', methods=['POST'])
def send_reminder(task_id):
    """
    Sendet eine Erinnerungsbenachrichtigung für eine bestimmte Aufgabe an die im Nutzer-Session hinterlegte E-Mail-Adresse.
    
    Parameters:
        task_id (int): Die ID der Aufgabe, für die eine Erinnerung gesendet werden soll.
    
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
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    prompt = request.form.get('prompt')

    message = None
    status_code = 500

    if not prompt:
        message = "Kein Prompt übergeben."
        status_code = 400
    else:
        try:
            with Text() as text_generator:
                generated_text = text_generator(prompt)

            if is_ajax:
                return jsonify({'generated_text': generated_text})

            session['generated_text'] = generated_text
            return redirect(url_for('main.home'))

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logger.warning(f"HTTP-Verbindungsfehler während der Textgenerierung: {e}")
            message = "Verbindungsfehler bei der Textgenerierung. Bitte versuchen Sie es später erneut."
            status_code = 503
        except httpx.HTTPError as e:
            logger.warning(f"HTTP-Fehler während der Textgenerierung: {e}")
            message = "HTTP-Fehler bei der Textgenerierung. Bitte versuchen Sie es später erneut."
            status_code = 502
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            message = "Textgenerierung fehlgeschlagen. Bitte versuchen Sie es erneut."
            status_code = 500

    if is_ajax:
        return jsonify({'error': message}), status_code

    flash(message, "error")
    return redirect(url_for('main.home'))
