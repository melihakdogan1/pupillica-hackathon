#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB durum kontrolü
"""

import chromadb
import os

def check_chromadb_status():
    try:
        print("🔍 ChromaDB durumu kontrol ediliyor...")
        
        # Klasör kontrolü
        db_path = './data/chroma_db'
        if os.path.exists(db_path):
            print(f"✅ ChromaDB klasörü mevcut: {db_path}")
            
            # Klasör içeriği
            files = os.listdir(db_path)
            print(f"📁 Klasör içeriği: {files}")
        else:
            print(f"❌ ChromaDB klasörü bulunamadı: {db_path}")
            return
        
        # ChromaDB bağlantısı
        client = chromadb.PersistentClient(path=db_path)
        
        # Mevcut collection'lar
        collections = client.list_collections()
        print(f"📚 Mevcut collections: {len(collections)}")
        
        for collection in collections:
            print(f"   - {collection.name}: {collection.count()} documents")
            
        if not collections:
            print("❌ Hiç collection bulunamadı!")
            print("💡 Yeni collection oluşturulması gerekiyor")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    check_chromadb_status()