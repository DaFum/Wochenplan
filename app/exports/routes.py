from datetime import datetime, timedelta

from flask import send_file
from weasyprint import HTML

from app.modules.ical_exporter import ICalExporter
from app.modules.task_manager import TaskManager
from . import exports_bp

ical_exporter = ICalExporter()
task_manager = TaskManager()


@exports_bp.route('/download-ical')
def download_ical():
    tasks = task_manager.list_tasks()
    events = []
    for task in tasks:
        events.append({
            "summary": task.title,
            "start": datetime.now(),
            "end": datetime.now() + timedelta(hours=1),
            "description": getattr(task, 'description', '') or ''
        })

    file_path = "wochenplan.ics"
    ical_exporter.export_to_file(events, file_path)

    return send_file(
        file_path,
        as_attachment=True,
        download_name='wochenplan.ics',
        mimetype='text/calendar'
    )

@exports_bp.route('/download-pdf')
def download_pdf():
    # This is a placeholder for PDF generation
    html = HTML(string="<h1>Wochenplan</h1><p>This is a placeholder PDF.</p>")
    pdf = html.write_pdf()
    return send_file(
        pdf,
        as_attachment=True,
        download_name='wochenplan.pdf',
        mimetype='application/pdf'
    )
