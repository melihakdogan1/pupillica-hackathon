from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import chromadb
from chromadb.config import Settings
import os
import time
from pathlib import Path
import json

# FastAPI app
app = FastAPI(
    title="İlaç Asistanı API",
    description="TİTCK İlaç ve Tıbbi Ürün Bilgi Sistemi API",
    version="1.0.0"
)

# CORS configuration for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vercel domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
chroma_client = None
collection = None
total_documents = 0

def initialize_database():
    """Initialize ChromaDB connection"""
    global chroma_client, collection, total_documents
    
    try:
        # For Vercel, data will be uploaded differently
        # For now, use in-memory for demo
        chroma_client = chromadb.Client(Settings(
            is_persistent=False,
            anonymized_telemetry=False
        ))
        
        # Create demo collection
        collection = chroma_client.create_collection(
            name="drug_documents",
            metadata={"description": "İlaç Asistanı Demo"}
        )
        
        # Add demo data
        demo_data = [
            {
                "id": "demo_1",
                "text": "Paracetamol, ateş düşürücü ve ağrı kesici özellikler gösteren bir ilaçtır. Günlük maksimum doz 4000 mg'dır. Karaciğer hastalığı olan hastalar dikkatli kullanmalıdır.",
                "metadata": {"document_name": "Paracetamol Kullanım Kılavuzu", "document_type": "Kullanım Kılavuzu"}
            },
            {
                "id": "demo_2", 
                "text": "Aspirin kan sulandırıcı etkisi olan bir ilaçtır. Kalp krizi riskini azaltmak için düşük dozlarda kullanılabilir. Mide rahatsızlığı yaratabilir.",
                "metadata": {"document_name": "Aspirin Ürün Bilgileri", "document_type": "Ürün Bilgisi"}
            },
            {
                "id": "demo_3",
                "text": "Antibiyotikler bakteriyel enfeksiyonları tedavi eder. Viral enfeksiyonlarda etkisizdir. Doktor reçetesi ile kullanılmalıdır.",
                "metadata": {"document_name": "Antibiyotik Kullanım Rehberi", "document_type": "Rehber"}
            },
            {
                "id": "demo_4",
                "text": "Ağrı kesiciler farklı mekanizmalarla çalışır. NSAİİ grubu ilaçlar inflamasyonu da azaltır. Uzun süreli kullanımda yan etki riski vardır.",
                "metadata": {"document_name": "Ağrı Yönetimi Kılavuzu", "document_type": "Kılavuz"}
            },
            {
                "id": "demo_5",
                "text": "Hamilelik döneminde ilaç kullanımı dikkatli olmalıdır. FDA kategorilerine göre güvenlik değerlendirmesi yapılır. Doktor önerisi zorunludur.",
                "metadata": {"document_name": "Hamilelik İlaç Güvenliği", "document_type": "Güvenlik Bilgisi"}
            }
        ]
        
        # Add to collection
        collection.add(
            ids=[doc["id"] for doc in demo_data],
            documents=[doc["text"] for doc in demo_data],
            metadatas=[doc["metadata"] for doc in demo_data]
        )
        
        total_documents = len(demo_data)
        print(f"✅ Demo database initialized with {total_documents} documents")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        # Create minimal fallback
        chroma_client = chromadb.Client(Settings(is_persistent=False))
        collection = chroma_client.create_collection(name="fallback")
        total_documents = 0

# Initialize on startup
initialize_database()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        # Try to read the HTML file
        html_path = Path(__file__).parent.parent / "frontend" / "index.html"
        if html_path.exists():
            return HTMLResponse(content=html_path.read_text(encoding='utf-8'))
        else:
            # Fallback HTML
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head><title>İlaç Asistanı</title></head>
            <body>
                <h1>💊 İlaç Asistanı</h1>
                <p>API çalışıyor! <a href="/docs">API Dokümantasyonu</a></p>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>İlaç Asistanı</h1><p>Demo sürüm aktif. Error: {e}</p>")

@app.get("/health")
async def health_check():
    """API health check"""
    global total_documents
    return {
        "status": "healthy",
        "message": "İlaç Asistanı API çalışıyor",
        "total_documents": total_documents,
        "timestamp": time.time()
    }

@app.get("/search")
async def search_documents(
    q: str = Query(..., description="Arama terimi"),
    limit: int = Query(default=5, le=20, description="Maksimum sonuç sayısı"),
    min_similarity: float = Query(default=0.1, ge=0.0, le=1.0, description="Minimum benzerlik skoru")
):
    """Semantic search in drug documents"""
    global collection, total_documents
    
    if not collection:
        raise HTTPException(status_code=503, detail="Database not available")
    
    start_time = time.time()
    
    try:
        # Perform semantic search
        results = collection.query(
            query_texts=[q],
            n_results=min(limit, 20),
            include=["documents", "metadatas", "distances"]
        )
        
        search_time = int((time.time() - start_time) * 1000)
        
        # Process results
        processed_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                similarity = 1 - results["distances"][0][i]  # Convert distance to similarity
                
                if similarity >= min_similarity:
                    metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}
                    
                    processed_results.append({
                        "text_chunk": doc,
                        "similarity_score": round(similarity, 4),
                        "document_name": metadata.get("document_name", "Bilinmeyen Doküman"),
                        "document_type": metadata.get("document_type", "Genel")
                    })
        
        return {
            "success": True,
            "query": q,
            "total_results": len(processed_results),
            "results": processed_results,
            "search_time_ms": search_time,
            "database_documents": total_documents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    global total_documents
    return {
        "total_documents": total_documents,
        "database_type": "ChromaDB",
        "status": "demo" if total_documents < 1000 else "production"
    }

# For Vercel
def handler(event, context):
    """Vercel handler function"""
    return app(event, context)