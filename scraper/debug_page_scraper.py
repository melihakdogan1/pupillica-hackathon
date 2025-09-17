"""
TİTCK Debug Page Scraper - Sayfa içeriğini kontrol et
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def setup_driver():
    """Chrome driver'ı kur"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    chrome_options.add_argument("--ignore-ssl-errors-types")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    
    return driver

def debug_page(driver, wait, page_num):
    """Belirli bir sayfayı debug et"""
    print(f"\n🔍 Sayfa {page_num} Debug Başlıyor...")
    
    try:
        # Tabloyu bekle
        table_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dataTable")))
        print("✅ dataTable elementi bulundu")
        
        # Sayfa HTML'ini analiz et
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Tablo varlığını kontrol et
        table_soup = soup.find('table', class_='dataTable')
        if not table_soup:
            print("❌ Soup'ta dataTable bulunamadı")
            return False
        print("✅ Soup'ta dataTable bulundu")
        
        # Tbody kontrol et
        tbody = table_soup.find('tbody')
        if not tbody:
            print("❌ tbody bulunamadı")
            return False
        print("✅ tbody bulundu")
        
        # Satırları kontrol et
        rows = tbody.find_all('tr')
        print(f"📊 Bulunan satır sayısı: {len(rows)}")
        
        if len(rows) == 0:
            print("❌ Hiç satır bulunamadı!")
            return False
        
        # İlk 3 satırı analiz et
        for i, row in enumerate(rows[:3]):
            cells = row.find_all('td')
            print(f"\n📋 Satır {i+1}:")
            print(f"   Hücre sayısı: {len(cells)}")
            
            if len(cells) >= 7:
                ilac_adi = cells[1].get_text(strip=True)
                kub_link = cells[5].find('a')
                kt_link = cells[6].find('a')
                
                print(f"   İlaç adı: {ilac_adi[:50]}...")
                print(f"   KÜB linki: {'✅' if kub_link else '❌'}")
                print(f"   KT linki: {'✅' if kt_link else '❌'}")
            else:
                print(f"   ⚠️ Yetersiz hücre sayısı: {len(cells)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug hatası: {e}")
        return False

def navigate_to_page(driver, wait, target_page):
    """Belirli bir sayfaya git"""
    current_page = 1
    
    print(f"🎯 Sayfa {target_page}'a gidiliyor...")
    
    for i in range(target_page - 1):
        try:
            # Next butonunu bul
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".paginate_button.next")))
            
            # Sayfayı yukarı kaydır
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Tıkla
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            
            current_page += 1
            print(f"📄 Sayfa {current_page}'a geçildi")
            
        except Exception as e:
            print(f"❌ Sayfa geçiş hatası: {e}")
            return False
    
    return True

def main():
    """Main fonksiyon"""
    SEARCH_URL = "https://titck.gov.tr/kubkt"
    
    print("🚀 TİTCK Debug Scraper Başlıyor...")
    
    driver = None
    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)
        
        print(f"🌐 {SEARCH_URL} adresine gidiliyor...")
        driver.get(SEARCH_URL)
        time.sleep(5)
        
        # İlk sayfayı test et
        print("\n🔍 İlk sayfa testi:")
        debug_page(driver, wait, 1)
        
        # 284. sayfaya git
        if navigate_to_page(driver, wait, 284):
            print("\n🔍 284. sayfa testi:")
            debug_page(driver, wait, 284)
        
        # 300. sayfaya git
        if navigate_to_page(driver, wait, 300):
            print("\n🔍 300. sayfa testi:")
            debug_page(driver, wait, 300)
        
        # 400. sayfayı test et
        if navigate_to_page(driver, wait, 400):
            print("\n🔍 400. sayfa testi:")
            debug_page(driver, wait, 400)
        
        input("\n⏸️ Test tamamlandı. Enter'a basın...")
        
    except Exception as e:
        print(f"❌ Genel hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()