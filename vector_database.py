#!/usr/bin/env python3
"""
PUPILLICA - Vector Database Sistemi
Amaç: PDF'lerden çıkarılan metinleri embedding'e çevirip aranabilir hale getirmek
"""

import os
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import hashlib
from tqdm import tqdm
import re

# Dizinler
DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"
VECTOR_DB_DIR = PROCESSED_DIR / "vector_db"

class PupillicaVectorDB:
    """Pupillica Vector Database Yönetim Sınıfı"""
    
    def __init__(self, db_path: Path = None, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Vector DB'yi başlat
        
        Args:
            db_path: ChromaDB dosya yolu
            embedding_model: Sentence transformer model adı
        """
        self.db_path = db_path or VECTOR_DB_DIR
        self.embedding_model_name = embedding_model
        
        # ChromaDB ayarları
        os.makedirs(self.db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Embedding model yükle
        print(f"🤖 Embedding model yükleniyor: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print(f"✅ Model hazır - Boyut: {self.embedding_model.get_sentence_embedding_dimension()}")
        
        # Collections
        self.kt_collection = None
        self.kub_collection = None
        
    def create_collections(self):
        """ChromaDB koleksiyonlarını oluştur"""
        try:
            # KT (Kullanım Talimatı) koleksiyonu
            self.kt_collection = self.client.create_collection(
                name="pupillica_kt",
                metadata={"description": "İlaç Kullanım Talimatları"}
            )
            print("✅ KT koleksiyonu oluşturuldu")
        except Exception:
            self.kt_collection = self.client.get_collection("pupillica_kt")
            print("📂 KT koleksiyonu mevcut")
        
        try:
            # KUB (Kısa Ürün Bilgisi) koleksiyonu  
            self.kub_collection = self.client.create_collection(
                name="pupillica_kub",
                metadata={"description": "Kısa Ürün Bilgileri (Doktor)"}
            )
            print("✅ KUB koleksiyonu oluşturuldu")
        except Exception:
            self.kub_collection = self.client.get_collection("pupillica_kub")
            print("📂 KUB koleksiyonu mevcut")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Metni chunks'lara böl"""
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Sentence boundary'de kesmeye çalış
            if end < len(text):
                # Son cümle sonunu bul
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                boundary = max(last_period, last_newline)
                
                if boundary > start + chunk_size // 2:  # Chunk'ın yarısından büyükse kabul et
                    end = boundary + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def process_drug_document(self, drug_data: Dict) -> List[Dict]:
        """Tek ilaç dokümanını işle ve chunk'lara böl"""
        drug_name = drug_data.get('drug_name', 'Unknown')
        doc_type = drug_data.get('document_type', 'Unknown')
        text = drug_data.get('extracted_text', '')
        
        if not text:
            return []
        
        # Metni chunk'lara böl
        chunks = self.chunk_text(text)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{drug_name}_{doc_type}_chunk_{i}"
            
            # Embedding oluştur
            embedding = self.embedding_model.encode(chunk).tolist()
            
            chunk_data = {
                'id': chunk_id,
                'text': chunk,
                'embedding': embedding,
                'metadata': {
                    'drug_name': drug_name,
                    'document_type': doc_type,
                    'chunk_index': i,
                    'chunk_count': len(chunks),
                    'file_path': drug_data.get('file_path', ''),
                    'text_length': len(chunk),
                    'processing_timestamp': datetime.now().isoformat()
                }
            }
            
            processed_chunks.append(chunk_data)
        
        return processed_chunks
    
    def add_documents_to_collection(self, collection, documents: List[Dict]):
        """Dokümanları koleksiyona ekle"""
        if not documents:
            return
        
        ids = [doc['id'] for doc in documents]
        embeddings = [doc['embedding'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        documents_text = [doc['text'] for doc in documents]
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents_text
        )
    
    def load_and_process_extracted_data(self, kt_file: Path = None, kub_file: Path = None):
        """Çıkarılan veriyi yükle ve işle"""
        kt_file = kt_file or EXTRACTED_DIR / "kt_extracted_test.json"
        kub_file = kub_file or EXTRACTED_DIR / "kub_extracted_test.json"
        
        print(f"📂 Veri yükleniyor...")
        
        # KT verilerini yükle
        kt_documents = []
        if kt_file.exists():
            with open(kt_file, 'r', encoding='utf-8') as f:
                kt_data = json.load(f)
            
            print(f"📊 KT dosyaları işleniyor: {len(kt_data)}")
            for drug_data in tqdm(kt_data, desc="KT Processing"):
                chunks = self.process_drug_document(drug_data)
                kt_documents.extend(chunks)
            
            print(f"✅ KT chunks: {len(kt_documents)}")
        
        # KUB verilerini yükle
        kub_documents = []
        if kub_file.exists():
            with open(kub_file, 'r', encoding='utf-8') as f:
                kub_data = json.load(f)
            
            print(f"📊 KUB dosyaları işleniyor: {len(kub_data)}")
            for drug_data in tqdm(kub_data, desc="KUB Processing"):
                chunks = self.process_drug_document(drug_data)
                kub_documents.extend(chunks)
            
            print(f"✅ KUB chunks: {len(kub_documents)}")
        
        # Koleksiyonlara ekle
        if kt_documents and self.kt_collection:
            print(f"💾 KT chunks veritabanına ekleniyor...")
            self.add_documents_to_collection(self.kt_collection, kt_documents)
            print(f"✅ {len(kt_documents)} KT chunk eklendi")
        
        if kub_documents and self.kub_collection:
            print(f"💾 KUB chunks veritabanına ekleniyor...")
            self.add_documents_to_collection(self.kub_collection, kub_documents)
            print(f"✅ {len(kub_documents)} KUB chunk eklendi")
        
        return len(kt_documents), len(kub_documents)
    
    def search(self, query: str, collection_type: str = "both", top_k: int = 5) -> List[Dict]:
        """Vector database'de arama yap"""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = []
        
        # KT'de ara
        if collection_type in ["kt", "both"] and self.kt_collection:
            kt_results = self.kt_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            for i in range(len(kt_results['ids'][0])):
                results.append({
                    'id': kt_results['ids'][0][i],
                    'text': kt_results['documents'][0][i],
                    'metadata': kt_results['metadatas'][0][i],
                    'distance': kt_results['distances'][0][i],
                    'collection': 'kt'
                })
        
        # KUB'da ara
        if collection_type in ["kub", "both"] and self.kub_collection:
            kub_results = self.kub_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            for i in range(len(kub_results['ids'][0])):
                results.append({
                    'id': kub_results['ids'][0][i],
                    'text': kub_results['documents'][0][i],
                    'metadata': kub_results['metadatas'][0][i],
                    'distance': kub_results['distances'][0][i],
                    'collection': 'kub'
                })
        
        # Distance'a göre sırala (küçükten büyüğe)
        results.sort(key=lambda x: x['distance'])
        
        return results[:top_k]
    
    def get_collection_stats(self) -> Dict:
        """Koleksiyon istatistikleri"""
        stats = {
            'kt_count': 0,
            'kub_count': 0,
            'total_count': 0
        }
        
        if self.kt_collection:
            stats['kt_count'] = self.kt_collection.count()
        
        if self.kub_collection:
            stats['kub_count'] = self.kub_collection.count()
        
        stats['total_count'] = stats['kt_count'] + stats['kub_count']
        
        return stats

def test_vector_search():
    """Vector search testleri"""
    print("🧪 Vector Search Test Başlıyor...")
    
    # Test sorguları
    test_queries = [
        "parasetamol yan etkileri nelerdir",
        "kalp hastalığı için ilaç",
        "hamilelikte kullanılabilir mi",
        "doz aşımı durumunda ne yapmalı",
        "alerji yapan maddeler"
    ]
    
    vector_db = PupillicaVectorDB()
    vector_db.create_collections()
    
    # Verileri yükle
    kt_count, kub_count = vector_db.load_and_process_extracted_data()
    
    print(f"\n📊 Vector DB İstatistikleri:")
    stats = vector_db.get_collection_stats()
    print(f"  KT chunks: {stats['kt_count']}")
    print(f"  KUB chunks: {stats['kub_count']}")
    print(f"  Toplam: {stats['total_count']}")
    
    print(f"\n🔍 Test Aramaları:")
    for query in test_queries:
        print(f"\n❓ Soru: {query}")
        results = vector_db.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            drug_name = result['metadata'].get('drug_name', 'Unknown')
            collection = result['collection'].upper()
            distance = result['distance']
            text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
            
            print(f"  {i}. [{collection}] {drug_name} (similarity: {1-distance:.3f})")
            print(f"     {text_preview}")
    
    return vector_db

def main():
    """Ana fonksiyon"""
    print("🚀 PUPILLICA VECTOR DATABASE KURULUMU")
    print("=" * 60)
    
    try:
        vector_db = test_vector_search()
        
        print(f"\n✅ VECTOR DATABASE KURULUMU TAMAMLANDI!")
        print(f"📊 Sistem hazır - arama testleri başarılı")
        print(f"🎯 Sonraki adım: Backend API için hazırız!")
        
        return vector_db
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()