from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Pupillica Medical AI API",
    description="İlaç prospektüs bilgileri için AI chatbot API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    confidence: float = 0.0

class DrugInfo(BaseModel):
    name: str
    active_ingredient: str
    indication: str
    dosage: str
    side_effects: str
    source_type: str  # KUB or KT

# Global variables for ML models (will be loaded on startup)
vector_store = None
embeddings_model = None
llm_model = None

@app.on_event("startup")
async def startup_event():
    """Uygulama başlarken ML modellerini yükle"""
    print("🚀 Pupillica Medical AI API başlatılıyor...")
    print("📊 Vector database yükleniyor...")
    # TODO: Vector store'u yükle
    print("🤖 AI modelleri hazırlanıyor...")
    # TODO: Embeddings ve LLM modellerini yükle
    print("✅ API hazır!")

@app.get("/")
async def root():
    return {
        "message": "Pupillica Medical AI API",
        "status": "running",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Sistem sağlık kontrolü"""
    return {
        "status": "healthy",
        "database": "connected" if vector_store else "not loaded",
        "ai_models": "loaded" if llm_model else "not loaded"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(message: ChatMessage):
    """Ana chatbot endpoint"""
    try:
        # TODO: RAG pipeline implementation
        # 1. Kullanıcı mesajını vektorize et
        # 2. Relevant PDF'leri bul
        # 3. Context'i hazırla
        # 4. LLM'den yanıt al
        
        # Geçici yanıt (development için)
        response = f"Merhaba! '{message.message}' sorunuzu aldım. Bu özellik henüz geliştiriliyor."
        
        return ChatResponse(
            response=response,
            sources=["Geliştirme aşamasında"],
            confidence=0.5
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat hatası: {str(e)}")

@app.get("/search/{drug_name}")
async def search_drug(drug_name: str):
    """İlaç adına göre arama"""
    try:
        # TODO: Vector search implementation
        return {
            "query": drug_name,
            "results": [],
            "message": "Arama özelliği geliştiriliyor"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arama hatası: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Sistem istatistikleri"""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    kub_dir = os.path.join(data_dir, "kub")
    kt_dir = os.path.join(data_dir, "kt")
    
    kub_count = len([f for f in os.listdir(kub_dir) if f.endswith('.pdf')]) if os.path.exists(kub_dir) else 0
    kt_count = len([f for f in os.listdir(kt_dir) if f.endswith('.pdf')]) if os.path.exists(kt_dir) else 0
    
    return {
        "total_kub_pdfs": kub_count,
        "total_kt_pdfs": kt_count,
        "total_drugs": max(kub_count, kt_count),
        "data_coverage": f"{((kub_count + kt_count) / 30378 * 100):.1f}%" if (kub_count + kt_count) > 0 else "0%"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )