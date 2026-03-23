"""
GMRIT Results Scraper - Production Runner
Simple production-ready launcher
"""
import os
import sys
from app import app

if __name__ == '__main__':
    # Ensure necessary directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('html_pages', exist_ok=True)
    os.makedirs('pdfs', exist_ok=True)
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting GMRIT Results Scraper Web Interface...")
    print(f"Access application at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    print("Render deployment optimized - Chrome/Selenium fixed")
    print("-" * 50)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
