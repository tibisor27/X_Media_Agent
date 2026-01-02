# Asigură-te că fișierul cu clasa se numește 'selenium_scraper.py'
# Dacă se numește 'pinterest_scraper.py', schimbă linia de mai jos
from selenium_scraper import SeleniumPinterestScraper

if __name__ == "__main__":
    # Inițializare
    # AICI era probabil eroarea ta. Argumentele trebuie să fie în ordine.
    scraper = SeleniumPinterestScraper(headless=False) 
    
    try:
        # Link-ul pe care vrei să îl scanezi
        link = "https://ro.pinterest.com/pin/2040762326397158/"
        
        print(f"--- Începem extragerea de la: {link} ---")
        
        # Apelarea corectă: primul argument e link-ul (pozițional), al doilea e numit (keyword)
        imagini = scraper.scrape_by_url(link, count=20)
        
        # Descărcare
        scraper.download_images(imagini)

    except Exception as e:
        print(f"Eroare generală: {e}")
        
    finally:
        # Închidem browserul la final
        if 'scraper' in locals():
            scraper.close()