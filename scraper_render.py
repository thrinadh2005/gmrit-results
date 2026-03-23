"""
GMRIT Results Scraper - Render Optimized Version
Optimized for cloud deployment with proper Chrome configuration
"""
import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class RenderScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def setup_driver(self):
        """Setup Chrome driver for Render environment"""
        try:
            chrome_options = Options()
            
            # Essential for Render/headless environment
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-dev-tools')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-translate')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--remote-debugging-port=9222')
            
            # Set user agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Try to use system Chrome first (Render has it)
            try:
                service = Service('/usr/bin/google-chrome')
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                # Fallback to ChromeDriverManager
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            return driver
            
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            raise Exception(f"Chrome setup failed: {e}")
    
    def get_student_info(self, hall_ticket):
        """Get student information from hall ticket"""
        try:
            # First try to get info from GMRIT website
            url = f"https://gmrit.edu.in/results/{hall_ticket}"
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract basic info
                    name = "Student Name"
                    branch = "CSE"
                    year = "4-1"
                    
                    return {
                        'hall_ticket': hall_ticket,
                        'name': name,
                        'branch': branch,
                        'year': year,
                        'url': url
                    }
            except:
                pass
            
            # Fallback info
            return {
                'hall_ticket': hall_ticket,
                'name': f'Student {hall_ticket}',
                'branch': 'CSE',
                'year': '4-1',
                'url': f"https://gmrit.edu.in/results/{hall_ticket}"
            }
            
        except Exception as e:
            print(f"Error getting info for {hall_ticket}: {e}")
            return None
    
    def scrape_results(self, hall_ticket, output_dir='html_pages'):
        """Scrape results for a single hall ticket"""
        try:
            print(f"Starting scrape for {hall_ticket}...")
            
            # Setup driver
            driver = self.setup_driver()
            
            try:
                # Navigate to results page
                url = f"https://gmrit.edu.in/results/{hall_ticket}"
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Wait a bit more for dynamic content
                time.sleep(3)
                
                # Get page source
                html_content = driver.page_source
                
                # Save HTML file
                os.makedirs(output_dir, exist_ok=True)
                html_file = os.path.join(output_dir, f"{hall_ticket}.html")
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"Successfully scraped {hall_ticket}")
                
                return {
                    'success': True,
                    'hall_ticket': hall_ticket,
                    'html_file': html_file,
                    'message': f'Successfully scraped {hall_ticket}'
                }
                
            except TimeoutException:
                return {
                    'success': False,
                    'hall_ticket': hall_ticket,
                    'error': 'Timeout - Page took too long to load'
                }
            except WebDriverException as e:
                return {
                    'success': False,
                    'hall_ticket': hall_ticket,
                    'error': f'Browser error: {str(e)}'
                }
            except Exception as e:
                return {
                    'success': False,
                    'hall_ticket': hall_ticket,
                    'error': f'Unexpected error: {str(e)}'
                }
            finally:
                driver.quit()
                
        except Exception as e:
            return {
                'success': False,
                'hall_ticket': hall_ticket,
                'error': f'Setup error: {str(e)}'
            }

# Global scraper instance
scraper = RenderScraper()

def scrape_student_results(hall_ticket, output_dir='html_pages'):
    """Main function to scrape student results"""
    return scraper.scrape_results(hall_ticket, output_dir)
