#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ SÜRAHIYEN HIZINDA PDF PROCESSING! ⚡
5,275 PDF'i paralel olarak text extraction + ChromaDB loading
"""

import os
import sys
import time
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import chromadb
import hashlib
import json
from typing import List, Dict, Optional, Tuple
import traceback

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"❌ Eksik kütüphane: {e}")
    print("📦 Kurulum: pip install PyPDF2 pdfplumber sentence-transformers")
    sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RapidPDFProcessor:
    def __init__(self):
        self.base_dir = Path("C:/pupillicaHackathon")
        self.kt_dir = self.base_dir / "data/kt"
        self.kub_dir = self.base_dir / "data/kub"
        self.processed_dir = self.base_dir / "data/processed/extracted"
        self.vector_db_path = self.base_dir / "data/chroma_db"
        
        # Create directories
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.total_files = 0
        self.processed_files = 0
        self.failed_files = 0
        self.start_time = time.time()
        
        # Process tracking
        self.processed_hashes = set()
        self.load_processed_hashes()
        
    def load_processed_hashes(self):
        """Daha önce process edilmiş dosyaları yükle"""
        hash_file = self.processed_dir / "processed_hashes.json"
        if hash_file.exists():
            try:
                with open(hash_file, 'r') as f:
                    data = json.load(f)
                    self.processed_hashes = set(data.get('hashes', []))
                logger.info(f"📋 {len(self.processed_hashes)} dosya hash'i yüklendi")
            except Exception as e:
                logger.warning(f"Hash dosyası yüklenemedi: {e}")
    
    def save_processed_hash(self, file_hash: str):
        """Process edilmiş dosya hash'ini kaydet"""
        self.processed_hashes.add(file_hash)
        hash_file = self.processed_dir / "processed_hashes.json"
        try:
            with open(hash_file, 'w') as f:
                json.dump({'hashes': list(self.processed_hashes)}, f)
        except Exception as e:
            logger.warning(f"Hash kayıt hatası: {e}")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Dosya hash'i hesapla"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                # İlk 8KB'ı hash'le (hız için)
                chunk = f.read(8192)
                hasher.update(chunk)
                hasher.update(str(file_path.stat().st_size).encode())
        except:
            return None
        return hasher.hexdigest()
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[Dict]:
        """PDF'den text extract et"""
        try:
            # Hash kontrolü
            file_hash = self.get_file_hash(pdf_path)
            if file_hash in self.processed_hashes:
                return None  # Daha önce process edilmiş
            
            text_content = ""
            metadata = {
                "file_name": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size": pdf_path.stat().st_size,
                "file_hash": file_hash,
                "source_type": "kt" if "/kt/" in str(pdf_path) else "kub",
                "extraction_method": "pdfplumber"
            }
            
            # PDFPlumber ile deneme (daha kaliteli)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages[:50]):  # İlk 50 sayfa (hız)
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_content += f"\\n\\n--- Sayfa {page_num + 1} ---\\n{page_text}"
                        except:
                            continue
                            
                if len(text_content) < 100:  # Çok az text varsa PyPDF2 dene
                    raise Exception("Insufficient text from pdfplumber")
                    
                metadata["extraction_method"] = "pdfplumber"
                
            except Exception as e:
                # PyPDF2 ile fallback
                try:
                    with open(pdf_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num in range(min(len(pdf_reader.pages), 50)):  # İlk 50 sayfa
                            try:
                                page = pdf_reader.pages[page_num]
                                page_text = page.extract_text()
                                if page_text:
                                    text_content += f"\\n\\n--- Sayfa {page_num + 1} ---\\n{page_text}"
                            except:
                                continue
                    metadata["extraction_method"] = "PyPDF2"
                    
                except Exception as e2:
                    logger.error(f"❌ PDF extraction failed for {pdf_path.name}: {e2}")
                    return None
            
            # Text temizleme
            text_content = text_content.strip()
            if len(text_content) < 50:
                logger.warning(f"⚠️ Az text: {pdf_path.name} - {len(text_content)} karakter")
                return None
            
            # Metadata güncelleme
            metadata["text_length"] = len(text_content)
            metadata["page_count"] = text_content.count("--- Sayfa")
            
            # Hash'i kaydet
            self.save_processed_hash(file_hash)
            
            return {
                "text": text_content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ PDF processing hatası {pdf_path.name}: {e}")
            return None
    
    def get_pdf_files(self) -> List[Path]:
        """Tüm PDF dosyalarını bul"""
        pdf_files = []
        
        # KT klasörü
        if self.kt_dir.exists():
            kt_files = list(self.kt_dir.glob("*.pdf"))
            pdf_files.extend(kt_files)
            logger.info(f"📁 KT klasörü: {len(kt_files)} PDF")
        
        # KUB klasörü  
        if self.kub_dir.exists():
            kub_files = list(self.kub_dir.glob("*.pdf"))
            pdf_files.extend(kub_files)
            logger.info(f"📁 KUB klasörü: {len(kub_files)} PDF")
        
        self.total_files = len(pdf_files)
        logger.info(f"🎯 Toplam: {self.total_files} PDF dosyası bulundu")
        
        return pdf_files
    
    def process_batch(self, pdf_files: List[Path], batch_size: int = 100) -> List[Dict]:
        """PDF'leri batch halinde process et"""
        results = []
        
        # CPU sayısına göre worker sayısı
        max_workers = min(cpu_count(), 8)  # Max 8 worker
        logger.info(f"🚀 {max_workers} parallel worker ile processing başlıyor...")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit batch
            future_to_file = {
                executor.submit(self.extract_text_from_pdf, pdf_file): pdf_file 
                for pdf_file in pdf_files[:batch_size]
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                pdf_file = future_to_file[future]
                try:
                    result = future.result(timeout=30)  # 30 saniye timeout
                    if result:
                        results.append(result)
                        self.processed_files += 1
                    else:
                        self.failed_files += 1
                        
                    # Progress raporu
                    if (self.processed_files + self.failed_files) % 50 == 0:
                        elapsed = time.time() - self.start_time
                        rate = (self.processed_files + self.failed_files) / elapsed
                        eta = (self.total_files - self.processed_files - self.failed_files) / rate
                        
                        logger.info(f"⚡ Progress: {self.processed_files}/{self.total_files} "
                                  f"({self.processed_files/self.total_files*100:.1f}%) "
                                  f"- Rate: {rate:.1f} files/sec - ETA: {eta/60:.1f} min")
                        
                except Exception as e:
                    logger.error(f"❌ Worker error for {pdf_file.name}: {e}")
                    self.failed_files += 1
        
        return results
    
    def save_extracted_texts(self, results: List[Dict]):
        """Extract edilmiş textleri kaydet"""
        for i, result in enumerate(results):
            try:
                # Dosya adı
                file_name = f"extracted_{i:06d}_{result['metadata']['file_hash'][:8]}.json"
                output_path = self.processed_dir / file_name
                
                # JSON olarak kaydet
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                logger.error(f"❌ Text kayıt hatası: {e}")
    
    def run_rapid_processing(self, batch_size: int = 500):
        """Hızlı processing'i başlat"""
        logger.info("🚀 SÜRAHİYA HIZINDA PDF PROCESSING BAŞLIYOR!")
        
        # PDF dosyalarını bul
        pdf_files = self.get_pdf_files()
        if not pdf_files:
            logger.error("❌ PDF dosyası bulunamadı!")
            return False
        
        # Batch'ler halinde process et
        all_results = []
        for i in range(0, len(pdf_files), batch_size):
            batch = pdf_files[i:i+batch_size]
            logger.info(f"📦 Batch {i//batch_size + 1}: {len(batch)} dosya")
            
            batch_results = self.process_batch(batch, len(batch))
            all_results.extend(batch_results)
            
            # Intermediate save
            if batch_results:
                self.save_extracted_texts(batch_results)
                
            logger.info(f"✅ Batch tamamlandı: {len(batch_results)} başarılı")
        
        # Final sonuçlar
        elapsed = time.time() - self.start_time
        success_rate = (self.processed_files / self.total_files) * 100
        
        logger.info(f"")
        logger.info(f"🎯 PROCESSING TAMAMLANDI!")
        logger.info(f"📊 Toplam dosya: {self.total_files}")
        logger.info(f"✅ Başarılı: {self.processed_files} ({success_rate:.1f}%)")
        logger.info(f"❌ Başarısız: {self.failed_files}")
        logger.info(f"⏱️ Süre: {elapsed/60:.1f} dakika")
        logger.info(f"⚡ Ortalama hız: {self.total_files/elapsed:.1f} dosya/saniye")
        logger.info(f"💾 Extracted files: {len(list(self.processed_dir.glob('*.json')))}")
        
        return len(all_results) > 0

if __name__ == "__main__":
    processor = RapidPDFProcessor()
    success = processor.run_rapid_processing(batch_size=200)
    
    if success:
        print("🎉 PDF Processing tamamlandı! ChromaDB loading'e geçiliyor...")
    else:
        print("❌ PDF Processing başarısız!")
        sys.exit(1)