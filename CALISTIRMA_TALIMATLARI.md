# ProspektAsistan - Çalıştırma Talimatları

## Backend Çalıştırma

### 1. Gerekli Bağımlılıkları Yükle
```bash
cd c:\pupillicaHackathon
pip install -r requirements.txt
```

### 2. Backend'i Başlat
```bash
cd c:\pupillicaHackathon\backend
python main.py
```

**Alternatif olarak uvicorn ile:**
```bash
cd c:\pupillicaHackathon\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Backend Test Et
Tarayıcıda `http://127.0.0.1:8000` adresine gidip API'nin çalıştığını kontrol edin.
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Frontend Çalıştırma

### Seçenek 1: VS Code Live Server (Önerilen)
1. VS Code'da `frontend` klasörünü açın
2. `index.html` dosyasına sağ tıklayın
3. "Open with Live Server" seçin
4. Otomatik olarak `http://127.0.0.1:5500` adresinde açılır

### Seçenek 2: Python HTTP Server
```bash
cd c:\pupillicaHackathon\frontend
python -m http.server 8080
```
Sonra `http://127.0.0.1:8080` adresine gidin.

### Seçenek 3: Doğrudan Dosya Açma
`c:\pupillicaHackathon\frontend\index.html` dosyasını çift tıklayarak açın.

## Tam Test Süreci

1. **Backend'i başlatın** (port 8000)
2. **Frontend'i açın** (Live Server önerilen)
3. **Web sitesini test edin:**
   - Giriş ekranında "AI Asistan ile Sohbet Et" tıklayın
   - Chat ekranında bir ilaç adı yazın (örn: "aspirin")
   - AI'ın cevap verdiğini kontrol edin

## Sorun Giderme

### Backend Sorunları
- **Port 8000 kullanımda:** Başka bir port kullanın: `python main.py --port 8001`
- **ModuleNotFoundError:** `pip install -r requirements.txt` çalıştırın
- **Database bulunamadı:** Log'larda "demo mode" yazmalı, normal bir durum

### Frontend Sorunları
- **CORS hatası:** Backend'in çalıştığından emin olun
- **API bağlantısı yok:** Otomatik demo mode'a geçer, turuncu renk gösterir
- **JavaScript hatası:** Tarayıcı console'unu (F12) kontrol edin

## API Endpoint'leri

- `GET /` - API ana sayfa
- `GET /health` - Sistem durumu
- `POST /search` - İlaç arama (JSON body: `{"query": "aspirin"}`)
- `GET /docs` - Swagger API dokumentasyonu

## Demo Mode
Eğer backend bağlantısı kurulamazsa, frontend otomatik olarak demo mode'a geçer ve mock verilerle çalışır.

## Geliştirme Notları
- Backend değişiklik yapıldığında `--reload` ile otomatik yeniden başlar
- Frontend değişiklikleri Live Server ile otomatik yenilenir
- Production'da CORS ayarlarını güvenlik için kısıtlayın