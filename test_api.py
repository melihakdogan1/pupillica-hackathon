#!/usr/bin/env python3
"""
API test scripti
"""

import requests
import json

def test_api():
    """API'yi test et"""
    
    # API'nin çalışıp çalışmadığını kontrol et
    try:
        print("🔍 API'yi test ediyorum...")
        
        # Health endpoint test
        health_response = requests.get("http://localhost:8001/health", timeout=10)
        print(f"Health Status Code: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API Çalışıyor!")
            print(f"📊 Veritabanı Durumu: {health_data['database_status']}")
            print(f"📁 Toplam Dokument: {health_data['total_documents']:,}")
            print(f"🤖 LLM Durumu: {health_data['llm_status']}")
            
            # Basit arama testi
            print("\n🔍 Arama testi yapılıyor...")
            search_data = {
                "query": "parol", 
                "limit": 2,
                "use_llm": False,
                "minimum_similarity": 0.3
            }
            
            search_response = requests.post(
                "http://localhost:8001/search",
                json=search_data,
                timeout=60
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Arama başarılı!")
                print(f"📊 Bulunan sonuç: {results['total_results']}")
                
                for i, result in enumerate(results['results'][:3]):
                    print(f"\n{i+1}. {result['document_name']}")
                    print(f"   Benzerlik: {result['similarity_score']:.3f}")
                    print(f"   Metin: {result['text_chunk'][:100]}...")
            else:
                print(f"❌ Arama hatası: {search_response.status_code}")
                print(f"Hata: {search_response.text}")
        else:
            print(f"❌ API erişilemiyor: {health_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API'ye bağlanılamıyor. API çalışıyor mu?")
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_api()