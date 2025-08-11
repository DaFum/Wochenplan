from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import io

from flask import send_file, render_template, current_app
from weasyprint import HTML

from app.modules.ical_exporter import ICalExporter
from app.modules.task_manager import TaskManager
from . import exports_bp

import logging
logger = logging.getLogger(__name__)

ical_exporter = ICalExporter()
task_manager = TaskManager()
@exports_bp.route('/download-ical')
def download_ical():
    """
    Exportiert alle Aufgaben als iCal-Datei zum Download.
    
    Gibt eine iCal-Datei mit allen aktuellen Aufgaben als Download zurück. Bei Fehlern während der Generierung wird eine entsprechende Fehlermeldung mit HTTP-Status 500 ausgegeben.
    """
    tasks = task_manager.list_tasks()
    events = []
    tz = ZoneInfo(current_app.config.get('DEFAULT_TIMEZONE', 'Europe/Berlin'))
    for task in tasks:
        start_time = task.due_date or datetime.now(tz)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=tz)
        else:
            start_time = start_time.astimezone(tz)
        end_time = start_time + timedelta(hours=1)
        events.append({
            "summary": task.title,
            "start": start_time,
            "end": end_time,
            "description": getattr(task, 'description', '') or '',
            "uid": f"task-{task.id}@wochenplan",
            "dtstamp": datetime.now(timezone.utc),
        })

    try:
        ical_string = ical_exporter.export_to_memory(events)
        if ical_string is None:
            logger.error("ICalExporter returned None")
            return "Fehler bei der iCal-Generierung.", 500
    except Exception as e:
        logger.error(f"Fehler beim iCal-Export: {e}")
        return "Interner Serverfehler.", 500

    return send_file(
        io.BytesIO(ical_string.encode('utf-8')),
        as_attachment=True,
        download_name='wochenplan.ics',
        mimetype='text/calendar'
    )

@exports_bp.route('/download-pdf')
def download_pdf():
    """
    Exportiert die Aufgabenliste als PDF-Datei und stellt sie zum Download bereit.
    
    Die Funktion rendert die Aufgaben mit einer HTML-Vorlage, wandelt das Ergebnis in eine PDF-Datei um und liefert diese als Download mit dem Dateinamen 'wochenplan.pdf' und dem MIME-Typ 'application/pdf' aus.
    """
    tasks = task_manager.list_tasks()
    rendered_html = render_template('pdf_template.html', tasks=tasks)
    html = HTML(string=rendered_html)
    pdf = io.BytesIO()
    html.write_pdf(target=pdf)
    pdf.seek(0)
    return send_file(
        pdf,
        as_attachment=True,
        download_name='wochenplan.pdf',
        mimetype='application/pdf'
    )
