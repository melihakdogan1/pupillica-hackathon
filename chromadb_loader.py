#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB Loader - 4,809 Text Dosyasını Yükleme
"""

import os
import json
import re
from pathlib import Path
import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Optional
import time
from tqdm import tqdm

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromaDBLoader:
    def __init__(self, 
                 text_dir: str = "data/processed/extracted_clean",
                 db_path: str = "data/chroma_db", 
                 collection_name: str = "drug_info"):
        
        self.text_dir = Path(text_dir)
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        
        # ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Collection oluştur/al
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"✅ Mevcut collection bulundu: {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "TİTCK İlaç Bilgileri Database"}
            )
            logger.info(f"🆕 Yeni collection oluşturuldu: {collection_name}")
        
        self.stats = {
            "total_files": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "total_chunks": 0,
            "errors": []
        }
    
    def clean_text(self, text: str) -> str:
        """Text temizleme"""
        # Başlık satırlarını kaldır
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Başlık satırlarını atla
            if line.startswith('#'):
                continue
                
            # Boş satırları atla
            if not line:
                continue
                
            # Çok kısa satırları atla
            if len(line) < 10:
                continue
                
            cleaned_lines.append(line)
        
        # Birleştir
        cleaned_text = ' '.join(cleaned_lines)
        
        # Fazla boşlukları temizle
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Unicode karakterleri normalize et
        cleaned_text = cleaned_text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return cleaned_text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Text'i chunk'lara böl"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Son chunk'sa tamamını al
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Kelime sınırında böl
            chunk = text[start:end]
            last_space = chunk.rfind(' ')
            
            if last_space > chunk_size - 200:  # Reasonable word boundary
                chunk = text[start:start + last_space]
                start += last_space + 1
            else:
                start = end
            
            chunks.append(chunk)
            
            # Overlap için geri git
            if start < len(text):
                start = max(0, start - overlap)
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 50]
    
    def extract_metadata(self, filename: str, text: str) -> Dict:
        """Dosyadan metadata çıkar"""
        # Dosya tipi (KT veya KUB)
        doc_type = "KT" if filename.startswith("kt_") else "KUB"
        
        # İlaç adını dosya adından çıkar
        drug_name = filename.replace("kt_", "").replace("kub_", "").replace(".txt", "")
        drug_name = drug_name.replace("_", " ").strip()
        
        # Text'ten bilgi çıkar
        text_sample = text[:500].upper()
        
        # Kategori tespiti
        category = "DİĞER"
        if any(keyword in text_sample for keyword in ["ANTİBİYOTİK", "ANTIBIYOTIC"]):
            category = "ANTİBİYOTİK"
        elif any(keyword in text_sample for keyword in ["AĞRI", "ANALJEZI", "AĞRI KESİCİ"]):
            category = "AĞRI KESİCİ"
        elif any(keyword in text_sample for keyword in ["VİTAMİN", "VITAMIN"]):
            category = "VİTAMİN"
        elif any(keyword in text_sample for keyword in ["KARDIAK", "KALP", "HIPERTANSIYON"]):
            category = "KARDİYOVASKÜLER"
        elif any(keyword in text_sample for keyword in ["ANTİDEPRESAN", "PSİKİATRİK"]):
            category = "PSİKİATRİK"
        
        return {
            "drug_name": drug_name,
            "document_type": doc_type,
            "category": category,
            "filename": filename,
            "text_length": len(text)
        }
    
    def load_texts_to_chromadb(self):
        """Ana yükleme fonksiyonu"""
        logger.info("🚀 ChromaDB yükleme başlıyor...")
        
        # Text dosyalarını bul
        text_files = list(self.text_dir.glob("*.txt"))
        self.stats["total_files"] = len(text_files)
        
        logger.info(f"📊 {len(text_files)} text dosyası bulundu")
        
        if not text_files:
            logger.error("❌ Hiç text dosyası bulunamadı!")
            return False
        
        start_time = time.time()
        
        # Batch processing için listeler
        batch_size = 100
        documents = []
        metadatas = []
        ids = []
        
        for i, text_file in enumerate(tqdm(text_files, desc="📄 Processing files")):
            try:
                # Dosyayı oku
                with open(text_file, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
                
                if len(raw_text.strip()) < 100:
                    logger.warning(f"⏭️ Çok kısa dosya atlandı: {text_file.name}")
                    continue
                
                # Text temizle
                cleaned_text = self.clean_text(raw_text)
                
                if len(cleaned_text) < 100:
                    logger.warning(f"⏭️ Temizleme sonrası çok kısa: {text_file.name}")
                    continue
                
                # Metadata çıkar
                metadata = self.extract_metadata(text_file.name, cleaned_text)
                
                # Text'i chunk'lara böl
                chunks = self.chunk_text(cleaned_text)
                
                # Her chunk için document oluştur
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id = f"{text_file.stem}_chunk_{chunk_idx}"
                    
                    documents.append(chunk)
                    
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                        "chunk_id": doc_id
                    })
                    metadatas.append(chunk_metadata)
                    ids.append(doc_id)
                    
                    self.stats["total_chunks"] += 1
                
                self.stats["successful"] += 1
                
                # Batch yükleme
                if len(documents) >= batch_size:
                    self._upload_batch(documents, metadatas, ids)
                    documents = []
                    metadatas = []
                    ids = []
                
            except Exception as e:
                logger.error(f"❌ Hata {text_file.name}: {e}")
                self.stats["failed"] += 1
                self.stats["errors"].append(f"{text_file.name}: {str(e)}")
            
            self.stats["processed"] += 1
            
            # Progress log
            if (i + 1) % 100 == 0:
                logger.info(f"📊 Progress: {i+1}/{len(text_files)} - {self.stats['total_chunks']} chunks")
        
        # Son batch'i yükle
        if documents:
            self._upload_batch(documents, metadatas, ids)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final stats
        logger.info("=" * 60)
        logger.info("🎯 CHROMADB YÜKLEME TAMAMLANDI!")
        logger.info(f"⏱️ Süre: {duration:.2f} saniye")
        logger.info(f"📁 İşlenen dosya: {self.stats['successful']}/{self.stats['total_files']}")
        logger.info(f"📄 Toplam chunks: {self.stats['total_chunks']}")
        logger.info(f"💾 ChromaDB kayıtları: {self.collection.count()}")
        
        if self.stats["errors"]:
            logger.info(f"⚠️ İlk 5 hata:")
            for error in self.stats["errors"][:5]:
                logger.info(f"  - {error}")
        
        return True
    
    def _upload_batch(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Batch halinde ChromaDB'ye yükle"""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.debug(f"✅ {len(documents)} chunks yüklendi")
        except Exception as e:
            logger.error(f"❌ Batch yükleme hatası: {e}")
            raise

def main():
    loader = ChromaDBLoader()
    success = loader.load_texts_to_chromadb()
    
    if success:
        print(f"\n🎯 BAŞARILI! {loader.stats['total_chunks']} chunks ChromaDB'ye yüklendi!")
        
        # Test arama
        print("\n🔍 Test arama yapılıyor...")
        results = loader.collection.query(
            query_texts=["aspirin ağrı kesici"],
            n_results=3
        )
        print(f"✅ Test sonucu: {len(results['documents'][0])} sonuç bulundu")
        
        if results['documents'][0]:
            print(f"📝 İlk sonuç: {results['documents'][0][0][:200]}...")
    else:
        print("❌ Yükleme başarısız!")

if __name__ == "__main__":
    main()