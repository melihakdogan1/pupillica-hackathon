#!/usr/bin/env python3
"""
API Test Script - Basit ve Stabil
"""

import requests
import json
import time

def test_api():
    print("🧪 Pupillica API Test")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8001"
    
    # 1. Health Check
    print("1️⃣ Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Sağlık: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return
    
    # 2. Basit arama testleri
    test_queries = [
        "parasetamol",
        "ibuprofen", 
        "augmentin",
        "parol"
    ]
    
    print(f"\n2️⃣ {len(test_queries)} İlaç Arama Testi...")
    
    for drug in test_queries:
        print(f"\n🔍 '{drug}' araması...")
        
        search_data = {
            "query": drug,
            "limit": 3,
            "use_llm": False
        }
        
        try:
            response = requests.post(f"{base_url}/search", json=search_data, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                found_results = results.get('found_results', 0)
                
                if found_results > 0:
                    print(f"   ✅ {found_results} sonuç bulundu")
                    
                    # İlk sonucu göster
                    first_result = results['results'][0]
                    doc_name = first_result.get('document_name', 'Bilinmeyen')
                    score = first_result.get('similarity_score', 0)
                    print(f"   📄 En iyi: {doc_name}")
                    print(f"   📊 Skor: {score:.3f}")
                else:
                    print(f"   ⚠️ Sonuç bulunamadı")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    print(f"\n🎉 Test Tamamlandı!")

if __name__ == "__main__":
    test_api()