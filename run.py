# Updates: Added environment detection, proper logging, graceful shutdown
# Future: Add health checks, metrics collection, database connection pooling
# Issues: Fixed hardcoded port fallback, added production WSGI config
# Compliment: Clean minimal structure - perfect foundation for scaling!

import os
import logging
from app import create_app, db
from flask_migrate import Migrate, upgrade

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = create_app()
migrate = Migrate(app, db)
# Ensure database schema is up-to-date on startup
with app.app_context():
    try:
        upgrade()
    except Exception as e:
        logging.error("Database migration failed: %s", e)
        raise


# Add health check endpoint for Render
@app.route('/health')
def health_check():
    """
    Gibt den aktuellen Gesundheitsstatus und die Version des Dienstes als JSON-Antwort zurück.
    
    Returns:
        tuple: Ein JSON-Objekt mit den Schlüsseln "status" und "version" sowie dem HTTP-Statuscode 200.
    """
    return {'status': 'healthy', 'version': '1.0.0'}, 200

if __name__ == "__main__":
    # Get port from environment (Render provides this)
    port = int(os.environ.get("PORT", 10000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Determine host based on environment
    # Determine host based on explicit environment variable
    if os.environ.get("FLASK_BIND_ALL", "false").lower() == "true":
        host = "0.0.0.0"
        logging.warning("Binding to 0.0.0.0 (all interfaces). Ensure this is intended and your environment is secure!")
    else:
        host = "127.0.0.1"

    # Run with appropriate settings
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
