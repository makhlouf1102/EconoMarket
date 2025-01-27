from typing import Dict, List
from datetime import datetime
from .base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import PyPDF2
import os
import time
import requests
from bs4 import BeautifulSoup
from google.cloud import documentai
import io
from dotenv import load_dotenv
from pdf2image import convert_from_path
import tempfile
from PIL import Image
import concurrent.futures

# Load environment variables
load_dotenv()

# Configure paths from environment variables
DOWNLOADS_DIR = os.getenv('DOWNLOADS_DIR', './downloads')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us')  # Document AI location
PROCESSOR_ID = os.getenv('GOOGLE_CLOUD_PROCESSOR_ID')  # OCR Processor ID

Image.MAX_IMAGE_PIXELS = None  # Disable the decompression bomb check

class AdonisScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            store_name="Adonis",
            base_url="https://circulaire.groupeadonis.ca"
        )
        self.current_store_id = os.getenv('ADONIS_SAUVE_STORE_ID', "21937")  # Default store ID (Sauvé)
        self.flyer_id = "79768"  # Current flyer ID
        self.pdf_path = None
        
        # Create necessary directories
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        self.setup_selenium()
        # Initialize Document AI client
        self.docai_client = documentai.DocumentProcessorServiceClient()
        self.processor_name = self.docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)
        
    def setup_selenium(self):
        """Configure Selenium WebDriver"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # macOS specific options
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # Add PDF download preferences
        chrome_options.add_experimental_option(
            'prefs', {
                'download.default_directory': os.path.abspath(DOWNLOADS_DIR),
                'download.prompt_for_download': False,
                'plugins.always_open_pdf_externally': True,
                'download.open_pdf_in_system_reader': False,
                'profile.default_content_settings.popups': 0,
                'safebrowsing.enabled': True
            }
        )
        
        try:
            # Use manually installed ChromeDriver
            service = Service('/opt/homebrew/bin/chromedriver')
            
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            self.logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise
        
    def get_flyer_url(self) -> str:
        """Get the flyer URL"""
        return f"{self.base_url}/flyer/{self.flyer_id}?storeId={self.current_store_id}&language=en"
        
    def download_flyer_pdf(self) -> str:
        """Download the flyer PDF using Selenium"""
        try:
            # Clean up any existing PDF files
            for file in os.listdir(DOWNLOADS_DIR):
                if file.endswith('.pdf'):
                    os.remove(os.path.join(DOWNLOADS_DIR, file))
            
            # Navigate to the flyer URL using Selenium
            flyer_url = self.get_flyer_url()
            self.logger.info(f"Accessing flyer URL: {flyer_url}")
            self.driver.get(flyer_url)
            
            # Wait for the page to be fully loaded
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            # Wait for any loading overlays to disappear
            try:
                WebDriverWait(self.driver, 10).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#ais"))
                )
            except Exception as e:
                self.logger.warning(f"Loading overlay did not disappear: {str(e)}")
            
            # Wait for the More button to be present and visible
            more_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".hamburger-menu-button button"))
            )
            
            # Scroll the button into view and ensure it's clickable
            self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
            time.sleep(1)  # Small delay to let any animations complete
            
            # Try multiple click strategies
            click_methods = [
                lambda: more_button.click(),  # Normal click
                lambda: self.driver.execute_script("arguments[0].click();", more_button),  # JS click
                lambda: self.driver.execute_script("""
                    var evt = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    arguments[0].dispatchEvent(evt);
                """, more_button)  # Dispatch mouse event
            ]
            
            last_error = None
            for click_method in click_methods:
                try:
                    click_method()
                    self.logger.info("Successfully clicked More button")
                    break
                except Exception as e:
                    last_error = e
                    continue
            else:
                self.logger.error(f"All click methods failed. Last error: {str(last_error)}")
                raise last_error
            
            # Wait for the dropdown menu to appear and the PDF download link to be clickable
            pdf_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pdf-btn[href*='/pdfs/Adonis']"))
            )
            
            pdf_url = pdf_link.get_attribute('href')
            self.logger.info(f"Found PDF URL: {pdf_url}")
            
            if pdf_url:
                # Download the PDF using requests session with timeout
                self.logger.info(f"Downloading PDF from: {pdf_url}")
                pdf_response = self.session.get(pdf_url, timeout=30)
                
                content_type = pdf_response.headers.get('content-type', '').lower()
                if pdf_response.status_code == 200 and (content_type.startswith('application/pdf') or content_type == 'application/octet-stream'):
                    pdf_path = os.path.join(DOWNLOADS_DIR, f"flyer_{self.flyer_id}.pdf")
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_response.content)
                    
                    # Verify the file exists and has content
                    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                        self.pdf_path = pdf_path
                        self.logger.info(f"PDF downloaded successfully: {self.pdf_path} ({os.path.getsize(pdf_path)} bytes)")
                        return self.pdf_path
                    else:
                        self.logger.error(f"PDF file was not created or is empty: {pdf_path}")
                else:
                    self.logger.error(f"Failed to download PDF. Status: {pdf_response.status_code}, Content-Type: {content_type}")
                    # Try to get more information from the response
                    self.logger.debug(f"Response headers: {dict(pdf_response.headers)}")
                    self.logger.debug(f"Response content preview: {pdf_response.content[:200]}")
            else:
                self.logger.error("Could not find PDF link in the page")
            return None
            
        except requests.Timeout:
            self.logger.error("Timeout while downloading PDF")
            return None
        except Exception as e:
            self.logger.error(f"Error downloading PDF: {str(e)}")
            return None
            
    def process_image(self, image: Image.Image, page_num: int) -> str:
        """Process a single image with Vision API"""
        try:
            self.logger.info(f"Processing page {page_num} with Vision API...")
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG', optimize=True, quality=85)
            content = img_byte_arr.getvalue()
            
            # Create vision image object
            vision_image = vision.Image(content=content)
            
            # Detect text in the image
            response = self.vision_client.text_detection(
                image=vision_image,
                image_context={"language_hints": ["fr"]}
            )
            
            if response.error.message:
                self.logger.error(f"Error detecting text on page {page_num}: {response.error.message}")
                return ""
            
            # Get the text annotations
            page_text = response.text_annotations[0].description if response.text_annotations else ""
            
            # Clean up the text
            if page_text.strip():
                lines = [line.strip() for line in page_text.split('\n')]
                lines = [line for line in lines if line and len(line) > 1]
                return f"\n=== Page {page_num} ===\n" + '\n'.join(lines) + '\n'
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error processing page {page_num}: {str(e)}")
            return ""
            
    def extract_text_from_pdf(self) -> str:
        """Extract text content from the downloaded PDF using Google Document AI"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            self.logger.error("PDF file not found")
            return ""
            
        try:
            # Read the PDF file
            self.logger.info("Reading PDF file...")
            with open(self.pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
            
            # Configure the process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=documentai.RawDocument(
                    content=pdf_content,
                    mime_type="application/pdf"
                )
            )
            
            self.logger.info("Processing PDF with Document AI...")
            result = self.docai_client.process_document(request=request)
            document = result.document
            
            # Extract and clean the text
            text = document.text
            if text.strip():
                # Clean up the text (remove multiple spaces and empty lines)
                lines = [line.strip() for line in text.split('\n')]
                lines = [line for line in lines if line and len(line) > 1]  # Keep lines with at least 2 chars
                text = '\n'.join(lines)
                
                self.logger.info(f"Successfully extracted text from PDF ({len(text)} characters)")
            else:
                self.logger.error("No text was extracted from the PDF")
                
            return text
                
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
        
    def parse_products_from_text(self, text: str) -> List[Dict]:
        """Save raw text to file and return empty list for now"""
        # Save raw text to file
        output_file = os.path.join(OUTPUT_DIR, f"flyer_{self.flyer_id}_raw.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        self.logger.info(f"Raw text saved to: {output_file}")
        return []  # Return empty list for now, we'll parse it later
        
    def get_categories(self) -> List[Dict[str, str]]:
        """Get flyer categories by downloading and parsing the PDF"""
        pdf_path = self.download_flyer_pdf()
        if not pdf_path:
            return []
            
        text = self.extract_text_from_pdf()
        if not text:
            return []
            
        # Return a single category containing all products
        return [{
            'name': 'All Products (PDF)',
            'url': self.get_flyer_url(),
            'page_id': 'pdf-products'
        }]
        
    def scrape_category(self, category_url: str, category_name: str) -> List[Dict]:
        """Scrape products from the PDF"""
        if not self.pdf_path:
            self.download_flyer_pdf()
            
        text = self.extract_text_from_pdf()
        return self.parse_products_from_text(text)
        
    def scrape_product(self, product_url: str) -> Dict:
        """Not used for PDF scraping"""
        self.logger.warning("scrape_product is not used for PDF scraping")
        return {}
        
    def __del__(self):
        """Cleanup method to close the browser and remove downloaded files"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            if self.pdf_path and os.path.exists(self.pdf_path):
                os.remove(self.pdf_path)
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
        
    def get_available_stores(self) -> List[Dict[str, str]]:
        """Get available stores"""
        return [
            {
                'name': 'Sauvé',
                'id': 'Sauve',
                'store_id': '21937',
                'address': '2001 Rue Sauvé Ouest',
                'phone': '(514) 382-8606'
            },
            {
                'name': 'Anjou',
                'id': 'Anjou',
                'store_id': '21938',
                'address': '7250 Boulevard des Roseraies',
                'phone': '(514) 355-9595'
            },
            {
                'name': 'Brossard',
                'id': 'Brossard',
                'store_id': '21939',
                'address': '8405 Boulevard Taschereau',
                'phone': '(450) 462-0066'
            }
        ]
        
    def set_store(self, store_id: str):
        """Set the current store ID"""
        self.current_store_id = store_id 