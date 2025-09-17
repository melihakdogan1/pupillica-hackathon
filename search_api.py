"""
🏥 PUPILLICA SEARCH API
FastAPI tabanlı ilaç bilgi arama sistemi
- Semantic search with ChromaDB
- RAG pipeline integration  
- RESTful API endpoints
- Medical domain optimization
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
import uvicorn
import logging
import time
from datetime import datetime
import os
import json

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="🏥 Pupillica Drug Information API",
    description="Türkiye İlaç Bilgi Arama Sistemi - TİTCK verileri ile semantic search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da specific domains olmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    minimum_similarity: float = 0.3
    include_metadata: bool = True

class SearchResult(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    text_chunk: str
    similarity_score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    search_time_ms: int
    total_results: int
    success: bool
    message: str

class HealthResponse(BaseModel):
    status: str
    database_status: str
    total_documents: int
    api_version: str
    timestamp: str

# Global variables
chroma_client = None
collection = None

def initialize_database():
    """ChromaDB connection initialize et"""
    global chroma_client, collection
    
    try:
        logger.info("🔌 ChromaDB bağlantısı kuruluyor...")
        
        # ChromaDB client  
        chroma_client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(allow_reset=True)
        )
        
        # Collection bağlantısı
        collection_name = "drug_info"
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

def format_search_results(results, query: str, search_time: float) -> SearchResponse:
    """Search sonuçlarını format et"""
    
    if not results or not results['documents'][0]:
        return SearchResponse(
            query=query,
            results=[],
            search_time_ms=int(search_time * 1000),
            total_results=0,
            success=True,
            message="Hiç sonuç bulunamadı"
        )
    
    formatted_results = []
    documents = results['documents'][0]
    metadatas = results['metadatas'][0] if results.get('metadatas') else [{}] * len(documents)
    distances = results['distances'][0] if results.get('distances') else [0] * len(documents)
    ids = results['ids'][0] if results.get('ids') else list(range(len(documents)))
    
    for i, (doc, metadata, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
        # Similarity score hesapla (distance'i similarity'ye çevir)
        similarity = max(0, 1 - distance)
        
        # Metadata'dan bilgileri extract et
        doc_name = metadata.get('document_name', f'Document_{i+1}')
        doc_type = metadata.get('document_type', 'Unknown')
        
        # Text chunk'ı temizle ve kısalt
        text_chunk = doc.strip()
        if len(text_chunk) > 300:
            text_chunk = text_chunk[:297] + "..."
        
        result = SearchResult(
            document_id=str(doc_id),
            document_name=doc_name,
            document_type=doc_type,
            text_chunk=text_chunk,
            similarity_score=round(similarity, 3),
            metadata=metadata
        )
        formatted_results.append(result)
    
    return SearchResponse(
        query=query,
        results=formatted_results,
        search_time_ms=int(search_time * 1000),
        total_results=len(formatted_results),
        success=True,
        message=f"{len(formatted_results)} sonuç bulundu"
    )

@app.on_event("startup")
async def startup_event():
    """API başlatma olayı"""
    logger.info("🚀 Pupillica Search API başlatılıyor...")
    if not initialize_database():
        logger.error("❌ Database initialization başarısız!")
    else:
        logger.info("✅ API başarıyla başlatıldı!")

@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "message": "🏥 Pupillica Drug Information API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if collection is None:
            return HealthResponse(
                status="unhealthy",
                database_status="disconnected",
                total_documents=0,
                api_version="1.0.0",
                timestamp=datetime.now().isoformat()
            )
        
        doc_count = collection.count()
        
        return HealthResponse(
            status="healthy",
            database_status="connected",
            total_documents=doc_count,
            api_version="1.0.0",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return HealthResponse(
            status="unhealthy",
            database_status="error",
            total_documents=0,
            api_version="1.0.0",
            timestamp=datetime.now().isoformat()
        )

@app.post("/search", response_model=SearchResponse)
async def search_drugs(request: SearchRequest):
    """
    İlaç bilgileri arama endpoint'i
    - Semantic search yaplar
    - Similarity scoring ile sonuç döner
    - Metadata ile zenginleştirilmiş sonuçlar
    """
    start_time = time.time()
    
    try:
        if collection is None:
            raise HTTPException(status_code=500, detail="Database bağlantısı yok")
        
        # Input validation
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query boş olamaz")
        
        if request.limit < 1 or request.limit > 50:
            raise HTTPException(status_code=400, detail="Limit 1-50 arasında olmalı")
        
        logger.info(f"🔍 Search query: '{request.query}' (limit: {request.limit})")
        
        # ChromaDB search
        results = collection.query(
            query_texts=[request.query],
            n_results=request.limit,
            include=['documents', 'metadatas', 'distances']
        )
        
        search_time = time.time() - start_time
        
        # Sonuçları format et
        response = format_search_results(results, request.query, search_time)
        
        # Minimum similarity filter
        if request.minimum_similarity > 0:
            response.results = [
                r for r in response.results 
                if r.similarity_score >= request.minimum_similarity
            ]
            response.total_results = len(response.results)
            if response.total_results == 0:
                response.message = f"Minimum similarity ({request.minimum_similarity}) kriterini karşılayan sonuç bulunamadı"
        
        logger.info(f"✅ Search completed: {response.total_results} results in {response.search_time_ms}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        search_time = time.time() - start_time
        return SearchResponse(
            query=request.query,
            results=[],
            search_time_ms=int(search_time * 1000),
            total_results=0,
            success=False,
            message=f"Arama hatası: {str(e)}"
        )

@app.get("/search", response_model=SearchResponse)
async def search_drugs_get(
    q: str = Query(..., description="Arama sorgusu"),
    limit: int = Query(5, ge=1, le=50, description="Sonuç sayısı"),
    min_similarity: float = Query(0.3, ge=0, le=1, description="Minimum benzerlik skoru")
):
    """
    GET ile search (basit kullanım için)
    """
    request = SearchRequest(
        query=q,
        limit=limit,
        minimum_similarity=min_similarity
    )
    return await search_drugs(request)

@app.get("/stats", response_model=Dict[str, Any])
async def database_stats():
    """Database istatistikleri"""
    try:
        if collection is None:
            raise HTTPException(status_code=500, detail="Database bağlantısı yok")
        
        doc_count = collection.count()
        
        # Sample search to test performance
        start_time = time.time()
        sample_results = collection.query(
            query_texts=["test"],
            n_results=1,
            include=['documents']
        )
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "total_documents": doc_count,
            "collection_name": collection.name,
            "sample_search_time_ms": search_time_ms,
            "api_status": "active",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats alınamadı: {str(e)}")

if __name__ == "__main__":
    # Production için gunicorn kullanılmalı
    uvicorn.run(
        "search_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development için
        log_level="info"
    )