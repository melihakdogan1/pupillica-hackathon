"""
ProspektAsistan - AI-Powered Drug Information Assistant Backend

Bu backend, ilaç prospektüsleri veritabanını kullanarak kullanıcı sorularına
akıllı cevaplar veren bir RAG (Retrieval-Augmented Generation) sistemi sağlar.

Özellikler:
- ChromaDB ile vektör arama
- FastAPI ile REST API
- CORS desteği ile frontend entegrasyonu
- 6,425+ ilaç prospektüsü verisi
"""
import os
import logging
from pathlib import Path
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
collection = None

# --- API Modelleri ---
class SearchRequest(BaseModel):
    """Arama isteği modeli"""
    query: str

class SearchResponse(BaseModel):
    """Arama yanıtı modeli"""
    llm_answer: str

# --- FastAPI Uygulaması ---
app = FastAPI(
    title="🧠 ProspektAsistan API", 
    version="1.0.0",
    description="AI-powered drug information assistant API"
)

# CORS ayarları - Frontend domainleri için
origins = [
    "https://charming-creponne-1a466d.netlify.app",  # Netlify production
    "http://localhost:3000",  # Development frontend
    "http://127.0.0.1:3000",  # Local development
    "*"  # Demo için tüm domainlere izin
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo için tüm domainlere izin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Uygulama başlangıcında veritabanı bağlantısını kurar"""
    global collection
    try:
        logger.info("🔌 ChromaDB veritabanına bağlanılıyor...")
        backend_dir = Path(__file__).resolve().parent
        db_path = str(backend_dir.parent / "data" / "veritabani_optimized")
        
        if not os.path.exists(db_path):
            logger.critical(f"❌ KRİTİK HATA: Veritabanı '{db_path}' yolunda bulunamadı!")
            return
            
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection("ilac_prospektusleri")
        logger.info(f"✅ Veritabanı başarıyla yüklendi: {collection.count():,} döküman")
        
    except Exception as e:
        logger.error(f"❌ Veritabanı başlatma hatası: {e}")

@app.get("/health")
async def health_check():
    """API sağlık durumunu kontrol eder"""
    return {
        "status": "healthy",
        "database_status": "connected" if collection else "disconnected",
        "total_documents": collection.count() if collection else 0
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Kullanıcı sorgusuna göre ilaç bilgisi arar ve akıllı cevap üretir"""
    if not collection:
        raise HTTPException(status_code=503, detail="Veritabanı hazır değil.")
    
    logger.info(f"Hızlı arama yapılıyor: '{request.query}'")
    try:
        results = collection.query(query_texts=[request.query], n_results=1)
        if not results['documents'][0]:
            raise HTTPException(status_code=404, detail="Sonuç bulunamadı.")
            
        top_result = results['documents'][0][0]
        drug_name = results['metadatas'][0][0].get('drug_name', 'Bilinmeyen İlaç')
        
        answer = f"🔍 **{drug_name}** hakkında bulunan en alakalı bilgi şudur:\n\n*\"{top_result.strip()}\"*\n\n**ÖNEMLİ NOT:** Bu, prospektüsten alınan doğrudan bir alıntıdır ve tıbbi tavsiye yerine geçmez. Lütfen doktorunuza danışın."
        return SearchResponse(llm_answer=answer)
    except Exception as e:
        logger.error(f"Arama sırasında hata: {e}")
        raise HTTPException(status_code=500, detail="Arama sırasında bir hata oluştu.")

if __name__ == "__main__":
    uvicorn.run("main.app", host="0.0.0.0", port=8000, reload=True)