#!/usr/bin/env python3
"""
Gerçek Sistem Durumu Analizi
"""
import chromadb
from chromadb.config import Settings
import os
from pathlib import Path

def analyze_real_system():
    """Mevcut sistemin gerçek durumunu analiz et"""
    print("🔍 Gerçek Sistem Durumu Analizi")
    print("=" * 50)
    
    # 1. Dosya sayıları
    kt_files = len(list(Path("data/kt").glob("*.pdf"))) if Path("data/kt").exists() else 0
    kub_files = len(list(Path("data/kub").glob("*.pdf"))) if Path("data/kub").exists() else 0
    extracted_files = len(list(Path("data/processed/extracted").glob("*.txt"))) if Path("data/processed/extracted").exists() else 0
    
    print(f"📁 PDF Dosyaları:")
    print(f"   KT klasörü: {kt_files:,} dosya")
    print(f"   KUB klasörü: {kub_files:,} dosya")
    print(f"   Toplam PDF: {kt_files + kub_files:,} dosya")
    print(f"   İşlenmiş: {extracted_files:,} dosya")
    
    # 2. Vector database analizi
    try:
        db_path = "data/processed/vector_db_full"
        if Path(db_path).exists():
            client = chromadb.PersistentClient(path=db_path)
            collections = client.list_collections()
            
            print(f"\n🗄️ Vector Database:")
            print(f"   Konum: {db_path}")
            print(f"   Collection sayısı: {len(collections)}")
            
            if collections:
                collection = collections[0]
                real_count = collection.count()
                print(f"   Gerçek doküman sayısı: {real_count:,}")
                
                # Sample query
                if real_count > 0:
                    results = collection.query(
                        query_texts=["paracetamol"],
                        n_results=min(3, real_count)
                    )
                    print(f"   Sample arama sonucu: {len(results['documents'][0]) if results['documents'] else 0} sonuç")
            else:
                print("   ❌ Collection bulunamadı")
        else:
            print(f"\n❌ Vector database bulunamadı: {db_path}")
            
    except Exception as e:
        print(f"\n❌ Database analiz hatası: {e}")
    
    # 3. API test
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🌐 API Durumu:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Rapor edilen doküman: {data.get('total_documents', 0):,}")
        else:
            print(f"\n❌ API yanıt vermiyor: {response.status_code}")
    except Exception as e:
        print(f"\n❌ API erişim hatası: {e}")
    
    # 4. Özet
    print(f"\n📊 ÖZET:")
    actual_processing_rate = (extracted_files / (kt_files + kub_files) * 100) if (kt_files + kub_files) > 0 else 0
    print(f"   PDF İndirme: %{((kt_files + kub_files) / 5000 * 100):.1f} tamamlandı")
    print(f"   Text Extraction: %{actual_processing_rate:.1f} tamamlandı")
    print(f"   Vector Database: {'Var' if Path('data/processed/vector_db_full').exists() else 'Yok'}")
    
    if actual_processing_rate < 10:
        print(f"\n⚠️  UYARI: Sistem çok az veri ile çalışıyor!")
        print(f"   Gerçek performans testine geçmeden önce veri artırılmalı.")

if __name__ == "__main__":
    analyze_real_system()