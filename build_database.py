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
DB_PATH = "data/veritabani_optimized"  # Optimized demo veritabanı
COLLECTION_NAME = "ilac_prospektusleri"

# Türkiye'de en sık kullanılan ilaçların optimized listesi (demo için sınırlandırılmış)
POPULAR_DRUGS = [
    "PARASETAMOL", "PAROL", "IBUPROFEN", "ASPIRIN", "METAMIZOL", "A-FERIN", 
    "AUGMENTIN", "AMOKSISILIN", "SEFALEKSIN", "OMEPRAZOL", "LANSOPRAZOL", 
    "METFORMIN", "LORATADIN", "CLARINASE", "VOLTAREN", "DIKLOFENAK",
    "RAMIPRIL", "AMLODIPINE", "METOPROLOL", "CONCOR"
]

# PDF klasörleri
KUB_PATH = "data/kub"
KT_PATH = "data/kt"

# Metin parçalama ayarları (daha küçük chunks için optimize)
CHUNK_SIZE = 800  # Daha küçük parçalar
CHUNK_OVERLAP = 150  # Daha az örtüşme

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
    """Sık kullanılan ilaçlar listesindeki PDF'leri bulur."""
    pdfs = []
    logger.info(f"Sık kullanılan ilaçlar listesine göre PDF'ler aranıyor: {POPULAR_DRUGS}")
    found_drugs = set()

    # Her iki klasörde de ara
    search_paths = [
        (KUB_PATH, "KUB"),
        (KT_PATH, "KT")
    ]
    
    for search_path, doc_type in search_paths:
        if not os.path.exists(search_path):
            logger.warning(f"'{search_path}' klasörü bulunamadı.")
            continue
            
        # Tüm PDF dosyalarını listele
        for pdf_file in Path(search_path).glob("*.pdf"):
            file_name_upper = pdf_file.stem.upper()
            
            # Her ilaç adını dosya adında ara (büyük/küçük harf duyarsız)
            for drug_name in POPULAR_DRUGS:
                if drug_name.upper() in file_name_upper:
                    pdfs.append({
                        "path": str(pdf_file),
                        "type": doc_type,
                        "name": pdf_file.stem
                    })
                    found_drugs.add(drug_name)
                    break  # Bu dosya için sadece bir kez ekle

    logger.info(f"Bulunan sık kullanılan ilaçlar: {sorted(list(found_drugs))}")
    logger.info(f"Toplam bulunan PDF dosyası sayısı: {len(pdfs)}")
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
        logger.error("Hic PDF dosyasi bulunamadi!")
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
        
        # Loglama
        logger.info(f"[{i+1}/{len(pdf_files)}] Isleniyor: {pdf_path}")
        
        text = extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"Metin cikarilamadi: {pdf_path}")
            continue
            
        chunks = chunk_text(text)
        if not chunks:
            logger.warning(f"Metin parcalanamadi: {pdf_path}")
            continue
        
        num_chunks = len(chunks)
        total_chunks += num_chunks
        
        # Her bir chunk için ID ve metadata oluştur
        for j, chunk in enumerate(chunks):
            chunk_id = f"{pdf_name}_{j}"
            
            metadata = {
                "source": pdf_name,
                "type": pdf_type,
                "chunk_index": j,
                "total_chunks_in_doc": num_chunks,
                "pdf_path": pdf_path
            }
            
            batch_docs.append(chunk)
            batch_ids.append(chunk_id)
            batch_metadatas.append(metadata)
            
            # Batch dolduğunda veritabanına ekle
            if len(batch_docs) >= batch_size:
                try:
                    collection.add(
                        documents=batch_docs,
                        ids=batch_ids,
                        metadatas=batch_metadatas
                    )
                    logger.info(f"{len(batch_docs)} parca veritabanina eklendi.")
                    batch_docs, batch_ids, batch_metadatas = [], [], []
                except Exception as e:
                    logger.error(f"Veritabanina ekleme hatasi: {e}")

    # Kalan son batch'i ekle
    if batch_docs:
        try:
            collection.add(
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_metadatas
            )
            logger.info(f"Kalan {len(batch_docs)} parca veritabanina eklendi.")
        except Exception as e:
            logger.error(f"Veritabanina ekleme hatasi (son batch): {e}")

    end_time = time.time()
    duration = end_time - start_time
    
    logger.info("Veritabani olusturma tamamladi.")
    logger.info(f"Toplam islenen PDF sayisi: {len(pdf_files)}")
    logger.info(f"Toplam olusturulan metin parcasi (chunk): {total_chunks}")
    logger.info(f"Islem suresi: {duration:.2f} saniye")
    
    return True

if __name__ == '__main__':
    create_database()