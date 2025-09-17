#!/usr/bin/env python3
"""
Simple Data-Focused TİTCK Scraper
Amaç: İlk sayfadan son sayfaya kadar SADECE VERİ İNDİRMEK
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException, NoAlertPresentException
from bs4 import BeautifulSoup
import time
import os
import requests
import re
from tqdm import tqdm
import random
import json
from datetime import datetime
from urllib.parse import urljoin

# Ayarlar
BASE_URL = "https://www.titck.gov.tr"
SEARCH_URL = f"{BASE_URL}/kubkt"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KUB_DIR = os.path.join(DATA_DIR, "kub")
KT_DIR = os.path.join(DATA_DIR, "kt")

def setup_driver():
    """Chrome driver'ı başlat"""
    print("🔧 Chrome WebDriver başlatılıyor...")
    
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    options.add_argument(f"--user-agent={user_agent}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    return driver

def download_pdf(url, file_path):
    """PDF dosyasını indir"""
    if os.path.exists(file_path):
        return "EXISTS"  # Dosya zaten mevcut
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200 and len(response.content) > 1000:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return "DOWNLOADED"
        else:
            return "ERROR"
    except Exception as e:
        print(f"  ❌ İndirme hatası: {str(e)[:50]}")
        return "ERROR"

def process_page(driver, page_num):
    """Sayfa verilerini işle ve dosyaları indir"""
    print(f"\n📄 Sayfa {page_num} işleniyor...")
    
    try:
        # Sayfanın yüklendiğinden emin ol
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataTable"))
        )
        
        # Alert varsa kapat
        try:
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(1)
        except NoAlertPresentException:
            pass
        
        # Sayfa kaynak kodunu al
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='dataTable')
        
        if not table:
            print("  ❌ Tablo bulunamadı")
            return 0, 0, 0
        
        tbody = table.find('tbody')
        if not tbody:
            print("  ❌ Tbody bulunamadı")
            return 0, 0, 0
        
        rows = tbody.find_all('tr')
        if not rows:
            print("  ❌ Satır bulunamadı")
            return 0, 0, 0
        
        print(f"  📊 {len(rows)} ilaç bulundu")
        
        downloaded_kub = 0
        downloaded_kt = 0
        total_processed = 0
        
        for i, row in enumerate(rows, 1):
            cells = row.find_all('td')
            if len(cells) < 7:
                continue
            
            # İlaç adını al
            drug_name = cells[1].get_text(strip=True)
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', drug_name)
            
            print(f"  🔄 {i:2d}/10: {drug_name[:40]}...")
            
            # KUB linki
            kub_link = cells[5].find('a')
            kub_status = "SKIP"
            if kub_link and kub_link.get('href'):
                kub_url = urljoin(BASE_URL, kub_link.get('href'))
                kub_path = os.path.join(KUB_DIR, f"{safe_name}_KUB.pdf")
                kub_status = download_pdf(kub_url, kub_path)
                if kub_status == "DOWNLOADED":
                    downloaded_kub += 1
            
            # KT linki
            kt_link = cells[6].find('a')
            kt_status = "SKIP"
            if kt_link and kt_link.get('href'):
                kt_url = urljoin(BASE_URL, kt_link.get('href'))
                kt_path = os.path.join(KT_DIR, f"{safe_name}_KT.pdf")
                kt_status = download_pdf(kt_url, kt_path)
                if kt_status == "DOWNLOADED":
                    downloaded_kt += 1
            
            print(f"    KUB: {kub_status}, KT: {kt_status}")
            total_processed += 1
            
            # Kısa bekleme
            time.sleep(random.uniform(0.5, 1.0))
        
        print(f"  ✅ Sayfa {page_num}: {total_processed} ilaç, {downloaded_kub} KUB, {downloaded_kt} KT indirildi")
        return total_processed, downloaded_kub, downloaded_kt
        
    except Exception as e:
        print(f"  ❌ Sayfa işleme hatası: {e}")
        return 0, 0, 0

def go_to_next_page(driver):
    """Sonraki sayfaya git"""
    try:
        # Next butonunu bul
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "posts_next"))
        )
        
        # Disabled kontrolü
        if "disabled" in next_button.get_attribute("class"):
            return False
        
        # Sayfayı yukarı kaydır
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Click yap
        next_button.click()
        time.sleep(3)
        
        # Yeni sayfanın yüklendiğini kontrol et
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataTable"))
        )
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Sayfa geçiş hatası: {e}")
        return False

def save_progress(page, total_drugs, total_kub, total_kt):
    """Progress'i kaydet"""
    progress = {
        'timestamp': datetime.now().isoformat(),
        'current_page': page,
        'total_drugs_processed': total_drugs,
        'total_kub_downloaded': total_kub,
        'total_kt_downloaded': total_kt,
        'total_files': total_kub + total_kt
    }
    
    progress_file = os.path.join(os.path.dirname(__file__), "..", "simple_progress.json")
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def main():
    """Ana scraping fonksiyonu"""
    print("🚀 Simple Data-Focused TİTCK Scraper Başlıyor...")
    print("🎯 Amaç: İlk sayfadan son sayfaya VERİ İNDİRMEK!")
    
    # Klasörleri oluştur
    os.makedirs(KUB_DIR, exist_ok=True)
    os.makedirs(KT_DIR, exist_ok=True)
    
    # Başlangıç durumu
    existing_kub = len([f for f in os.listdir(KUB_DIR) if f.endswith('.pdf')])
    existing_kt = len([f for f in os.listdir(KT_DIR) if f.endswith('.pdf')])
    
    print(f"📊 Başlangıç durumu:")
    print(f"   KUB: {existing_kub} dosya mevcut")
    print(f"   KT: {existing_kt} dosya mevcut")
    print(f"   Toplam: {existing_kub + existing_kt} dosya mevcut")
    
    driver = None
    try:
        driver = setup_driver()
        
        print(f"🌐 {SEARCH_URL} adresine gidiliyor...")
        driver.get(SEARCH_URL)
        time.sleep(5)
        
        # Sayaçlar
        current_page = 1
        total_drugs = 0
        total_kub_downloaded = 0
        total_kt_downloaded = 0
        
        while True:
            print(f"\n{'='*60}")
            print(f"📄 SAYFA {current_page}")
            print(f"{'='*60}")
            
            # Sayfayı işle
            page_drugs, page_kub, page_kt = process_page(driver, current_page)
            
            if page_drugs == 0:
                print(f"❌ Sayfa {current_page}'de veri bulunamadı - işlem durduruluyor")
                break
            
            # Sayaçları güncelle
            total_drugs += page_drugs
            total_kub_downloaded += page_kub
            total_kt_downloaded += page_kt
            
            # Progress kaydet
            save_progress(current_page, total_drugs, total_kub_downloaded, total_kt_downloaded)
            
            print(f"📈 Toplam durum:")
            print(f"   İşlenen ilaç: {total_drugs}")
            print(f"   İndirilen KUB: {total_kub_downloaded}")
            print(f"   İndirilen KT: {total_kt_downloaded}")
            print(f"   Toplam indirilen: {total_kub_downloaded + total_kt_downloaded}")
            
            # Sonraki sayfaya git
            print(f"🔄 Sayfa {current_page + 1}'e geçiliyor...")
            if not go_to_next_page(driver):
                print("❌ Son sayfaya ulaşıldı veya sayfa geçiş hatası")
                break
            
            current_page += 1
            
            # Her 10 sayfada bir uzun bekleme
            if current_page % 10 == 0:
                print(f"⏸️ 10 sayfa tamamlandı - 5 saniye bekleme...")
                time.sleep(5)
        
        print(f"\n🎉 SCRAPING TAMAMLANDI!")
        print(f"📊 Final sonuçlar:")
        print(f"   Toplam sayfa: {current_page}")
        print(f"   İşlenen ilaç: {total_drugs}")
        print(f"   İndirilen KUB: {total_kub_downloaded}")
        print(f"   İndirilen KT: {total_kt_downloaded}")
        print(f"   Toplam dosya: {total_kub_downloaded + total_kt_downloaded}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Kullanıcı tarafından durduruldu")
        save_progress(current_page, total_drugs, total_kub_downloaded, total_kt_downloaded)
    except Exception as e:
        print(f"\n❌ Genel hata: {e}")
    finally:
        if driver:
            driver.quit()
            print("🔄 Tarayıcı kapatıldı")

if __name__ == "__main__":
    main()