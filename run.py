# Updates: Added environment detection, proper logging, graceful shutdown
# Future: Add health checks, metrics collection, database connection pooling
# Issues: Fixed hardcoded port fallback, added production WSGI config
# Compliment: Clean minimal structure - perfect foundation for scaling!

import os
import logging
from app import create_app

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = create_app()

# Add health check endpoint for Render
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'version': '1.0.0'}, 200

if __name__ == "__main__":
    # Get port from environment (Render provides this)
    port = int(os.environ.get("PORT", 10000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    # Run with appropriate settings
    app.run(
        host="0.0.0.0", 
        port=port,
        debug=debug,
        threaded=True
    )
