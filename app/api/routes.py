from flask import jsonify, current_app

from . import api_bp


@api_bp.route('/health')
def health_check():
    """
    Gibt den aktuellen Gesundheitsstatus und die Versionsnummer des Dienstes als JSON-Antwort zurück.
    
    Returns:
        Response: JSON-Objekt mit den Schlüsseln "status" und "version".
    """
    return jsonify({'status': 'healthy', 'version': '1.0.0'})


@api_bp.route('/library-tasks/<subject>')
def library_tasks(subject):
    """Return preset tasks for a given subject from the content library."""
    try:
        tasks = current_app.content_library.get_tasks_for_subject(subject)
    except Exception as e:
        current_app.logger.error(f"Error fetching library tasks for subject '{subject}': {e}")
        return jsonify({'tasks': []}), 400
    return jsonify({'tasks': tasks})
