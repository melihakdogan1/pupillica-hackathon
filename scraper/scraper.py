import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import re

# --- Ayarlar ---
BASE_URL = "https://www.titck.gov.tr"
SEARCH_URL = f"{BASE_URL}/kubkt"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
    'Referer': 'https://www.google.com/'
}
# Proje kök dizinine göre data klasörlerinin yolları
KUB_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "kub")
KT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "kt")
MAX_PAGES = 1520 
DOWNLOAD_DELAY = 1 # İstekler arası bekleme süresini 1 saniyeye çıkaralım.
RETRY_COUNT = 5 # Hata durumunda 5 kere tekrar denesin.
RETRY_BACKOFF_FACTOR = 0.5 # Denemeler arası bekleme süresi çarpanı.

# --- Klasörleri Oluştur ---
os.makedirs(KUB_DIR, exist_ok=True)
os.makedirs(KT_DIR, exist_ok=True)

def create_session_with_retries():
    """Hata durumunda tekrar deneme mekanizmasına sahip bir Session nesnesi oluşturur."""
    session = requests.Session()
    retry_strategy = Retry(
        total=RETRY_COUNT,
        status_forcelist=[429, 500, 502, 503, 504], # Bu HTTP kodlarında tekrar dene
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=RETRY_BACKOFF_FACTOR
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session

def sanitize_filename(filename):
    """Dosya adlarındaki geçersiz karakterleri temizler."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_pdf(session, url, folder, file_name):
    """Belirtilen URL'den PDF indirir ve belirtilen klasöre kaydeder."""
    if not url.startswith('http'):
        url = BASE_URL + url
        
    safe_file_name = sanitize_filename(file_name)
    pdf_path = os.path.join(folder, f"{safe_file_name}.pdf")

    if os.path.exists(pdf_path):
        return f"Mevcut: {safe_file_name}.pdf"

    try:
        response = session.get(url, stream=True, timeout=60)
        response.raise_for_status() 

        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        time.sleep(DOWNLOAD_DELAY)
        return f"İndirildi: {safe_file_name}.pdf"
    except requests.exceptions.RequestException as e:
        return f"HATA: {safe_file_name} indirilemedi - {e}"

def scrape_titck():
    """TİTCK web sitesinden KÜB ve KT verilerini kazır."""
    print("TİTCK İlaç Prospektüs Veri Kazıma İşlemi Başlatılıyor...")
    print(f"KÜB dosyaları şu klasöre kaydedilecek: {KUB_DIR}")
    print(f"KT dosyaları şu klasöre kaydedilecek: {KT_DIR}")
    
    session = create_session_with_retries()
    total_ilac_count = 0
    
    for page_num in range(300, MAX_PAGES + 1):
        print(f"\n--- Sayfa {page_num}/{MAX_PAGES} Taranıyor ---")
        params = {'page': page_num}
        try:
            response = session.get(SEARCH_URL, params=params, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Sayfa {page_num} alınamadı: {e}. Bu sayfa atlanıyor.")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table', class_='table-striped')
        if not table:
            print(f"Sayfa {page_num}'de ilaç tablosu bulunamadı. Muhtemelen son sayfa veya bir sorun var. İşlem tamamlanıyor.")
            break
            
        rows = table.find('tbody').find_all('tr')
        if not rows:
            print(f"Sayfa {page_num} boş. Sonraki sayfaya geçiliyor.")
            continue

        for row in tqdm(rows, desc=f"Sayfa {page_num} İlaçları", unit=" ilaç"):
            cols = row.find_all('td')
            if len(cols) < 4:
                continue

            ilac_adi = cols[1].text.strip()
            
            kub_link_tag = cols[2].find('a')
            kt_link_tag = cols[3].find('a')

            if kub_link_tag and kub_link_tag.has_attr('href'):
                kub_link = kub_link_tag['href']
                status = download_pdf(session, kub_link, KUB_DIR, ilac_adi + "_KUB")
                # print(f"  {ilac_adi} (KÜB): {status}")

            if kt_link_tag and kt_link_tag.has_attr('href'):
                kt_link = kt_link_tag['href']
                status = download_pdf(session, kt_link, KT_DIR, ilac_adi + "_KT")
                # print(f"  {ilac_adi} (KT): {status}")
            
            total_ilac_count += 1

    print(f"\nKazıma işlemi tamamlandı. Toplam {total_ilac_count} ilaç bilgisi işlendi.")
    session.close()

if __name__ == "__main__":
    scrape_titck()