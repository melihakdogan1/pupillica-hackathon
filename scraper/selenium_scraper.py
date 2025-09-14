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
import re
from tqdm import tqdm

# --- Ayarlar ---
BASE_URL = "https://www.titck.gov.tr"
SEARCH_URL = f"{BASE_URL}/kubkt"
# Proje kök dizinine göre data klasörlerinin yolları
KUB_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "kub")
KT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "kt")
DOWNLOAD_DELAY = 1
PAGE_LOAD_DELAY = 3

# --- Klasörleri Oluştur ---
os.makedirs(KUB_DIR, exist_ok=True)
os.makedirs(KT_DIR, exist_ok=True)

def setup_driver():
    """Selenium WebDriver'ı kurar"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Headless mode (opsiyonel - tarayıcı görünmez)
    # chrome_options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # WebDriver'ın bot olduğunu gizle
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def sanitize_filename(filename):
    """Dosya adlarındaki geçersiz karakterleri temizler."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_pdf_from_link(driver, link_element, folder, file_name):
    """PDF linkinden dosyayı indir"""
    safe_file_name = sanitize_filename(file_name)
    pdf_path = os.path.join(folder, f"{safe_file_name}.pdf")

    if os.path.exists(pdf_path):
        return f"Mevcut: {safe_file_name}.pdf"

    try:
        # Linki tıkla ve URL'yi al
        href = link_element.get_attribute('href')
        if not href:
            return f"HATA: {safe_file_name} - Link bulunamadı"
        
        # Tam URL'yi oluştur
        if not href.startswith('http'):
            href = BASE_URL + href
        
        # PDF olup olmadığını kontrol et
        if not any(ext in href.lower() for ext in ['.pdf', 'pdf']):
            return f"HATA: {safe_file_name} - PDF değil"
        
        # requests ile PDF'i indir
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(href, stream=True, timeout=60, headers=headers)
        response.raise_for_status()
        
        # Content-Type kontrolü
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
            return f"HATA: {safe_file_name} - İçerik PDF değil ({content_type})"
        
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Dosya boyutunu kontrol et
        file_size = os.path.getsize(pdf_path)
        if file_size < 1024:  # 1KB'den küçükse
            os.remove(pdf_path)
            return f"HATA: {safe_file_name} - Dosya çok küçük ({file_size} byte)"
        
        time.sleep(DOWNLOAD_DELAY)
        return f"İndirildi: {safe_file_name}.pdf ({file_size} byte)"
        
    except Exception as e:
        # Hatalı dosyayı temizle
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass
        return f"HATA: {safe_file_name} indirilemedi - {e}"

def scrape_current_page(driver):
    """Mevcut sayfadaki ilaçları kazır"""
    time.sleep(3)  # Sayfanın tamamen yüklenmesini bekle
    
    try:
        # Selenium ile tüm satırları bul
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table.dataTable tbody tr")
        
        if not table_rows:
            return 0, False
        
        processed_count = 0
        successful_downloads = 0
        
        print(f"Sayfada {len(table_rows)} satır bulundu.")
        
        for i, row in enumerate(tqdm(table_rows, desc="İlaçlar İşleniyor", unit=" ilaç")):
            try:
                # Her satırdaki kolonları bul
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 7:
                    print(f"  Satır {i+1}: Yetersiz kolon ({len(cols)})")
                    continue
                
                # İlaç adını al
                ilac_adi = cols[0].text.strip()
                if not ilac_adi:
                    print(f"  Satır {i+1}: İlaç adı boş")
                    continue
                
                print(f"  İşleniyor: {ilac_adi[:50]}...")
                
                # KÜB linki (6. kolon - index 5)
                kub_downloaded = False
                try:
                    kub_links = cols[5].find_elements(By.TAG_NAME, "a")
                    if kub_links:
                        kub_link = kub_links[0]  # İlk linki al
                        href = kub_link.get_attribute('href')
                        if href and 'pdf' in href.lower():
                            status = download_pdf_from_link(driver, kub_link, KUB_DIR, ilac_adi + "_KUB")
                            if "İndirildi" in status or "Mevcut" in status:
                                kub_downloaded = True
                                print(f"    KÜB: ✓")
                            else:
                                print(f"    KÜB: ✗ ({status})")
                        else:
                            print(f"    KÜB: Link geçersiz")
                    else:
                        print(f"    KÜB: Link yok")
                except Exception as e:
                    print(f"    KÜB: Hata - {e}")
                
                # KT linki (7. kolon - index 6)
                kt_downloaded = False
                try:
                    kt_links = cols[6].find_elements(By.TAG_NAME, "a")
                    if kt_links:
                        kt_link = kt_links[0]  # İlk linki al
                        href = kt_link.get_attribute('href')
                        if href and 'pdf' in href.lower():
                            status = download_pdf_from_link(driver, kt_link, KT_DIR, ilac_adi + "_KT")
                            if "İndirildi" in status or "Mevcut" in status:
                                kt_downloaded = True
                                print(f"    KT: ✓")
                            else:
                                print(f"    KT: ✗ ({status})")
                        else:
                            print(f"    KT: Link geçersiz")
                    else:
                        print(f"    KT: Link yok")
                except Exception as e:
                    print(f"    KT: Hata - {e}")
                
                if kub_downloaded or kt_downloaded:
                    successful_downloads += 1
                
                processed_count += 1
                
            except Exception as e:
                print(f"  Satır {i+1} GENEL HATA: {e}")
                continue
        
        print(f"Sayfa özeti: {processed_count} ilaç işlendi, {successful_downloads} başarılı indirme")
        return processed_count, True
        
    except Exception as e:
        print(f"Sayfa kazıma hatası: {e}")
        return 0, False

def go_to_next_page(driver):
    """Sonraki sayfaya git"""
    try:
        # "Next" butonunu bul
        next_button = driver.find_element(By.CSS_SELECTOR, "a.paginate_button.next:not(.disabled)")
        if next_button:
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(PAGE_LOAD_DELAY)
            return True
        return False
    except:
        return False

def scrape_titck_with_selenium():
    """Selenium ile TİTCK web sitesinden veri kazı"""
    print("Selenium ile TİTCK İlaç Prospektüs Veri Kazıma İşlemi Başlatılıyor...")
    print(f"KÜB dosyaları şu klasöre kaydedilecek: {KUB_DIR}")
    print(f"KT dosyaları şu klasöre kaydedilecek: {KT_DIR}")
    
    driver = setup_driver()
    total_ilac_count = 0
    total_downloads = 0
    page_num = 1
    
    try:
        # İlk sayfaya git
        print("Siteye bağlanılıyor...")
        driver.get(SEARCH_URL)
        time.sleep(PAGE_LOAD_DELAY)
        print("Site yüklendi.")
        
        while True:
            print(f"\n{'='*60}")
            print(f"--- Sayfa {page_num} Taranıyor ---")
            print(f"{'='*60}")
            
            # Mevcut sayfayı kazı
            processed, success = scrape_current_page(driver)
            
            if not success:
                print(f"Sayfa {page_num}'de veri bulunamadı. İşlem tamamlanıyor.")
                break
            
            total_ilac_count += processed
            print(f"✓ Sayfa {page_num} tamamlandı: {processed} ilaç işlendi")
            print(f"📊 Toplam işlenen ilaç: {total_ilac_count}")
            
            # İndirilen dosya sayılarını kontrol et
            kub_files = len([f for f in os.listdir(KUB_DIR) if f.endswith('.pdf')])
            kt_files = len([f for f in os.listdir(KT_DIR) if f.endswith('.pdf')])
            print(f"📁 İndirilen dosyalar - KÜB: {kub_files}, KT: {kt_files}")
            
            # Sonraki sayfaya git
            print("Sonraki sayfaya geçiliyor...")
            if not go_to_next_page(driver):
                print("Son sayfa. İşlem tamamlanıyor.")
                break
            
            page_num += 1
            
            # Güvenlik için maksimum sayfa limiti
            if page_num > 2000:
                print("Maksimum sayfa limitine ulaşıldı.")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"🚨 Genel hata: {e}")
    
    finally:
        print("\n🔄 Tarayıcı kapatılıyor...")
        driver.quit()
    
    # Final istatistikleri
    kub_files = len([f for f in os.listdir(KUB_DIR) if f.endswith('.pdf')])
    kt_files = len([f for f in os.listdir(KT_DIR) if f.endswith('.pdf')])
    
    print(f"\n{'='*60}")
    print("🎉 VERİ ÇEKME İŞLEMİ TAMAMLANDI")
    print(f"{'='*60}")
    print(f"📋 Toplam İşlenen İlaç: {total_ilac_count}")
    print(f"📁 İndirilen KÜB Dosyası: {kub_files}")
    print(f"📁 İndirilen KT Dosyası: {kt_files}")
    print(f"📁 Toplam İndirilen: {kub_files + kt_files}")
    print(f"📊 Başarı Oranı: {((kub_files + kt_files) / (total_ilac_count * 2) * 100):.1f}%" if total_ilac_count > 0 else "N/A")
    print(f"{'='*60}")

if __name__ == "__main__":
    scrape_titck_with_selenium()