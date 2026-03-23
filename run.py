"""
GMRIT Results Scraper - Production Runner
Simple production-ready launcher
"""
import os
import sys
from app import app

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('html_pages', exist_ok=True)
    os.makedirs('pdfs', exist_ok=True)
    
    print("Starting GMRIT Results Scraper Web Interface...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run in production mode
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
