from flask import jsonify

from . import api_bp


@api_bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})
