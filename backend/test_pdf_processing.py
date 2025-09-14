#!/usr/bin/env python3
"""
PDF Processing Test Script
Scraper çalışırken PDF processing'i test eder
"""

import os
import sys
from pathlib import Path

# Backend modüllerini import et
sys.path.append(str(Path(__file__).parent))

from pdf_processor import extract_text_from_pdf, parse_drug_info
from vector_db import VectorDB

def test_pdf_processing():
    """PDF processing'i test et"""
    print("🧪 PDF Processing Test Başlatılıyor...")
    
    # Test için PDF dosyalarını bul
    kt_dir = Path("../data/kt")
    kub_dir = Path("../data/kub")
    
    if not kt_dir.exists():
        print("❌ KT klasörü bulunamadı!")
        return
    
    if not kub_dir.exists():
        print("❌ KÜB klasörü bulunamadı!")
        return
    
    # İlk 3 PDF'i test et
    kt_files = list(kt_dir.glob("*.pdf"))[:3]
    kub_files = list(kub_dir.glob("*.pdf"))[:3]
    
    print(f"📄 Test edilecek KT dosyaları: {len(kt_files)}")
    print(f"📄 Test edilecek KÜB dosyaları: {len(kub_files)}")
    
    # Vector DB'yi başlat
    try:
        vector_db = VectorDB()
        print("✅ Vector DB başlatıldı")
    except Exception as e:
        print(f"❌ Vector DB hatası: {e}")
        return
    
    # PDF processing testi
    test_count = 0
    success_count = 0
    
    for pdf_file in kt_files + kub_files:
        test_count += 1
        try:
            print(f"\n🔍 Test {test_count}: {pdf_file.name[:50]}...")
            
            # Text extraction
            text = extract_text_from_pdf(str(pdf_file))
            if not text:
                print(f"⚠️ Text çıkarılamadı: {pdf_file.name}")
                continue
            
            print(f"📝 Text uzunluğu: {len(text)} karakter")
            print(f"📝 İlk 200 karakter: {text[:200].replace('\n', ' ')}...")
            
            # Drug info parsing
            drug_info = parse_drug_info(text)
            print(f"💊 İlaç bilgisi: {drug_info}")
            
            # Vector DB'ye ekleme testi
            doc_type = "KT" if "kt" in pdf_file.parent.name.lower() else "KUB"
            vector_db.add_documents([{
                "content": text[:1000],  # İlk 1000 karakter
                "filename": pdf_file.name,
                "drug_name": drug_info.get("drug_name", "Bilinmiyor"),
                "type": doc_type
            }])
            
            print(f"✅ Vector DB'ye eklendi")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    # Similarity search testi
    try:
        print(f"\n🔎 Similarity Search Testi...")
        results = vector_db.search_similar("paracetamol ağrı kesici", n_results=3)
        print(f"📊 Bulunan sonuç sayısı: {len(results)}")
        for i, result in enumerate(results[:2]):
            print(f"🎯 Sonuç {i+1}: {result.get('filename', 'N/A')} (Skor: {result.get('distance', 'N/A')})")
    except Exception as e:
        print(f"❌ Search hatası: {e}")
    
    print(f"\n📊 Test Özeti:")
    print(f"📋 Toplam test: {test_count}")
    print(f"✅ Başarılı: {success_count}")
    print(f"📈 Başarı oranı: {success_count/test_count*100:.1f}%")

if __name__ == "__main__":
    test_pdf_processing()