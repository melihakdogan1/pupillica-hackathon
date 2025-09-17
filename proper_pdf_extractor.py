#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Düzgün PDF Text Extraction
5,275 PDF'den text çıkarma sistemi
"""

import os
import json
from pathlib import Path
import PyPDF2
import logging
from typing import Dict, List, Optional
import time

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.kt_path = self.base_path / "kt"
        self.kub_path = self.base_path / "kub" 
        self.output_path = self.base_path / "processed" / "extracted_clean"
        self.progress_file = self.base_path / "processed" / "extraction_progress.json"
        
        # Output klasörü oluştur
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "total_files": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
    
    def load_progress(self) -> Dict:
        """Önceki progress'i yükle"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"processed_files": []}
    
    def save_progress(self, progress: Dict):
        """Progress'i kaydet"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """Tek PDF'den text çıkar"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if len(pdf_reader.pages) == 0:
                    return None
                
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_parts.append(page_text.strip())
                    except Exception as e:
                        logger.warning(f"Sayfa {page_num} hatası {pdf_path.name}: {e}")
                        continue
                
                full_text = "\n\n".join(text_parts)
                
                # Minimum text kontrolü
                if len(full_text.strip()) < 50:
                    return None
                    
                return full_text
                
        except Exception as e:
            logger.error(f"PDF okuma hatası {pdf_path.name}: {e}")
            return None
    
    def process_directory(self, source_dir: Path, dir_type: str) -> List[Dict]:
        """Bir klasördeki tüm PDF'leri process et"""
        results = []
        
        if not source_dir.exists():
            logger.warning(f"Klasör bulunamadı: {source_dir}")
            return results
        
        pdf_files = list(source_dir.glob("*.pdf"))
        logger.info(f"📁 {dir_type} klasöründe {len(pdf_files)} PDF bulundu")
        
        progress = self.load_progress()
        processed_files = set(progress.get("processed_files", []))
        
        for i, pdf_file in enumerate(pdf_files, 1):
            # Skip eğer daha önce process edilmişse
            file_key = f"{dir_type}_{pdf_file.name}"
            if file_key in processed_files:
                logger.info(f"⏭️ Atlanıyor (daha önce process edildi): {pdf_file.name}")
                continue
            
            logger.info(f"📄 [{i}/{len(pdf_files)}] İşleniyor: {pdf_file.name}")
            
            # Text extraction
            extracted_text = self.extract_text_from_pdf(pdf_file)
            
            if extracted_text:
                # Text dosyasını kaydet
                output_file = self.output_path / f"{dir_type}_{pdf_file.stem}.txt"
                
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Kaynak: {pdf_file.name}\n")
                        f.write(f"# Tür: {dir_type.upper()}\n")
                        f.write(f"# İşlem Tarihi: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(extracted_text)
                    
                    result = {
                        "source_file": str(pdf_file),
                        "output_file": str(output_file),
                        "type": dir_type,
                        "text_length": len(extracted_text),
                        "success": True
                    }
                    results.append(result)
                    self.stats["successful"] += 1
                    
                    # Progress güncelle
                    processed_files.add(file_key)
                    
                    logger.info(f"✅ Başarılı: {len(extracted_text)} karakter")
                    
                except Exception as e:
                    logger.error(f"Dosya yazma hatası {output_file}: {e}")
                    self.stats["failed"] += 1
                    self.stats["errors"].append(f"{pdf_file.name}: {str(e)}")
            else:
                logger.warning(f"❌ Text çıkarılamadı: {pdf_file.name}")
                self.stats["failed"] += 1
                self.stats["errors"].append(f"{pdf_file.name}: Text extraction failed")
            
            self.stats["processed"] += 1
            
            # Her 10 dosyada bir progress kaydet
            if self.stats["processed"] % 10 == 0:
                progress["processed_files"] = list(processed_files)
                self.save_progress(progress)
                logger.info(f"📊 Progress: {self.stats['processed']}/{self.stats['total_files']} - {self.stats['successful']} başarılı")
        
        # Final progress save
        progress["processed_files"] = list(processed_files)
        self.save_progress(progress)
        
        return results
    
    def run_extraction(self):
        """Ana extraction process"""
        logger.info("🚀 PDF Text Extraction başlıyor...")
        
        # Toplam dosya sayısını hesapla
        kt_files = list(self.kt_path.glob("*.pdf")) if self.kt_path.exists() else []
        kub_files = list(self.kub_path.glob("*.pdf")) if self.kub_path.exists() else []
        
        self.stats["total_files"] = len(kt_files) + len(kub_files)
        logger.info(f"📊 Toplam: {len(kt_files)} KT + {len(kub_files)} KUB = {self.stats['total_files']} PDF")
        
        start_time = time.time()
        
        # KT dosyalarını process et
        if kt_files:
            logger.info("📁 KT dosyaları işleniyor...")
            kt_results = self.process_directory(self.kt_path, "kt")
        
        # KUB dosyalarını process et  
        if kub_files:
            logger.info("📁 KUB dosyaları işleniyor...")
            kub_results = self.process_directory(self.kub_path, "kub")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final istatistikler
        logger.info("=" * 60)
        logger.info("🎯 EXTRACTION TAMAMLANDI!")
        logger.info(f"⏱️ Süre: {duration:.2f} saniye")
        logger.info(f"📊 Toplam: {self.stats['total_files']} dosya")
        logger.info(f"✅ Başarılı: {self.stats['successful']} dosya")
        logger.info(f"❌ Başarısız: {self.stats['failed']} dosya")
        logger.info(f"📁 Çıktı klasörü: {self.output_path}")
        
        if self.stats["errors"]:
            logger.info(f"⚠️ İlk 5 hata:")
            for error in self.stats["errors"][:5]:
                logger.info(f"  - {error}")
        
        # Stats dosyasını kaydet
        stats_file = self.base_path / "processed" / "extraction_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        return self.stats

def main():
    extractor = PDFExtractor()
    stats = extractor.run_extraction()
    
    print(f"\n🎯 ÖZET: {stats['successful']}/{stats['total_files']} dosya başarıyla işlendi")

if __name__ == "__main__":
    main()