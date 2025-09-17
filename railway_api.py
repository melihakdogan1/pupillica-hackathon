from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import time
import os
from pathlib import Path

# FastAPI app
app = FastAPI(
    title="İlaç Asistanı API",
    description="TİTCK İlaç ve Tıbbi Ürün Bilgi Sistemi API - Demo Sürüm",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data - sample drug information
DEMO_DATA = [
    {
        "id": "demo_1",
        "text": "Paracetamol (Asetaminofen), ateş düşürücü ve ağrı kesici özellikler gösteren bir ilaçtır. Yetişkinlerde günlük maksimum doz 4000 mg'dır. Karaciğer hastalığı olan hastalarda dikkatli kullanılmalıdır. Yan etkileri arasında nadir olarak deri döküntüsü görülebilir.",
        "metadata": {"document_name": "Paracetamol Kullanım Kılavuzu", "document_type": "İlaç Prospektüsü"}
    },
    {
        "id": "demo_2", 
        "text": "Aspirin (Asetilsalisilik Asit), kan sulandırıcı etkisi olan bir ilaçtır. Kalp krizi riskini azaltmak için düşük dozlarda kullanılabilir. Mide rahatsızlığı, kanama riski yaratabilir. Çocuklarda Reye sendromu riski nedeniyle kullanılmamalıdır.",
        "metadata": {"document_name": "Aspirin Ürün Bilgileri", "document_type": "Reçeteli İlaç"}
    },
    {
        "id": "demo_3",
        "text": "Antibiyotikler bakteriyel enfeksiyonları tedavi eder. Viral enfeksiyonlarda (grip, soğuk algınlığı) etkisizdir. Doktor reçetesi ile kullanılmalıdır. Antibiyotik direnci gelişimini önlemek için tam kür kullanılmalıdır.",
        "metadata": {"document_name": "Antibiyotik Kullanım Rehberi", "document_type": "Tedavi Kılavuzu"}
    },
    {
        "id": "demo_4",
        "text": "Ağrı kesiciler (analjezikler) farklı mekanizmalarla çalışır. NSAİİ grubu ilaçlar inflamasyonu da azaltır. Uzun süreli kullanımda mide, böbrek ve kardiyovasküler yan etki riski vardır. Doktor kontrolünde kullanılmalıdır.",
        "metadata": {"document_name": "Ağrı Yönetimi Kılavuzu", "document_type": "Tedavi Rehberi"}
    },
    {
        "id": "demo_5",
        "text": "Hamilelik döneminde ilaç kullanımı çok dikkatli olmalıdır. FDA kategorilerine göre güvenlik değerlendirmesi yapılır (A, B, C, D, X). İlk trimesterde özellikle dikkatli olunmalı, doktor önerisi olmadan ilaç kullanılmamalıdır.",
        "metadata": {"document_name": "Hamilelik İlaç Güvenliği", "document_type": "Güvenlik Bilgisi"}
    },
    {
        "id": "demo_6",
        "text": "İbuprofen güçlü bir ağrı kesici ve ateş düşürücüdür. NSAİİ grubundan olup inflamasyonu da azaltır. Mide koruması için yemekle birlikte alınmalıdır. Astım hastalarında bronkospazm riski vardır.",
        "metadata": {"document_name": "İbuprofen Prospektüsü", "document_type": "İlaç Bilgisi"}
    },
    {
        "id": "demo_7",
        "text": "Antihipertansif ilaçlar yüksek tansiyonu kontrol eder. ACE inhibitörleri, beta blokerler, kalsiyum kanal blokerleri farklı mekanizmalarla çalışır. Düzenli kullanım şarttır, ani kesme tehlikelidir.",
        "metadata": {"document_name": "Hipertansiyon Tedavisi", "document_type": "Tedavi Protokolü"}
    },
    {
        "id": "demo_8",
        "text": "Proton pompa inhibitörleri (PPI) mide asidi salgısını azaltır. Peptik ülser, gastroözofageal reflü tedavisinde kullanılır. Uzun süreli kullanımda B12, magnezyum eksikliği riski vardır.",
        "metadata": {"document_name": "Mide Koruyucu İlaçlar", "document_type": "İlaç Grubu Bilgisi"}
    },
    {
        "id": "demo_9",
        "text": "Antikoagülan ilaçlar kan pıhtılaşmasını engelleyerek tromboz riskini azaltır. Warfarin, dabigatran, rivaroksaban farklı etki mekanizmalarına sahiptir. Kanama riski nedeniyle düzenli takip gerektirir.",
        "metadata": {"document_name": "Kan Sulandırıcı Tedavisi", "document_type": "Tedavi Kılavuzu"}
    },
    {
        "id": "demo_10",
        "text": "Insulin diyabet tedavisinde kullanılan hayati bir hormondur. Hızlı etkili, orta etkili ve uzun etkili formları vardır. Hipoglisemi en önemli yan etkisidir, kan şekeri takibi şarttır.",
        "metadata": {"document_name": "Diyabet İlaçları", "document_type": "Endokrin Tedavi"}
    }
]

total_documents = len(DEMO_DATA)

def search_in_demo_data(query: str, limit: int = 5):
    """Simple text search in demo data"""
    query_lower = query.lower()
    results = []
    
    for item in DEMO_DATA:
        text_lower = item["text"].lower()
        
        # Simple keyword matching
        score = 0
        query_words = query_lower.split()
        
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                count = text_lower.count(word)
                score += count * (len(word) / 10)  # Weight by word length
        
        if score > 0:
            results.append({
                "text_chunk": item["text"],
                "similarity_score": min(score / 10, 1.0),  # Normalize to 0-1
                "document_name": item["metadata"]["document_name"],
                "document_type": item["metadata"]["document_type"]
            })
    
    # Sort by similarity score
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:limit]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        # Try to read the HTML file
        html_path = Path(__file__).parent / "frontend" / "index.html"
        if html_path.exists():
            content = html_path.read_text(encoding='utf-8')
            # Update API base URL for production
            content = content.replace(
                "window.location.hostname === 'localhost' ? 'http://localhost:8000' : window.location.origin + '/api'",
                "window.location.origin"
            )
            return HTMLResponse(content=content)
        else:
            # Fallback HTML with embedded interface
            return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💊 İlaç Asistanı - TİTCK İlaç Bilgi Sistemi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 1000px; margin: 0 auto; background: white; 
            border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #4CAF50, #45a049); color: white; 
            padding: 40px; text-align: center;
        }
        .header h1 { font-size: 3em; margin-bottom: 15px; }
        .search-section { padding: 40px; }
        .disclaimer { 
            background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; 
            padding: 20px; margin-bottom: 30px; color: #856404; text-align: center;
        }
        .search-container { 
            display: flex; gap: 15px; margin-bottom: 30px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-radius: 30px; overflow: hidden;
        }
        .search-input { 
            flex: 1; padding: 20px 25px; font-size: 16px; border: none; outline: none;
        }
        .search-btn { 
            padding: 20px 35px; background: linear-gradient(135deg, #4CAF50, #45a049); 
            color: white; border: none; font-size: 16px; cursor: pointer;
        }
        .results { margin-top: 30px; }
        .result-card { 
            background: white; border: 1px solid #e9ecef; border-radius: 15px; 
            padding: 25px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        @media (max-width: 768px) {
            .container { margin: 10px; }
            .header { padding: 30px 20px; }
            .header h1 { font-size: 2.2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💊 İlaç Asistanı</h1>
            <p>TİTCK İlaç ve Tıbbi Ürün Bilgi Sistemi - Demo</p>
        </div>
        <div class="search-section">
            <div class="disclaimer">
                <strong>⚠️ Önemli Uyarı:</strong> Bu sistem yalnızca bilgi amaçlıdır. 
                İlaç kullanımı ile ilgili kararlarınızı almadan önce mutlaka doktorunuza danışın.
            </div>
            <div class="search-container">
                <input type="text" class="search-input" id="searchInput" 
                       placeholder="İlaç adı, yan etki, doz bilgisi yazın...">
                <button class="search-btn" onclick="performSearch()">🔍 Ara</button>
            </div>
            <div id="results" class="results"></div>
        </div>
    </div>
    <script>
        async function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            
            const results = document.getElementById('results');
            results.innerHTML = '<p>Aranıyor...</p>';
            
            try {
                const response = await fetch(`/search?q=${encodeURIComponent(query)}&limit=5`);
                const data = await response.json();
                
                if (data.success && data.results.length > 0) {
                    results.innerHTML = data.results.map(result => `
                        <div class="result-card">
                            <h3>${result.document_name}</h3>
                            <p>${result.text_chunk}</p>
                            <small>Tip: ${result.document_type} | Benzerlik: ${(result.similarity_score * 100).toFixed(1)}%</small>
                        </div>
                    `).join('');
                } else {
                    results.innerHTML = '<p>Sonuç bulunamadı. Farklı terimler deneyin.</p>';
                }
            } catch (error) {
                results.innerHTML = '<p>Hata oluştu: ' + error.message + '</p>';
            }
        }
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });
    </script>
</body>
</html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>İlaç Asistanı</h1><p>Demo sürüm. Error: {e}</p>")

@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "message": "İlaç Asistanı API çalışıyor - Demo Sürüm",
        "total_documents": total_documents,
        "timestamp": time.time(),
        "version": "demo"
    }

@app.get("/search")
async def search_documents(
    q: str = Query(..., description="Arama terimi"),
    limit: int = Query(default=5, le=20, description="Maksimum sonuç sayısı"),
    min_similarity: float = Query(default=0.1, ge=0.0, le=1.0, description="Minimum benzerlik skoru")
):
    """Search in demo drug documents"""
    start_time = time.time()
    
    try:
        # Perform search in demo data
        results = search_in_demo_data(q, limit)
        
        # Filter by minimum similarity
        filtered_results = [r for r in results if r["similarity_score"] >= min_similarity]
        
        search_time = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "query": q,
            "total_results": len(filtered_results),
            "results": filtered_results,
            "search_time_ms": search_time,
            "database_documents": total_documents,
            "note": "Demo sürüm - 10 örnek doküman"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    return {
        "total_documents": total_documents,
        "database_type": "Demo Data",
        "status": "demo"
    }

# For Railway
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)