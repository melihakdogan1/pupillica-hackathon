#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Test Script - Gerçek 152,776 chunks ile test
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🚀 API Test başlıyor...")
    
    # Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ API bağlantı hatası: {e}")
        print("⚠️  API başlatılmış mı? python search_api.py")
        return
    
    # Test aramaları
    test_queries = [
        {
            "query": "aspirin ağrı kesici",
            "description": "Aspirin arama testi"
        },
        {
            "query": "antibiyotik enfeksiyon",
            "description": "Antibiyotik arama testi"
        },
        {
            "query": "vitamin B1 B6 B12",
            "description": "Vitamin arama testi"
        },
        {
            "query": "hipertansiyon kan basıncı",
            "description": "Hipertansiyon arama testi"
        },
        {
            "query": "paracetamol ateş",
            "description": "Paracetamol arama testi"
        }
    ]
    
    print(f"\n🔍 {len(test_queries)} test araması yapılıyor...")
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"🔍 Query: '{test_case['query']}'")
        
        try:
            search_data = {
                "query": test_case["query"],
                "limit": 3
            }
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/search",
                json=search_data,
                headers={"Content-Type": "application/json"}
            )
            search_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Başarılı! {result['total_results']} sonuç bulundu")
                print(f"⏱️  Arama süresi: {search_time:.3f} saniye")
                print(f"📊 API response time: {result.get('search_time_ms', 'N/A')} ms")
                
                if result['results']:
                    first_result = result['results'][0]
                    print(f"📄 İlk sonuç:")
                    print(f"   📝 Doküman: {first_result['document_name']}")
                    print(f"   🏷️  Tür: {first_result['document_type']}")
                    print(f"   🎯 Similarity: {first_result['similarity_score']}")
                    print(f"   📖 Metin: {first_result['text_chunk'][:200]}...")
                else:
                    print("⚠️  Sonuç bulunamadı")
                    
            else:
                print(f"❌ Arama hatası: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Test hatası: {e}")
        
        time.sleep(1)  # Rate limiting
    
    print("\n🎯 Tüm testler tamamlandı!")

if __name__ == "__main__":
    test_api()