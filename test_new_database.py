#!/usr/bin/env python3
"""
Yeni zenginleştirilmiş veritabanını test eden kapsamlı test scripti
"""

import requests
import json
import time
import sys

def test_comprehensive():
    """Kapsamlı API testi"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Pupillica API - Kapsamlı Test")
    print("=" * 50)
    
    # 1. Health Check
    print("1️⃣ Health Check...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ API erişilebilir")
        else:
            print("❌ API erişim sorunu")
            return
    except requests.exceptions.ConnectionError:
        print("❌ API'ye bağlanılamıyor. Sunucu çalışıyor mu?")
        return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return
    
    # 2. Popüler ilaçları test et
    popular_drugs = [
        "parasetamol",
        "parol", 
        "ibuprofen",
        "augmentin",
        "metamizol",
        "a-ferin",
        "omeprazol",
        "lansoprazol",
        "metformin",
        "amlodipin",
        "ramipril",
        "metoprolol",
        "loratadin",
        "siprofloksasin",
        "sefaleksin",
        "sefuroksim",
        "prednizolon"
    ]
    
    print(f"\n2️⃣ {len(popular_drugs)} Popüler İlaç Testi...")
    successful_searches = 0
    
    for drug in popular_drugs:
        print(f"🔍 {drug.upper()} araması...")
        
        search_data = {
            "query": f"{drug} nedir",
            "limit": 3
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/search",
                json=search_data,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                found_results = results.get('found_results', 0)
                
                if found_results > 0:
                    print(f"   ✅ {found_results} sonuç bulundu")
                    successful_searches += 1
                    
                    # İlk sonucu göster
                    if results.get('results'):
                        first_result = results['results'][0]
                        score = first_result.get('similarity_score', 0)
                        doc_name = first_result.get('document_name', 'Bilinmeyen')
                        print(f"   📄 En iyi eşleşme: {doc_name} (Skor: {score:.3f})")
                else:
                    print(f"   ⚠️ Sonuç bulunamadı")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Hata: {e}")
        
        time.sleep(0.5)  # API'yi yormamak için
    
    print(f"\n📊 Test Sonuçları:")
    print(f"   Toplam İlaç: {len(popular_drugs)}")
    print(f"   Başarılı Arama: {successful_searches}")
    print(f"   Başarı Oranı: {(successful_searches/len(popular_drugs)*100):.1f}%")
    
    # 3. Kompleks sorgular
    print(f"\n3️⃣ Kompleks Sorgu Testleri...")
    
    complex_queries = [
        "paracetamol yan etkileri nelerdir",
        "ibuprofen hamilelikte kullanılır mı",
        "antibiyotik kullanım kuralları",
        "ağrı kesici ilaçlar",
        "mide koruyucu ilaçlar",
        "tansiyon ilaçları"
    ]
    
    for query in complex_queries:
        print(f"🔍 '{query}'...")
        
        search_data = {
            "query": query,
            "limit": 2,
            "use_llm": True
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/search",
                json=search_data,
                timeout=60
            )
            
            if response.status_code == 200:
                results = response.json()
                found_results = results.get('found_results', 0)
                llm_answer = results.get('llm_answer', '')
                
                print(f"   ✅ {found_results} sonuç, LLM yanıt uzunluğu: {len(llm_answer)} karakter")
                
                if llm_answer:
                    # LLM yanıtının ilk 100 karakterini göster
                    preview = llm_answer[:100].replace('\n', ' ')
                    print(f"   💬 Yanıt: {preview}...")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Hata: {e}")
        
        time.sleep(1)  # LLM sorguları için daha uzun bekleme
    
    print(f"\n🎉 Test Tamamlandı!")
    print(f"✅ Yeni veritabanı {successful_searches}/{len(popular_drugs)} ilaç ile başarıyla çalışıyor!")

if __name__ == "__main__":
    test_comprehensive()