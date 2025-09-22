# 🚀 ProspektAsistan - Setup Instructions

## Quick Start Guide

### Prerequisites
- Python 3.9+
- pip package manager
- Modern web browser

### 1. Install Dependencies
```bash
cd c:\pupillicaHackathon
pip install -r requirements.txt
```

### 2. Start Backend
```bash
cd c:\pupillicaHackathon\backend
python main.py
```
✅ Backend will start at: `http://localhost:8000`

### 3. Start Frontend
```bash
cd c:\pupillicaHackathon\frontend
python -m http.server 3000
```
✅ Frontend will be available at: `http://localhost:3000`

### 4. Test the System
1. Open `http://localhost:3000` in your browser
2. Click "Sohbeti Başlat" (Start Chat)
3. Ask questions about medications in Turkish:
   - "aspirin yan etkileri nelerdir?"
   - "parol dozu nasıl hesaplanır?"
   - "nurofen ne için kullanılır?"

## API Documentation

### Health Check
```bash
GET http://localhost:8000/health
```

### Search Drug Information
```bash
POST http://localhost:8000/search
Content-Type: application/json

{
  "query": "aspirin yan etkileri"
}
```

### Example Response
```json
{
  "llm_answer": "🔍 **Aspirin** hakkında bulunan en alakalı bilgi şudur:\n\n*\"Aspirin'in bilinen yan etkileri arasında mide bulantısı, karın ağrısı ve baş dönmesi yer alır...\"*\n\n**ÖNEMLİ NOT:** Bu bilgiler sadece prospektüsten alınmıştır ve tıbbi tavsiye yerine geçmez."
}
```

## Project Structure
```
c:\pupillicaHackathon\
├── backend/
│   ├── main.py              # FastAPI backend server
├── frontend/
│   ├── index.html          # Main web interface
│   ├── style.css           # Styling
│   └── script.js           # JavaScript logic
├── data/
│   └── veritabani_optimized/   # ChromaDB database
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Production Deployment

### Frontend (Netlify/Vercel)
1. Update `API_BASE` in `frontend/script.js` with production backend URL
2. Deploy the `frontend/` folder to your hosting service

### Backend
1. Use services like Railway, Heroku, or DigitalOcean
2. Ensure ChromaDB data is included in deployment
3. Update CORS settings for production domain

## Features
- ✅ 6,425+ Turkish drug prospectus documents
- ✅ Vector search with ChromaDB
- ✅ Fast similarity search (~2-3 seconds)
- ✅ RESTful API with FastAPI
- ✅ Responsive web interface
- ✅ CORS enabled for cross-origin requests

## Troubleshooting

### Backend Issues
- Ensure Python 3.9+ is installed
- Check if ChromaDB data exists in `data/veritabani_optimized/`
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend Issues
- Check browser console for JavaScript errors
- Verify backend is running on correct port (8000)
- Ensure CORS is enabled in backend

### Performance Tips
- ChromaDB performs better with SSD storage
- Increase system RAM for better vector search performance
- Use production ASGI server (uvicorn) for better concurrent handling