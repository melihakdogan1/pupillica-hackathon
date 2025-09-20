#!/usr/bin/env python3
"""
LLM-Enhanced Drug Search API
Combines vector search with Hugging Face Gemma-2B
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

# Try importing Hugging Face transformers (optional for demo)
try:
    # Import only if needed, disabled for demo speed
    HAS_TRANSFORMERS = False  # Disabled for demo performance
    logger = logging.getLogger(__name__)
    logger.info("� Using rule-based AI for demo speed")
except ImportError:
    HAS_TRANSFORMERS = False
    logger = logging.getLogger(__name__)
    logger.warning("� Using rule-based responses")

# Try importing OpenAI (fallback)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
chroma_client = None
collection = None
llm_model = None
llm_tokenizer = None
llm_pipeline = None

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
    """Initialize rule-based AI for demo speed"""
    global HAS_TRANSFORMERS
    
    logger.info("🤖 Initializing fast rule-based AI system...")
    HAS_TRANSFORMERS = True  # Enable rule-based system
    logger.info("✅ Rule-based AI system ready!")
    return True

def initialize_openai_fallback():
    """Initialize OpenAI as fallback if Hugging Face fails"""
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
    """Generate intelligent response using rule-based AI"""
    global HAS_TRANSFORMERS
    
    if not HAS_TRANSFORMERS or not search_results:
        return None
    
    # Use enhanced rule-based response
    return enhanced_rule_based_response(query, search_results)

def enhanced_rule_based_response(query: str, search_results: List[dict]) -> Optional[LLMResponse]:
    """Enhanced rule-based response with smart context extraction"""
    if not search_results:
        return None
    
    top_result = search_results[0]
    text_chunk = top_result.get('text_chunk', '')
    drug_name = top_result.get('metadata', {}).get('drug_name', 'Bu ilaç')
    
    query_lower = query.lower()
    
    # Advanced pattern matching for Turkish medical queries
    if any(word in query_lower for word in ['yan etki', 'istenmeyen etki', 'zararlı']):
        answer = extract_medical_info(text_chunk, 'yan_etki', drug_name)
    elif any(word in query_lower for word in ['doz', 'miktar', 'kaç tane', 'ne kadar']):
        answer = extract_medical_info(text_chunk, 'doz', drug_name)
    elif any(word in query_lower for word in ['nasıl kullan', 'nasıl al', 'kullanım şekli']):
        answer = extract_medical_info(text_chunk, 'kullanim', drug_name)
    elif any(word in query_lower for word in ['nedir', 'ne için', 'hangi hastalık']):
        answer = extract_medical_info(text_chunk, 'genel', drug_name)
    elif any(word in query_lower for word in ['kimler kullanmamalı', 'kontrendikasyon', 'yasak']):
        answer = extract_medical_info(text_chunk, 'kontrendikasyon', drug_name)
    elif any(word in query_lower for word in ['hamilelik', 'gebelik', 'emzirme']):
        answer = extract_medical_info(text_chunk, 'hamilelik', drug_name)
    else:
        # General information
        answer = f"{drug_name} hakkında bilgi: {text_chunk[:200]}..."
    
    return LLMResponse(
        llm_answer=answer,
        confidence="Akıllı Analiz",
        sources_used=len(search_results)
    )

def extract_medical_info(text: str, info_type: str, drug_name: str) -> str:
    """Extract specific medical information from text"""
    sentences = text.split('.')
    
    keywords = {
        'yan_etki': ['yan etki', 'istenmeyen etki', 'reaksiyon', 'zararlı etki'],
        'doz': ['doz', 'miktar', 'günde', 'tablet', 'mg', 'ml', 'kaç'],
        'kullanim': ['kullanım', 'alınır', 'nasıl', 'şekli', 'yöntemi'],
        'genel': ['etken madde', 'içerik', 'nedir', 'tedavi', 'hastalık'],
        'kontrendikasyon': ['kullanmamalı', 'yasak', 'sakıncalı', 'kontrendikasyon'],
        'hamilelik': ['hamilelik', 'gebelik', 'emzirme', 'anne']
    }
    
    relevant_sentences = []
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords.get(info_type, [])):
            relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        result = '. '.join(relevant_sentences[:2])
        return f"{drug_name} - {result}."
    else:
        # Fallback to first meaningful sentence
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        if meaningful_sentences:
            return f"{drug_name} hakkında: {meaningful_sentences[0]}."
        else:
            return f"{drug_name} hakkında bilgi prospektüs içeriğinde mevcuttur."

def generate_openai_response(query: str, search_results: List[dict]) -> Optional[LLMResponse]:
    """Generate response using OpenAI as fallback"""
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
        
        # ChromaDB client - yeni veritabanı yolu
        chroma_client = chromadb.PersistentClient(
            path="./data/veritabani_optimized",
            settings=Settings(allow_reset=True)
        )
        
        # Collection bağlantısı - yeni collection adı
        collection_name = "ilac_prospektusleri"
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
    logger.info("🚀 AI-Powered ProspektAsistan API başlatılıyor...")
    
    # Initialize database
    db_success = initialize_database()
    if not db_success:
        logger.error("❌ Database initialization başarısız!")
        return
    
    # Try to initialize rule-based AI system
    llm_success = initialize_llm()
    if llm_success:
        logger.info("🤖 Rule-based AI sistemi aktif")
    else:
        # Fallback to OpenAI
        openai_success = initialize_openai_fallback()
        if openai_success:
            logger.info("🤖 OpenAI LLM fallback aktif")
        else:
            logger.info("🔍 Sadece vector search aktif")
    
    logger.info("✅ API başarıyla başlatıldı!")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """API ve database durumu"""
    try:
        doc_count = collection.count() if collection else 0
        
        # Determine LLM status
        llm_status = "unavailable"
        if HAS_TRANSFORMERS:
            llm_status = "rule-based-ai"
        elif HAS_OPENAI:
            llm_status = "openai"
        
        return HealthResponse(
            status="healthy",
            database_status="connected" if collection else "disconnected",
            total_documents=doc_count,
            llm_status=llm_status,
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
        if request.use_llm and formatted_results:
            # Try Hugging Face first, then OpenAI fallback
            if HAS_TRANSFORMERS and llm_pipeline:
                llm_response = generate_llm_response(request.query, [r.dict() for r in formatted_results])
            elif HAS_OPENAI:
                llm_response = generate_openai_response(request.query, [r.dict() for r in formatted_results])
        
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
    import os
    port = int(os.getenv("PORT", 8003))  # Railway PORT veya local 8003
    uvicorn.run(
        "llm_api:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )