"""
GMRIT Results Scraper - Desktop Launcher
Wraps the Flask web interface in a native desktop window
"""
import os
import sys
import threading
import time
import webview
from app import app
from config import BASE_DIR

def start_flask():
    """Start the Flask server in a separate thread"""
    port = 5000
    try:
        app.run(host='127.0.0.1', port=port, debug=False, threaded=True)
    except Exception as e:
        print(f"Error starting Flask: {e}")

def main():
    """Main desktop entry point"""
    # Create necessary directories
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'html_pages'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'pdfs'), exist_ok=True)
    
    # Start Flask in a daemon thread
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    # Wait a bit for Flask to initialize
    time.sleep(2)
    
    # Create the native window
    window = webview.create_window(
        'GMRIT Results Scraper',
        'http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    
    # Start the webview GUI loop
    webview.start()

if __name__ == '__main__':
    main()
