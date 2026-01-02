"""
Pinterest Scraper cu Selenium - Versiunea Universală
"""

import os
import time
import random
import requests
from typing import List
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@dataclass
class PinImage:
    pin_id: str
    url: str
    local_path: str = None

class SeleniumPinterestScraper:
    """
    Scraper cu Selenium - simulează utilizator real.
    """
    
    def __init__(
        self,
        headless: bool = True,
        output_folder: str = "pinterest_images"
    ):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Setup Chrome options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        # Anti-detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Selenium driver inițializat")
    
    def _random_delay(self, min_s: float = 1.0, max_s: float = 3.0):
        delay = random.uniform(min_s, max_s)
        time.sleep(delay)
    
    def _human_scroll(self, scrolls: int = 5):
        for _ in range(scrolls):
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self._random_delay(0.5, 1.5)

    def _get_high_res_url(self, url: str) -> str:
        """Convertește URL la rezoluție maximă."""
        for size in ["236x", "474x", "736x"]:
            if size in url:
                return url.replace(size, "originals")
        return url

    # --- FUNCȚIA NOUĂ ȘI UNIVERSALĂ ---
    def scrape_by_url(self, url: str, count: int = 50) -> List[PinImage]:
        """
        Scrape generic de pe orice link Pinterest (Profil, Board, Search, etc).
        """
        print(f"\n🔗 Accesare URL: {url}")
        
        self.driver.get(url)
        self._random_delay(3, 5)
        
        pins = []
        last_height = 0
        no_new_content = 0
        
        while len(pins) < count:
            self._human_scroll(3)
            self._random_delay(2, 4)
            
            try:
                # Selector universal
                pin_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "div[data-test-id='pin'] img, div[data-grid-item] img"
                )
                
                for elem in pin_elements:
                    if len(pins) >= count:
                        break
                    
                    src = elem.get_attribute("src")
                    
                    if src and "pinimg.com" in src:
                        # ⚠️ FILTRU: Ignorăm avatarele mici de user (75x75)
                        if "75x75" in src:
                            continue
                            
                        high_res_url = self._get_high_res_url(src)
                        pin_id = src.split("/")[-1].split(".")[0]
                        
                        # Evitare duplicate
                        if not any(p.pin_id == pin_id for p in pins):
                            pins.append(PinImage(
                                pin_id=pin_id,
                                url=high_res_url
                            ))
            except Exception as e:
                print(f"   ⚠️ Eroare la extragere: {e}")
            
            # Verificare final de pagină
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_new_content += 1
                if no_new_content >= 3:
                    print("   ℹ️ Pagina s-a terminat.")
                    break
            else:
                no_new_content = 0
                
            last_height = new_height
            print(f"   📊 Găsite: {len(pins)}/{count}")
        
        return pins[:count]
    
    def download_images(self, pins: List[PinImage]):
        print(f"\n📥 Downloading {len(pins)} imagini...")
        
        for i, pin in enumerate(pins, 1):
            try:
                self._random_delay(1, 2)
                response = requests.get(pin.url, timeout=30)
                
                if response.status_code == 200:
                    ext = pin.url.split(".")[-1].split("?")[0]
                    if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                        ext = "jpg"
                    
                    filename = f"{pin.pin_id}.{ext}"
                    filepath = os.path.join(self.output_folder, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    pin.local_path = filepath
                    print(f"   [{i}/{len(pins)}] ✅ {filename}")
                else:
                    print(f"   [{i}/{len(pins)}] ❌ Status {response.status_code}")
            except Exception as e:
                print(f"   [{i}/{len(pins)}] ❌ {e}")
        
        downloaded = len([p for p in pins if p.local_path])
        print(f"\n✅ Downloaded: {downloaded}/{len(pins)}")
    
    def close(self):
        self.driver.quit()
        print("🔒 Browser închis")