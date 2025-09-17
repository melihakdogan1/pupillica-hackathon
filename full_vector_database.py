#!/usr/bin/env python3
"""
PUPILLICA - FULL SCALE VECTOR DATABASE
4,816 PDF'den çıkarılan metinleri ChromaDB'ye indexleme
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
import time

# Dizinler
DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"
VECTOR_DB_DIR = PROCESSED_DIR / "vector_db_full"

class PupillicaFullVectorDB:
    """Pupillica Full Scale Vector Database Yönetim Sınıfı"""
    
    def __init__(self, db_path: Path = None, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Vector DB'yi başlat
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
        
        # Collection oluştur
        self.collection = self.client.get_or_create_collection(
            name="pupillica_full",
            metadata={"description": "Pupillica Full Scale Drug Information Database"}
        )
    
    def load_extracted_data(self):
        """Çıkarılan PDF verilerini yükle"""
        
        print("📚 Extracted veriler yükleniyor...")
        
        # KT ve KUB dosyalarını yükle
        kt_file = EXTRACTED_DIR / "kt_extracted_parallel.json"
        kub_file = EXTRACTED_DIR / "kub_extracted_parallel.json"
        
        kt_data = []
        kub_data = []
        
        if kt_file.exists():
            with open(kt_file, 'r', encoding='utf-8') as f:
                kt_data = json.load(f)
            print(f"📋 KT verisi: {len(kt_data)} dosya")
        
        if kub_file.exists():
            with open(kub_file, 'r', encoding='utf-8') as f:
                kub_data = json.load(f)
            print(f"📋 KUB verisi: {len(kub_data)} dosya")
        
        total_data = kt_data + kub_data
        print(f"📊 Toplam: {len(total_data)} dosya yüklendi")
        
        return total_data
    
    def clean_text(self, text: str) -> str:
        """Metni temizle"""
        if not text:
            return ""
        
        # Çok fazla boşluk ve satır sonu temizle
        text = re.sub(r'\s+', ' ', text)
        
        # Başındaki ve sonundaki boşlukları temizle
        text = text.strip()
        
        return text
    
    def create_chunks(self, text: str, chunk_size: int = 300, overlap: int = 30) -> List[str]:
        """Metni chunk'lara böl - optimize edilmiş"""
        
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Son chunk'sa, metni bitir
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Kelime sınırında kes
            chunk = text[start:end]
            last_space = chunk.rfind(' ')
            
            if last_space > chunk_size * 0.7:  # En az %70'inde boşluk varsa
                chunk = chunk[:last_space]
                end = start + last_space
            
            chunks.append(chunk)
            start = end - overlap
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def process_document(self, doc_data: dict) -> List[dict]:
        """Tek dokümanı işle ve chunk'ları oluştur"""
        
        file_path = doc_data['file_path']
        drug_name = doc_data['drug_name']
        text = doc_data['text']
        extraction_method = doc_data['extraction_method']
        
        # Metin tipini belirle
        doc_type = "KT" if "_KT" in file_path else "KUB"
        
        # Metni temizle
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return []
        
        # Chunk'lara böl
        chunks = self.create_chunks(cleaned_text)
        
        # Her chunk için metadata oluştur
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{drug_name}_{doc_type}_{i:03d}"
            
            chunk_data = {
                'chunk_id': chunk_id,
                'text': chunk,
                'metadata': {
                    'drug_name': drug_name,
                    'document_type': doc_type,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_path': file_path,
                    'extraction_method': extraction_method,
                    'text_length': len(chunk),
                    'source_doc_length': len(cleaned_text)
                }
            }
            processed_chunks.append(chunk_data)
        
        return processed_chunks
    
    def batch_embed_and_store(self, chunks: List[dict], batch_size: int = 100):
        """Chunk'ları batch'ler halinde embed edip kaydet"""
        
        print(f"🔄 {len(chunks)} chunk embedding ve kayıt işlemi...")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            # Tekstleri ve metadata'ları ayır
            texts = [chunk['text'] for chunk in batch]
            ids = [chunk['chunk_id'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]
            
            # Embeddings oluştur
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            
            # ChromaDB'ye kaydet
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            print(f"  ✅ Batch {i//batch_size + 1}: {len(batch)} chunk kaydedildi")
    
    def create_full_vector_database(self):
        """Full scale vector database oluştur"""
        
        print("🚀 PUPILLICA FULL SCALE VECTOR DATABASE OLUŞTURULUYOR")
        print("=" * 70)
        
        start_time = time.time()
        
        # Veriyi yükle
        documents = self.load_extracted_data()
        
        if not documents:
            print("❌ Yüklenecek veri bulunamadı!")
            return
        
        # Dokümanları işle
        print(f"\n📝 {len(documents)} doküman işleniyor...")
        all_chunks = []
        
        for doc in tqdm(documents, desc="Dokümanlar işleniyor"):
            chunks = self.process_document(doc)
            all_chunks.extend(chunks)
        
        print(f"✅ Toplam {len(all_chunks)} chunk oluşturuldu")
        
        # İstatistikler
        kt_chunks = len([c for c in all_chunks if c['metadata']['document_type'] == 'KT'])
        kub_chunks = len([c for c in all_chunks if c['metadata']['document_type'] == 'KUB'])
        
        print(f"  📋 KT chunks: {kt_chunks}")
        print(f"  📋 KUB chunks: {kub_chunks}")
        
        # Embedding ve kaydetme
        print(f"\n🤖 Embedding ve ChromaDB'ye kaydetme...")
        self.batch_embed_and_store(all_chunks, batch_size=100)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Final istatistikler
        collection_count = self.collection.count()
        
        print(f"\n🎯 FULL SCALE VECTOR DATABASE TAMAMLANDI!")
        print(f"  📊 Toplam chunks: {collection_count:,}")
        print(f"  ⏱️ İşlem süresi: {processing_time/60:.1f} dakika")
        print(f"  ⚡ Hız: {collection_count/(processing_time/60):.0f} chunk/dakika")
        print(f"  💾 Database boyutu: ~{collection_count * 384 * 4 / (1024**3):.2f} GB")
        
        # Test sorgusu
        self.test_search()
        
        return {
            'total_chunks': collection_count,
            'kt_chunks': kt_chunks,
            'kub_chunks': kub_chunks,
            'processing_time_minutes': processing_time / 60,
            'chunks_per_minute': collection_count / (processing_time / 60)
        }
    
    def test_search(self):
        """Vector database'i test et"""
        
        print(f"\n🔍 VECTOR DATABASE TESTİ:")
        
        test_queries = [
            "paracetamol yan etki",
            "aspirin doz",
            "antibiyotik kullanım",
            "ağrı kesici",
            "ateş düşürücü"
        ]
        
        for query in test_queries:
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results['documents'] and results['documents'][0]:
                doc = results['documents'][0][0]
                metadata = results['metadatas'][0][0]
                distance = results['distances'][0][0]
                
                print(f"  Query: '{query}'")
                print(f"    ✅ En yakın: {metadata['drug_name']} ({metadata['document_type']})")
                print(f"    📊 Distance: {distance:.3f}")
                print(f"    📝 Text: {doc[:100]}...")
                print()

def main():
    """Ana fonksiyon"""
    
    # Vector DB oluştur
    vector_db = PupillicaFullVectorDB()
    
    # Full scale database oluştur
    stats = vector_db.create_full_vector_database()
    
    return stats

if __name__ == "__main__":
    stats = main()