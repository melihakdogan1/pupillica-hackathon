#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB gerçek test scripti
"""

import chromadb

def test_chromadb():
    try:
        print("🔍 ChromaDB test başlıyor...")
        
        # ChromaDB bağlantısı
        client = chromadb.PersistentClient(path='./data/chroma_db')
        collection = client.get_collection('drug_info')
        
        # Doküman sayısı
        count = collection.count()
        print(f"📊 Toplam doküman: {count:,}")
        
        # Test aramaları
        test_queries = [
            "aspirin",
            "ağrı kesici", 
            "paracetamol",
            "antibiyotik",
            "vitamin"
        ]
        
        for query in test_queries:
            print(f"\n🔍 '{query}' aranıyor...")
            results = collection.query(
                query_texts=[query], 
                n_results=3
            )
            
            found = len(results['documents'][0])
            print(f"✅ {found} sonuç bulundu")
            
            if found > 0:
                # İlk sonucu göster
                first_doc = results['documents'][0][0]
                print(f"📝 İlk sonuç (ilk 200 karakter):")
                print(f"   {first_doc[:200]}...")
                
                # Metadata var mı?
                if results['metadatas'][0]:
                    metadata = results['metadatas'][0][0]
                    print(f"📋 Metadata: {metadata}")
            else:
                print("❌ Sonuç bulunamadı")
        
        print(f"\n🎯 SONUÇ: Vector database gerçekten {count:,} doküman içeriyor!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_chromadb()