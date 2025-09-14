from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import requests

def setup_driver():
    """Selenium WebDriver'ı kurar"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # WebDriver'ın bot olduğunu gizle
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def debug_site_with_selenium():
    """Selenium ile sitenin yapısını incele"""
    print("Selenium ile TİTCK sitesi inceleniyor...")
    
    driver = setup_driver()
    
    try:
        # Siteye git
        driver.get("https://www.titck.gov.tr/kubkt")
        print("Siteye erişildi.")
        
        # Sayfanın yüklenmesini bekle
        time.sleep(3)
        
        # Sayfa başlığını kontrol et
        print(f"Sayfa başlığı: {driver.title}")
        
        # HTML kaynağını al
        page_source = driver.page_source
        
        # HTML'i kaydet
        with open('selenium_debug_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Sayfa içeriği 'selenium_debug_page.html' dosyasına kaydedildi.")
        
        # BeautifulSoup ile analiz et
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Tüm tabloları bul
        tables = soup.find_all('table')
        print(f"Sayfada {len(tables)} tablo bulundu.")
        
        for i, table in enumerate(tables):
            class_attr = table.get('class', [])
            print(f"Tablo {i+1}: class={class_attr}")
            
            # İlk birkaç satırı göster
            rows = table.find_all('tr')[:5]
            for j, row in enumerate(rows):
                cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                if cols:  # Boş olmayan satırları göster
                    print(f"  Satır {j+1}: {cols}")
        
        # Pagination linklerini kontrol et
        pagination = soup.find_all('a', href=True)
        page_links = [a for a in pagination if 'page=' in a.get('href', '')]
        print(f"\n{len(page_links)} sayfa linki bulundu.")
        
        if page_links:
            print("İlk birkaç sayfa linki:")
            for i, link in enumerate(page_links[:5]):
                print(f"  {i+1}: {link.get('href')}")
        
    except Exception as e:
        print(f"Hata: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_site_with_selenium()