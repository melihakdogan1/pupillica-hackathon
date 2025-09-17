# 💊 İlaç Asistanı

**TİTCK İlaç ve Tıbbi Ürün Bilgi Sistemi**

## 🌟 Özellikler

- 📋 **468,406** TİTCK dokümanı içinde semantik arama
- 🔍 Gelişmiş doğal dil işleme
- ⚡ Hızlı arama sonuçları (250-700ms)
- 📱 Mobil uyumlu responsive tasarım
- 🔒 Rate limiting ile korunmuş API
- 🌐 Vercel'de deploy edilmiş

## 🚀 Canlı Demo

🌍 **[ilacasistan.vercel.app](https://ilacasistan.vercel.app)**

## 📁 Proje Yapısı

```
├── api/
│   └── search.py          # FastAPI backend
├── frontend/
│   └── index.html         # Web arayüzü
├── data/
│   └── processed/         # İşlenmiş veriler
├── vercel.json           # Vercel konfigürasyonu
├── requirements.txt      # Python bağımlılıkları
└── package.json         # Node.js metadata
```

## 🔧 Yerel Geliştirme

### Backend (FastAPI)
```bash
pip install -r requirements.txt
cd api
uvicorn search:app --reload --port 8000
```

### Frontend
```bash
# Statik dosya sunucusu
python -m http.server 3000 --directory frontend
```

## 📊 API Endpoints

### `GET /health`
Sistem durumu kontrolü
```json
{
  "status": "healthy",
  "total_documents": 468406,
  "timestamp": 1703123456
}
```

### `GET /search`
Semantik arama
```
/search?q=paracetamol&limit=5&min_similarity=0.2
```

**Response:**
```json
{
  "success": true,
  "query": "paracetamol",
  "total_results": 5,
  "results": [...],
  "search_time_ms": 250
}
```

## 🛡️ Güvenlik

- ⏱️ Rate limiting: 15 arama/dakika
- 🔒 CORS koruması
- 📝 Input sanitization
- ⚠️ Medikal disclaimer

## 📱 Kullanım

1. Ana sayfada arama kutusuna ilaç adı, yan etki veya doz bilgisi yazın
2. Enter'a basın veya "Ara" butonuna tıklayın
3. Sonuçları inceleyin - benzerlik skorları ile sıralanmış
4. Hızlı aramalar için örnek butonları kullanın

## ⚠️ Önemli Uyarı

Bu sistem yalnızca **bilgi amaçlıdır**. İlaç kullanımı ile ilgili kararlarınızı almadan önce **mutlaka doktorunuza danışın**.

## 🏗️ Teknolojiler

- **Backend:** FastAPI, ChromaDB, Sentence Transformers
- **Frontend:** Vanilla JavaScript, Modern CSS
- **Deploy:** Vercel, Serverless Functions
- **AI:** all-MiniLM-L6-v2 embedding model

## 📈 Performans

- **Doküman Sayısı:** 468,406
- **Arama Süresi:** 250-700ms
- **Benzerlik Modeli:** Semantic search
- **Rate Limit:** 15/dakika

## 🤝 Katkıda Bulunun

Bu proje TİTCK verilerini kullanarak geliştirilmiştir. Topluma faydalı olmak amacıyla açık kaynak olarak paylaşılmıştır.

---

💡 **İlaç Asistanı** - Güvenilir ilaç bilgisi için doğru adres