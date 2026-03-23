"""
Logger module for GMRIT Results Scraper
"""
import os
from datetime import datetime
from config import LOG_FILE

class Logger:
    def __init__(self, log_file=None):
        self.log_file = log_file or LOG_FILE
        
    def _write(self, message, to_console=True):
        """Write message to log file and optionally to console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if to_console:
            try:
                print(log_entry)
            except UnicodeEncodeError:
                print(log_entry.encode('ascii', errors='replace').decode('ascii'))
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def info(self, message):
        self._write(f"INFO: {message}")
    
    def success(self, message):
        self._write(f"SUCCESS: {message}")
    
    def warning(self, message):
        self._write(f"WARNING: {message}")
    
    def error(self, message):
        self._write(f"ERROR: {message}")
    
    def debug(self, message):
        self._write(f"DEBUG: {message}")
    
    def separator(self, char="=", length=80):
        self._write(char * length)
    
    def clear_log(self):
        """Clear the log file"""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

# Global logger instance
logger = Logger()
