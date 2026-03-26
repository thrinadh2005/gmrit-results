"""
Configuration settings for GMRIT Results Scraper
"""
import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "gmrit_results_pdf")
HTML_DIR = os.path.join(BASE_DIR, "html_pages")
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create directories if not exist
for directory in [OUTPUT_DIR, HTML_DIR, PDF_DIR, DATA_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Files
HALLTICKETS_FILE = os.path.join(DATA_DIR, "halltickets.txt")
LOG_FILE = os.path.join(BASE_DIR, "execution_log.txt")
EXCEL_FILE = os.path.join(BASE_DIR, "gmrit_results.xlsx")

# Webdriver settings
EXAM_TYPE = "General"
VIEW_TYPE = "All Semesters"

# Chrome options
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-sync",
    "--disable-notifications",
    "--disable-popup-blocking",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "--window-size=1920,1080",
]

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Timeouts
PAGE_LOAD_TIMEOUT = 60
IMPLICIT_WAIT = 15
PAGE_LOAD_STRATEGY = "eager"  # Options: normal, eager, none
