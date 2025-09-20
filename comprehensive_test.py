#!/usr/bin/env python3
"""
Kapsamlı sistem test scripti - İlaç Asistanı
"""

import requests
import json
import time

def comprehensive_search_test():
    """Kapsamlı arama testleri yap"""
    
    # Test terimleri ve beklenen minimum benzerlik skorları
    test_queries = [
        {"query": "aspirin", "min_score": 0.5, "description": "Aspirin ilaç araması"},
        {"query": "parol", "min_score": 0.6, "description": "Parol (Parasetamol) araması"},
        {"query": "ağrı kesici", "min_score": 0.4, "description": "Ağrı kesici genel araması"},
        {"query": "antibiyotik", "min_score": 0.4, "description": "Antibiyotik genel araması"},
        {"query": "yan etki", "min_score": 0.3, "description": "Yan etki bilgisi araması"},
        {"query": "doz", "min_score": 0.3, "description": "Dozaj bilgisi araması"},
        {"query": "hamilelik", "min_score": 0.3, "description": "Hamilelik kategorisi araması"},
        {"query": "çocuk", "min_score": 0.3, "description": "Çocuklarda kullanım araması"}
    ]
    
    print("🔍 İlaç Asistanı Kapsamlı Test Başlıyor...")
    print("=" * 60)
    
    api_base = "http://localhost:8001"
    total_tests = len(test_queries)
    passed_tests = 0
    
    # API sağlık kontrolü
    try:
        health_response = requests.get(f"{api_base}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API Durumu: {health_data['database_status']}")
            print(f"📊 Toplam Dokument: {health_data['total_documents']:,}")
            print(f"🤖 LLM Durumu: {health_data['llm_status']}")
            print()
        else:
            print("❌ API sağlık kontrolü başarısız!")
            return
    except Exception as e:
        print(f"❌ API'ye bağlanılamıyor: {e}")
        return
    
    # Her test terimini dene
    for i, test in enumerate(test_queries, 1):
        print(f"Test {i}/{total_tests}: {test['description']}")
        print(f"Aranan terim: '{test['query']}'")
        
        try:
            start_time = time.time()
            
            # POST isteği gönder
            search_data = {
                "query": test["query"],
                "limit": 5,
                "minimum_similarity": 0.2,
                "use_llm": False
            }
            
            response = requests.post(
                f"{api_base}/search",
                json=search_data,
                timeout=30
            )
            
            search_time = time.time() - start_time
            
            if response.status_code == 200:
                results = response.json()
                total_results = results.get('total_results', 0)
                
                if total_results > 0:
                    # En yüksek benzerlik skorunu bul
                    max_score = max([result['similarity_score'] for result in results['results']])
                    
                    print(f"   ✅ {total_results} sonuç bulundu")
                    print(f"   🎯 En yüksek benzerlik: {max_score:.3f}")
                    print(f"   ⏱️  Arama süresi: {search_time:.2f}s")
                    
                    # İlk 2 sonucu göster
                    for j, result in enumerate(results['results'][:2], 1):
                        doc_name = result.get('document_name', 'Bilinmeyen')
                        similarity = result['similarity_score']
                        text_preview = result['text_chunk'][:80] + "..." if len(result['text_chunk']) > 80 else result['text_chunk']
                        
                        print(f"   {j}. {doc_name}")
                        print(f"      Benzerlik: {similarity:.3f}")
                        print(f"      Metin: {text_preview}")
                    
                    # Test başarı kriterini kontrol et
                    if max_score >= test['min_score']:
                        print(f"   ✅ TEST BAŞARILI (Beklenen: ≥{test['min_score']:.1f})")
                        passed_tests += 1
                    else:
                        print(f"   ⚠️  Düşük benzerlik skoru (Beklenen: ≥{test['min_score']:.1f})")
                        
                else:
                    print(f"   ❌ Hiç sonuç bulunamadı")
                    
            else:
                print(f"   ❌ API hatası: {response.status_code}")
                print(f"   Hata: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Zaman aşımı (30s)")
        except Exception as e:
            print(f"   ❌ Hata: {e}")
            
        print("-" * 50)
        time.sleep(1)  # API'ye ara ver
    
    # Özet
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    print(f"Toplam test: {total_tests}")
    print(f"Başarılı: {passed_tests}")
    print(f"Başarısız: {total_tests - passed_tests}")
    print(f"Başarı oranı: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 TÜM TESTLER BAŞARILI! Sistem hackathon için hazır!")
    elif passed_tests >= total_tests * 0.7:
        print("\n✅ Sistem büyük ölçüde çalışıyor. Hackathon için kullanılabilir.")
    else:
        print("\n⚠️  Bazı iyileştirmeler gerekli olabilir.")

if __name__ == "__main__":
    comprehensive_search_test()