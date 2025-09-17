#!/usr/bin/env python3
"""
İlaç Asistanı API Test Suite
Quick tests for deployment verification
"""

import requests
import time
import json

# Configuration
LOCAL_API = "http://localhost:8000"
PROD_API = "https://ilacasistan.vercel.app/api"

def test_api(base_url, name):
    """Test API endpoints"""
    print(f"\n🧪 Testing {name} API: {base_url}")
    
    try:
        # Health check
        print("  📊 Health check...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data['status']}")
            print(f"  📚 Documents: {data.get('total_documents', 0):,}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
        
        # Search test
        print("  🔍 Search test...")
        search_queries = [
            "paracetamol",
            "ağrı kesici", 
            "yan etki",
            "antibiyotik"
        ]
        
        for query in search_queries:
            start_time = time.time()
            response = requests.get(
                f"{base_url}/search",
                params={"q": query, "limit": 3},
                timeout=15
            )
            search_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('total_results', 0)
                api_time = data.get('search_time_ms', 0)
                print(f"  ✅ '{query}': {results} results ({search_time}ms total, {api_time}ms API)")
            else:
                print(f"  ❌ Search '{query}' failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connection error: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🚀 İlaç Asistanı API Test Suite")
    print("=" * 50)
    
    # Test local API
    local_ok = test_api(LOCAL_API, "LOCAL")
    
    # Test production API (if available)
    prod_ok = test_api(PROD_API, "PRODUCTION")
    
    print("\n📋 Test Summary:")
    print(f"  Local API: {'✅ PASS' if local_ok else '❌ FAIL'}")
    print(f"  Production API: {'✅ PASS' if prod_ok else '❌ FAIL'}")
    
    if local_ok:
        print("\n🌐 Ready for deployment!")
        print("   Next steps:")
        print("   1. vercel login")
        print("   2. vercel --prod")
        print("   3. Test production URL")
    
    return local_ok and prod_ok

if __name__ == "__main__":
    run_tests()