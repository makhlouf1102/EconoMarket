import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.adonis_scraper import AdonisScraper
from typing import List, Dict

def test_stores():
    """Test la récupération des magasins disponibles"""
    scraper = AdonisScraper()
    stores = scraper.get_available_stores()
    
    print("\nMagasins disponibles:")
    if stores:
        print(f"✅ {len(stores)} magasins trouvés")
        for store in stores[:3]:  # Affiche les 3 premiers magasins
            print(f"- {store['name']} (ID: {store['id']})")
            if store['address']:
                print(f"  Adresse: {store['address']}")
            if store['phone']:
                print(f"  Téléphone: {store['phone']}")
    else:
        print("❌ Aucun magasin trouvé")
    return stores

def test_flyer_categories(scraper: AdonisScraper):
    """Test la récupération des catégories du flyer"""
    categories = scraper.get_categories()
    
    print("\nPages du flyer:")
    if categories:
        print(f"✅ {len(categories)} pages trouvées")
        for cat in categories[:3]:  
            print(f"- {cat['name']}")
            print(f"  URL: {cat['url']}")
    else:
        print("❌ Aucune page trouvée dans le flyer")
    return categories

def test_products_from_page(scraper: AdonisScraper, categories: List[Dict]):
    """Test l'extraction des produits d'une page"""
    if not categories:
        print("\n❌ Aucune page disponible pour tester l'extraction des produits")
        return
        
    # Test avec la première page
    test_page = categories[0]
    products = scraper.scrape_category(test_page['url'], test_page['name'])
    
    print(f"\nProduits de la {test_page['name']}:")
    if products:
        print(f"✅ {len(products)} produits trouvés")
        if products:
            print("\nExemple de produit:")
            product = products[0]
            for key, value in product.items():
                if key not in ['scraped_at', 'source']:  # Skip technical fields
                    print(f"- {key}: {value}")
    else:
        print("❌ Aucun produit trouvé")
    return products

def main():
    """Fonction principale de test"""
    print("=== Test du scraper Adonis ===")
    
    try:
        scraper = AdonisScraper()
        
        # Test des magasins disponibles
        print("\n1. Test des magasins disponibles...")
        stores = test_stores()
        
        if stores:
            # Utilise le magasin Sauvé pour les tests
            sauve_store = next((store for store in stores if store['id'] == 'Sauve'), None)
            if sauve_store and sauve_store['store_id']:
                print(f"\nUtilisation du magasin: {sauve_store['name']}")
                scraper.set_store(sauve_store['store_id'])
                
                # Test des pages du flyer
                print("\n2. Test des pages du flyer...")
                categories = test_flyer_categories(scraper)
                
                # Test des produits d'une page
                print("\n3. Test des produits d'une page...")
                test_products_from_page(scraper, categories)
            else:
                print("\n❌ Impossible de trouver l'ID du magasin Sauvé")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
    
    print("\n✨ Tests terminés")

if __name__ == "__main__":
    main() 