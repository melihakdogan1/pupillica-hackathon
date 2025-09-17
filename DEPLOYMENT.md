# Vercel Deployment Kılavuzu

## 🚀 İlaç Asistanı - Vercel Deployment

### 1. Vercel CLI Kurulumu
```bash
npm i -g vercel
```

### 2. Proje Hazırlığı
```bash
cd C:\pupillicaHackathon
vercel login
```

### 3. İlk Deployment
```bash
vercel --prod
```

### 4. Konfigürasyon
- Domain: `ilacasistan.vercel.app`
- Framework: Other
- Build Command: `echo "Static site"`
- Output Directory: `frontend`
- Install Command: `pip install -r requirements.txt`

### 5. Environment Variables
Vercel dashboard'da:
- `PYTHONPATH`: `/var/task`

### 6. Test
```bash
curl https://ilacasistan.vercel.app/api/health
```

### 7. Domain Ayarları
Vercel dashboard'da custom domain ekle:
- `ilacasistan.com` (opsiyonel)

## 📝 Deployment Checklist

- [x] vercel.json konfigürasyonu
- [x] api/search.py serverless function
- [x] frontend/index.html static site
- [x] requirements.txt dependencies
- [x] package.json metadata
- [x] CORS ayarları
- [x] Rate limiting
- [x] Error handling
- [x] Mobile responsive
- [x] SEO optimization

## 🔧 Troubleshooting

### Build Error
```bash
vercel logs
```

### Function Timeout
vercel.json'da `maxDuration: 30` ayarlandı

### Large Dependencies
ChromaDB ve sentence-transformers optimize edildi

## 📊 Monitoring

Vercel dashboard'da:
- Function invocations
- Error rates
- Response times
- Bandwidth usage

## 🔄 Updates

Kod değişikliği sonrası:
```bash
git add .
git commit -m "Update"
git push
vercel --prod
```