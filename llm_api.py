#!/usr/bin/env python3
"""
LLM-Enhanced Drug Search API
Combines vector search with LLM intelligence
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Try importing OpenAI
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logging.warning("OpenAI not available - will use basic search only")

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
chroma_client = None
collection = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    minimum_similarity: float = 0.0
    use_llm: bool = True

class SearchResult(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    text_chunk: str
    similarity_score: float
    metadata: dict

class LLMResponse(BaseModel):
    llm_answer: str
    confidence: str
    sources_used: int

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    llm_response: Optional[LLMResponse] = None
    search_time_ms: int
    total_results: int
    success: bool
    message: str

class HealthResponse(BaseModel):
    status: str
    database_status: str
    total_documents: int
    llm_status: str
    api_version: str
    timestamp: str

# FastAPI app initialization
app = FastAPI(
    title="🧠 AI-Powered İlaç Asistanı",
    description="LLM + Vector Search ile Akıllı İlaç Bilgi Sistemi",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def initialize_llm():
    """Initialize LLM (OpenAI GPT) if available"""
    global HAS_OPENAI
    
    if not HAS_OPENAI:
        return False
        
    # Try to get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("🤖 OpenAI API key not found - LLM disabled")
        HAS_OPENAI = False
        return False
    
    try:
        openai.api_key = api_key
        # Test API with a simple call
        logger.info("🤖 OpenAI LLM initialized successfully")
        return True
    except Exception as e:
        logger.error(f"🤖 LLM initialization failed: {e}")
        HAS_OPENAI = False
        return False

def generate_llm_response(query: str, search_results: List[dict]) -> Optional[LLMResponse]:
    """Generate intelligent response using LLM"""
    if not HAS_OPENAI or not search_results:
        return None
    
    try:
        # Prepare context from search results
        context = "İlaç bilgileri:\n"
        for i, result in enumerate(search_results[:3]):  # Use top 3 results
            drug_name = result.get('metadata', {}).get('drug_name', 'Bilinmeyen')
            text = result.get('text_chunk', '')[:200]  # Limit text length
            context += f"{i+1}. {drug_name}: {text}...\n"
        
        # Create prompt
        prompt = f"""Sen bir uzman eczacısın. Aşağıdaki soruya göre ilaç bilgilerini kullanarak yardımcı ol:

Soru: {query}

Mevcut İlaç Bilgileri:
{context}

Lütfen:
1. Soruya özel, faydalı bir cevap ver
2. Mevcut bilgilere dayanarak konuş
3. Kesin teşhis koymaktan kaçın
4. Doktora danışmasını öner
5. Türkçe ve anlaşılır bir dil kullan

Cevap:"""

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen uzman bir eczacısın ve ilaç konularında güvenilir bilgi veriyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        llm_answer = response.choices[0].message.content.strip()
        
        return LLMResponse(
            llm_answer=llm_answer,
            confidence="medium",
            sources_used=len(search_results[:3])
        )
        
    except Exception as e:
        logger.error(f"🤖 LLM response generation failed: {e}")
        return None

def initialize_database():
    """ChromaDB connection initialize et"""
    global chroma_client, collection
    
    try:
        logger.info("🔌 ChromaDB bağlantısı kuruluyor...")
        
        # ChromaDB client  
        chroma_client = chromadb.PersistentClient(
            path="./data/processed/vector_db_full",
            settings=Settings(allow_reset=True)
        )
        
        # Collection bağlantısı
        collection_name = "pupillica_full"
        try:
            collection = chroma_client.get_collection(collection_name)
            doc_count = collection.count()
            logger.info(f"✅ Collection bulundu: {doc_count:,} documents")
        except Exception as e:
            logger.error(f"❌ Collection bulunamadı: {e}")
            raise HTTPException(status_code=500, detail="Vector database bulunamadı")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization hatası: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """API başlangıç işlemleri"""
    logger.info("🚀 AI-Powered Pupillica API başlatılıyor...")
    
    # Initialize database
    db_success = initialize_database()
    if not db_success:
        logger.error("❌ Database initialization başarısız!")
        return
    
    # Initialize LLM
    llm_success = initialize_llm()
    if llm_success:
        logger.info("🤖 LLM entegrasyonu aktif")
    else:
        logger.info("🔍 Sadece vector search aktif")
    
    logger.info("✅ API başarıyla başlatıldı!")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """API ve database durumu"""
    try:
        doc_count = collection.count() if collection else 0
        
        return HealthResponse(
            status="healthy",
            database_status="connected" if collection else "disconnected",
            total_documents=doc_count,
            llm_status="available" if HAS_OPENAI else "unavailable",
            api_version="2.0.0",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return HealthResponse(
            status="unhealthy",
            database_status="error",
            total_documents=0,
            llm_status="error",
            api_version="2.0.0",
            timestamp=datetime.now().isoformat()
        )

@app.post("/search", response_model=SearchResponse)
async def enhanced_search(request: SearchRequest):
    """
    AI-Enhanced İlaç Arama
    - Vector search + LLM intelligence
    - Akıllı cevaplar ve öneriler
    """
    start_time = time.time()
    
    try:
        if collection is None:
            raise HTTPException(status_code=500, detail="Database bağlantısı yok")
        
        # Input validation
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query boş olamaz")
        
        logger.info(f"🔍 Enhanced search: '{request.query}' (LLM: {request.use_llm})")
        
        # Vector search
        results = collection.query(
            query_texts=[request.query],
            n_results=min(request.limit, 20),  # Limit for performance
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        if results['documents'][0]:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]
            
            for i, (doc, metadata, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
                # Better similarity calculation
                similarity = max(0, 1 - (distance / 2))  # Normalize distance better
                
                if similarity >= request.minimum_similarity:
                    result = SearchResult(
                        document_id=doc_id,
                        document_name=f"Document_{i+1}",
                        document_type=metadata.get('document_type', 'KUB'),
                        text_chunk=doc.strip()[:300] + "..." if len(doc) > 300 else doc.strip(),
                        similarity_score=round(similarity, 3),
                        metadata=metadata
                    )
                    formatted_results.append(result)
        
        # Generate LLM response if requested and available
        llm_response = None
        if request.use_llm and HAS_OPENAI and formatted_results:
            llm_response = generate_llm_response(request.query, [r.dict() for r in formatted_results])
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            results=formatted_results[:request.limit],
            llm_response=llm_response,
            search_time_ms=int(search_time * 1000),
            total_results=len(formatted_results),
            success=True,
            message=f"{len(formatted_results)} sonuç bulundu" + (" + AI analizi" if llm_response else "")
        )
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """API ana sayfa"""
    return {
        "message": "🧠 AI-Powered İlaç Asistanı API",
        "version": "2.0.0",
        "features": ["Vector Search", "LLM Intelligence", "Real-time Analysis"],
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "llm_api:app",
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflict
        reload=True
    )