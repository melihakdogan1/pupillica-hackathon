import requests
import json

def quick_test():
    base_url = "http://127.0.0.1:8001"
    
    print("🧪 Hızlı API Testi")
    print("="*30)
    
    # Health check
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ API Status: {response.status_code}")
    except Exception as e:
        print(f"❌ API bağlantı hatası: {e}")
        return
    
    # Basit arama testi
    print("\n🔍 PARASETAMOL araması...")
    search_data = {"query": "parasetamol", "limit": 3}
    
    try:
        response = requests.post(f"{base_url}/search", json=search_data, timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ {results.get('found_results', 0)} sonuç bulundu")
            
            for i, result in enumerate(results.get('results', [])[:2]):
                print(f"  {i+1}. {result.get('document_name', 'Bilinmeyen')}")
                print(f"     Skor: {result.get('similarity_score', 0):.3f}")
        else:
            print(f"❌ Arama hatası: {response.status_code}")
    except Exception as e:
        print(f"❌ Arama hatası: {e}")

if __name__ == "__main__":
    quick_test()