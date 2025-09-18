#!/usr/bin/env python3
"""
İlaç Veritabanı Oluşturucu
data/kub ve data/kt klasörlerindeki TÜM PDF'leri işleyerek anlamsal arama veritabanı oluşturur.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import PyPDF2
import pdfplumber
from tqdm import tqdm

# --- Konfigürasyon ---
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
DISTANCE_FUNCTION = "cosine"
DB_PATH = "data/veritabani"
COLLECTION_NAME = "ilac_prospektusleri"

# PDF klasörleri
KUB_PATH = "data/kub"
KT_PATH = "data/kt"

# Metin parçalama ayarları
CHUNK_SIZE = 1000  # Karakter sayısı
CHUNK_OVERLAP = 200  # Örtüşme

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('veritabani_olusturma.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF'den metin çıkarır."""
    text = ""
    
    # Önce pdfplumber ile deneyelim
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.warning(f"pdfplumber ile okuma başarısız {pdf_path}: {e}")
    
    # pdfplumber başarısızsa PyPDF2 ile deneyelim
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"PDF okuma başarısız {pdf_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Metni örtüşen parçalara böler."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Kelime sınırlarında kesmeye çalış
        if end < len(text):
            # Geriye doğru en yakın boşluğu bul
            while end > start and text[end] not in [' ', '\n', '.', '!', '?']:
                end -= 1
            
            if end == start:  # Boşluk bulunamadıysa orijinal konumu kullan
                end = start + chunk_size
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def find_all_pdfs() -> List[Dict[str, str]]:
    """KUB ve KT klasörlerindeki tüm PDF'leri bulur."""
    pdfs = []
    
    # KUB PDF'leri
    if os.path.exists(KUB_PATH):
        for pdf_file in Path(KUB_PATH).glob("*.pdf"):
            pdfs.append({
                "path": str(pdf_file),
                "type": "KUB",
                "name": pdf_file.stem
            })
    
    # KT PDF'leri
    if os.path.exists(KT_PATH):
        for pdf_file in Path(KT_PATH).glob("*.pdf"):
            pdfs.append({
                "path": str(pdf_file),
                "type": "KT", 
                "name": pdf_file.stem
            })
    
    return pdfs

def create_database():
    """Ana veritabanı oluşturma fonksiyonu."""
    logger.info("İlaç Veritabanı Oluşturma Başlıyor...")
    start_time = time.time()
    
    # --- 1. Embedding Fonksiyonunu Yükle ---
    logger.info(f"{EMBEDDING_MODEL} modeli yükleniyor...")
    try:
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            device="cpu"
        )
        logger.info("Embedding modeli başarıyla yüklendi.")
    except Exception as e:
        logger.error(f"Embedding modeli yüklenemedi: {e}")
        return False
    
    # --- 2. ChromaDB İstemcisini Başlat ---
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(
        path=DB_PATH,
        settings=Settings(allow_reset=True, anonymized_telemetry=False)
    )
    
    # Eski koleksiyonu sil ve yenisini oluştur
    try:
        client.delete_collection(name=COLLECTION_NAME)
        logger.info("Eski koleksiyon silindi.")
    except:
        pass
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": DISTANCE_FUNCTION},
        embedding_function=sentence_transformer_ef
    )
    logger.info(f"'{COLLECTION_NAME}' koleksiyonu '{DISTANCE_FUNCTION}' mesafe fonksiyonu ile oluşturuldu.")
    
    # --- 3. PDF'leri Bul ---
    pdf_files = find_all_pdfs()
    logger.info(f"Toplam {len(pdf_files)} PDF dosyası bulundu.")
    
    if not pdf_files:
        logger.error("❌ Hiç PDF dosyası bulunamadı!")
        return False
    
    # --- 4. PDF'leri İşle ---
    total_chunks = 0
    batch_size = 50  # Bellek kullanımını kontrol etmek için
    batch_docs = []
    batch_ids = []
    batch_metadatas = []
    
    for i, pdf_info in enumerate(tqdm(pdf_files, desc="PDF'ler işleniyor")):
        pdf_path = pdf_info["path"]
        pdf_type = pdf_info["type"]
        pdf_name = pdf_info["name"]
        
        # PDF'den metin çıkar
        text = extract_text_from_pdf(pdf_path)
        
        if not text or len(text) < 100:
            logger.warning(f"Boş veya çok kısa metin: {pdf_name}")
            continue
        
        # Metni parçalara böl
        chunks = chunk_text(text)
        
        for j, chunk in enumerate(chunks):
            if len(chunk) < 50:  # Çok kısa parçaları atla
                continue
            
            doc_id = f"{pdf_type}_{pdf_name}_{j}"
            
            batch_docs.append(chunk)
            batch_ids.append(doc_id)
            batch_metadatas.append({
                "pdf_name": pdf_name,
                "pdf_type": pdf_type,
                "chunk_index": j,
                "chunk_length": len(chunk),
                "source_path": pdf_path
            })
            
            total_chunks += 1
        
        # Belirli aralıklarla veritabanına ekle
        if len(batch_docs) >= batch_size:
            try:
                collection.add(
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metadatas
                )
                logger.info(f"{len(batch_docs)} parça veritabanına eklendi. (Toplam: {total_chunks})")
                
                # Batch'i temizle
                batch_docs = []
                batch_ids = []
                batch_metadatas = []
                
            except Exception as e:
                logger.error(f"❌ Batch ekleme hatası: {e}")
                return False
    
    # Kalan parçaları ekle
    if batch_docs:
        try:
            collection.add(
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_metadatas
            )
            logger.info(f"✅ Son {len(batch_docs)} parça eklendi.")
        except Exception as e:
            logger.error(f"❌ Son batch ekleme hatası: {e}")
            return False
    
    # --- 5. Sonuçları Doğrula ---
    final_count = collection.count()
    duration = time.time() - start_time
    
    logger.info(f"📊 Veritabanı oluşturma tamamlandı!")
    logger.info(f"📈 İşlenen PDF sayısı: {len(pdf_files)}")
    logger.info(f"📈 Toplam metin parçası: {final_count}")
    logger.info(f"⏱️ Süre: {duration:.2f} saniye")
    
    # Test sorgusu
    if final_count > 0:
        logger.info("🔍 Test sorgusu yapılıyor...")
        test_results = collection.query(
            query_texts=["parol"],
            n_results=3,
            include=['documents', 'distances', 'metadatas']
        )
        
        if test_results and test_results['documents'][0]:
            logger.info("✅ Test sorgusu başarılı!")
            for i, (doc, dist, meta) in enumerate(zip(
                test_results['documents'][0],
                test_results['distances'][0], 
                test_results['metadatas'][0]
            )):
                similarity = 1 - dist
                logger.info(f"   {i+1}. Benzerlik: {similarity:.3f} | PDF: {meta['pdf_name']} | Tip: {meta['pdf_type']}")
                logger.info(f"      Metin: {doc[:100]}...")
        else:
            logger.warning("⚠️ Test sorgusu sonuç vermedi.")
    
    return True

if __name__ == "__main__":
    success = create_database()
    if success:
        logger.info("🎉 İlaç veritabanı başarıyla oluşturuldu!")
    else:
        logger.error("❌ Veritabanı oluşturma başarısız!")