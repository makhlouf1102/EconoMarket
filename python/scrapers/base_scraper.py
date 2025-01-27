from abc import ABC, abstractmethod
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class BaseScraper(ABC):
    def __init__(self, store_name: str, base_url: str):
        self.store_name = store_name
        self.base_url = base_url
        self.session = requests.Session()
        self.setup_logging()
        
        # Headers par défaut
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.delay = 2  # Délai entre les requêtes
        
    def setup_logging(self):
        """Configure le logging pour le scraper"""
        self.logger = logging.getLogger(f"{self.store_name.lower()}_scraper")
        self.logger.setLevel(logging.INFO)
        
        # Crée le dossier logs s'il n'existe pas
        Path("logs").mkdir(exist_ok=True)
        
        # Handler pour le fichier
        file_handler = logging.FileHandler(f"logs/{self.store_name.lower()}_scraper.log")
        file_handler.setLevel(logging.INFO)
        
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Ajoute les handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[BeautifulSoup]:
        """
        Effectue une requête HTTP et retourne le contenu parsé avec BeautifulSoup.
        Permet d'utiliser des headers personnalisés qui seront fusionnés avec les headers par défaut.
        """
        try:
            # Fusionne les headers par défaut avec les headers personnalisés
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)
                
            time.sleep(self.delay)  # Respect du délai entre les requêtes
            
            response = self.session.get(url, headers=request_headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la requête vers {url}: {str(e)}")
            return None
    
    def save_data(self, data: List[Dict], category: str = ""):
        """Sauvegarde les données scrapées dans un fichier JSON"""
        try:
            # Crée le dossier data et le sous-dossier du magasin s'ils n'existent pas
            store_dir = Path("data") / self.store_name.lower()
            store_dir.mkdir(parents=True, exist_ok=True)
            
            # Génère le nom du fichier avec la date et l'heure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{category.lower().replace(' ', '_')}.json" if category else f"{timestamp}.json"
            
            # Sauvegarde les données
            with open(store_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Données sauvegardées dans {filename}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des données: {str(e)}")
    
    @abstractmethod
    def get_categories(self) -> List[Dict[str, str]]:
        """Récupère la liste des catégories disponibles"""
        pass
    
    @abstractmethod
    def scrape_category(self, category_url: str, category_name: str) -> List[Dict]:
        """Scrape les produits d'une catégorie"""
        pass
    
    @abstractmethod
    def scrape_product(self, product_url: str) -> Dict:
        """Scrape les détails d'un produit"""
        pass
    
    def run(self):
        """Exécute le scraping complet"""
        self.logger.info(f"Début du scraping pour {self.store_name}")
        
        try:
            categories = self.get_categories()
            for category in categories:
                self.logger.info(f"Scraping de la catégorie: {category['name']}")
                products = self.scrape_category(category['url'], category['name'])
                if products:
                    self.save_data(products, category['name'])
                    
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping: {str(e)}")
        
        self.logger.info("Scraping terminé") 