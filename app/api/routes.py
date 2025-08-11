from flask import jsonify

from . import api_bp


@api_bp.route('/health')
def health_check():
    """
    Gibt den aktuellen Gesundheitsstatus und die Versionsnummer des Dienstes als JSON-Antwort zurück.
    
    Returns:
        Response: JSON-Objekt mit den Schlüsseln "status" und "version".
    """
    return jsonify({'status': 'healthy', 'version': '1.0.0'})
