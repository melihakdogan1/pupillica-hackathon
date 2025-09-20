import requests
import json

# Basit test
url = "http://127.0.0.1:8001/search"
data = {"query": "parasetamol", "limit": 2, "use_llm": False}

print("🔍 PARASETAMOL araması yapılıyor...")
try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result.get('found_results', 0)} sonuç bulundu")
        
        for i, res in enumerate(result.get('results', [])[:2]):
            print(f"{i+1}. {res.get('document_name', 'Bilinmeyen')}")
            print(f"   Skor: {res.get('similarity_score', 0):.3f}")
    else:
        print(f"❌ Hata: {response.text}")
        
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")

print("Test bitti!")