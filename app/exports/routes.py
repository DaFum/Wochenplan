from datetime import datetime, timedelta

from flask import send_file
from weasyprint import HTML

from app.modules.ical_exporter import ICalExporter
from app.modules.task_manager import TaskManager
from . import exports_bp

ical_exporter = ICalExporter()
task_manager = TaskManager()


import io


@exports_bp.route('/download-ical')
def download_ical():
    tasks = task_manager.list_tasks()
    events = []
    for task in tasks:
        start_time = task.start_time or datetime.now()
        end_time = task.end_time or start_time + timedelta(hours=1)
        events.append({
            "summary": task.title,
            "start": start_time,
            "end": end_time,
            "description": getattr(task, 'description', '') or ''
        })

    ical_string = ical_exporter.export_to_memory(events)
    if ical_string is None:
        return "Could not generate iCal file.", 500

    return send_file(
        io.BytesIO(ical_string.encode('utf-8')),
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
