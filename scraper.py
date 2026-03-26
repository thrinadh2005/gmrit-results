"""
Web scraper module for GMRIT Results
"""
import os
import time
import base64
import traceback
import subprocess
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    CHROME_OPTIONS, MAX_RETRIES, RETRY_DELAY,
    PAGE_LOAD_TIMEOUT, IMPLICIT_WAIT, EXAM_TYPE, VIEW_TYPE,
    HTML_DIR, PDF_DIR
)
from logger import logger

# Cache for the ChromeDriver path to avoid redundant downloads/checks
_cached_driver_path = None

def get_driver_path():
    """Get the ChromeDriver path, using cache if available"""
    global _cached_driver_path
    if _cached_driver_path is None:
        try:
            logger.info("Checking for ChromeDriver updates...")
            _cached_driver_path = ChromeDriverManager().install()
        except Exception as e:
            logger.warning(f"Failed to get driver via manager: {e}")
            return None
    return _cached_driver_path

class Scraper:
    """Web scraper for GMRIT results"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def find_chrome_executable(self):
        """Find Chrome executable on the system"""
        names = ['chrome', 'google-chrome', 'chromium', 'chrome.exe']
        for name in names:
            path = shutil.which(name)
            if path:
                return path
        # Common Windows path
        common = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        if os.path.exists(common):
            return common
        return None
    
    def create_driver(self):
        """Create and return a WebDriver instance with robust fallback mechanisms"""
        options = Options()
        for option in CHROME_OPTIONS:
            options.add_argument(option)
        
        # Set preferences for PDF download
        prefs = {
            "printing.print_preview_sticky_settings.had_selection": False,
            "printing.default_printer_selection.selected_printer_name": "",
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.notifications": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        # Binary location detection (especially important for Render/Docker)
        chrome_bin = self.find_chrome_executable()
        if chrome_bin:
            options.binary_location = chrome_bin
            logger.info(f"Using Chrome binary at: {chrome_bin}")

        try:
            logger.info("Initializing Chrome WebDriver (Method 1: ChromeDriverManager)...")
            try:
                driver_path = get_driver_path()
                if driver_path:
                    self.driver = webdriver.Chrome(
                        service=Service(driver_path),
                        options=options
                    )
                else:
                    raise Exception("ChromeDriver path not available")
            except Exception as e1:
                logger.warning(f"Method 1 failed: {str(e1)}")
                logger.info("Attempting Method 2: System Chrome...")
                # Try to use system chrome without driver manager (requires chromedriver in path)
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT)
            logger.success("WebDriver initialized successfully")
            return True
        except Exception as e:
            error_msg = str(e).split('\n')[0]  # Get first line of error
            logger.error(f"Failed to initialize WebDriver: {error_msg}")
            # Log full traceback for debugging in the log file
            logger.debug(traceback.format_exc())
            return False
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.success("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {str(e)}")
    
    def process_hallticket(self, hallticket, output_dir=None):
        """Process a single hall ticket and return the result"""
        result = {
            'hallticket': hallticket,
            'success': False,
            'pdf_path': None,
            'html_path': None,
            'error': None
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Processing {hallticket} (Attempt {attempt + 1}/{MAX_RETRIES})")
                
                # Navigate to results page
                self.driver.get("https://gmrit.campx.in/gmrit/ums/results")
                # Wait for rollNo element specifically instead of static sleep
                hall_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, "rollNo"))
                )
                
                hall_input.clear()
                hall_input.send_keys(hallticket)
                
                # Select exam type
                self._select_dropdown("examType", EXAM_TYPE)
                
                # Select view type
                self._select_dropdown("viewType", VIEW_TYPE)
                
                # Click Get Result button
                self._click_get_result()
                
                # Wait for the result table or a specific element that confirms result loaded
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                
                # Save page source to HTML directory
                html_path = os.path.join(HTML_DIR, f"{hallticket}_page_source.html")
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                result['html_path'] = html_path
                
                # Generate PDF to PDF directory
                pdf_path = self._generate_pdf(PDF_DIR, hallticket)
                if pdf_path:
                    result['pdf_path'] = pdf_path
                    result['success'] = True
                    logger.success(f"✓ Successfully processed {hallticket}")
                    return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    result['error'] = str(e)
        
        return result
    
    def _select_dropdown(self, dropdown_id, value):
        """Select value from dropdown with optimized script execution"""
        try:
            dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, dropdown_id))
            )
            self.driver.execute_script("arguments[0].click();", dropdown)
            
            # Wait for the dropdown options to appear in the DOM
            option_xpath = f"//li[contains(text(), '{value}')]"
            try:
                option = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, option_xpath))
                )
                self.driver.execute_script("arguments[0].click();", option)
            except:
                # Fallback: check all options via script for speed
                self.driver.execute_script(f"""
                    var options = document.querySelectorAll('li');
                    var value = '{value}'.toLowerCase();
                    for (var i = 0; i < options.length; i++) {{
                        if (options[i].textContent.toLowerCase().includes(value)) {{
                            options[i].click();
                            return true;
                        }}
                    }}
                    if (options.length > 0) options[0].click();
                """)
            
            logger.info(f"✓ Selected {dropdown_id}: {value}")
        except Exception as e:
            logger.warning(f"Could not select {dropdown_id}: {str(e)}")

    def _click_get_result(self):
        """Click the Get Result button using script for speed"""
        try:
            btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Get Result')]"))
            )
            self.driver.execute_script("arguments[0].click();", btn)
            logger.info("✓ Clicked Get Result button")
        except Exception as e:
            logger.warning(f"Could not click Get Result button: {str(e)}")
    
    def _generate_pdf(self, output_dir, hallticket):
        """Generate PDF from the current page"""
        pdf_path = os.path.join(output_dir, f"{hallticket}_results.pdf")
        
        print_options = {
            "paperWidth": 8.5,
            "paperHeight": 11,
            "marginTop": 0.4,
            "marginBottom": 0.4,
            "marginLeft": 0.4,
            "marginRight": 0.4,
            "displayHeaderFooter": False,
            "printBackground": True,
            "landscape": False
        }
        
        try:
            result = self.driver.execute_cdp_cmd('Page.printToPDF', print_options)
            pdf_data = base64.b64decode(result['data'])
            with open(pdf_path, 'wb') as f:
                f.write(pdf_data)
            logger.success(f"✓ PDF created: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.warning(f"PDF generation failed: {str(e)}")
            # Fallback: save screenshot
            screenshot_path = os.path.join(output_dir, f"{hallticket}_results.png")
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"✓ Screenshot saved: {screenshot_path}")
            return screenshot_path

# Global scraper instance for convenience
_global_scraper = None

def get_scraper():
    """Get or create global scraper instance (Not thread-safe)"""
    global _global_scraper
    if _global_scraper is None:
        _global_scraper = Scraper()
        if not _global_scraper.create_driver():
            _global_scraper = None  # Reset so we can try again
            return None
    return _global_scraper

def scrape_student_results(hall_ticket, output_dir=None):
    """
    Main entry point for scraping a student's results.
    Creates a new scraper instance for thread safety.
    """
    from config import HTML_DIR
    output_dir = output_dir or HTML_DIR
    
    scraper = Scraper()
    if not scraper.create_driver():
        # Fallback to global scraper if thread-local fails (rare)
        logger.warning(f"Failed to create new driver for {hall_ticket}, attempting fallback...")
        scraper = get_scraper()
        if not scraper:
            return {
                'success': False,
                'hall_ticket': hall_ticket,
                'error': 'Failed to initialize Chrome WebDriver'
            }
    
    try:
        result = scraper.process_hallticket(hall_ticket, output_dir)
        
        # Map Scraper.process_hallticket result to app.py expected format
        return {
            'success': result['success'],
            'hall_ticket': hall_ticket,
            'html_file': result['html_path'],
            'pdf_file': result['pdf_path'],
            'error': result['error'],
            'message': 'Successfully scraped' if result['success'] else f"Failed: {result['error']}"
        }
    finally:
        # Only close if it's a dedicated instance, not the global one
        if scraper != _global_scraper:
            scraper.close_driver()
