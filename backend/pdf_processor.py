import pymupdf4llm
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
from tqdm import tqdm
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF'lerden metin çıkarma ve işleme sınıfı"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.kub_dir = self.data_dir / "kub"
        self.kt_dir = self.data_dir / "kt"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict:
        """Tek bir PDF'den metin çıkar"""
        try:
            # pymupdf4llm ile text extraction
            md_text = pymupdf4llm.to_markdown(str(pdf_path))
            
            # Metadata
            drug_name = pdf_path.stem.replace('_KUB', '').replace('_KT', '')
            doc_type = 'KUB' if '_KUB' in pdf_path.stem else 'KT'
            
            # Text cleaning ve parsing
            cleaned_text = self.clean_text(md_text)
            structured_data = self.parse_drug_info(cleaned_text, drug_name, doc_type)
            
            return {
                "file_name": pdf_path.name,
                "drug_name": drug_name,
                "document_type": doc_type,
                "raw_text": md_text,
                "cleaned_text": cleaned_text,
                "structured_data": structured_data,
                "file_size": pdf_path.stat().st_size,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"PDF işleme hatası {pdf_path.name}: {e}")
            return {
                "file_name": pdf_path.name,
                "error": str(e),
                "success": False
            }
    
    def clean_text(self, text: str) -> str:
        """Metni temizle ve normalize et"""
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        # Özel karakterleri temizle
        text = re.sub(r'[^\w\s\-\.\,\:\;\!\?]', '', text)
        
        # Türkçe karakterleri koru
        text = text.strip()
        
        return text
    
    def parse_drug_info(self, text: str, drug_name: str, doc_type: str) -> Dict:
        """Metinden yapılandırılmış bilgi çıkar"""
        # Temel bilgi alanları
        info = {
            "drug_name": drug_name,
            "document_type": doc_type,
            "active_ingredient": "",
            "indication": "",
            "dosage": "",
            "side_effects": "",
            "contraindications": "",
            "warnings": "",
            "interactions": ""
        }
        
        # Regex patterns for Turkish medical documents
        patterns = {
            "active_ingredient": r"(?:etkin madde|aktif madde|composition)[:\s]*(.*?)(?:\n|$)",
            "indication": r"(?:endikasyon|kullanım alanı|tedavi)[:\s]*(.*?)(?:\n|$)",
            "dosage": r"(?:doz|posoji|kullanım şekli)[:\s]*(.*?)(?:\n|$)",
            "side_effects": r"(?:yan etki|advers|istenmeyen)[:\s]*(.*?)(?:\n|$)",
            "contraindications": r"(?:kontrendikasyon|kullanılmamalı)[:\s]*(.*?)(?:\n|$)",
            "warnings": r"(?:uyarı|dikkat|önemli)[:\s]*(.*?)(?:\n|$)"
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                info[field] = match.group(1).strip()[:500]  # İlk 500 karakter
        
        return info
    
    def process_batch(self, limit: Optional[int] = None) -> Dict:
        """Toplu PDF işleme"""
        results = {
            "kub_processed": 0,
            "kt_processed": 0,
            "total_success": 0,
            "total_errors": 0,
            "processed_data": []
        }
        
        # KUB dosyalarını işle
        if self.kub_dir.exists():
            kub_files = list(self.kub_dir.glob("*.pdf"))
            if limit:
                kub_files = kub_files[:limit//2]
                
            logger.info(f"🔄 {len(kub_files)} KUB dosyası işleniyor...")
            for pdf_file in tqdm(kub_files, desc="KUB Processing"):
                result = self.extract_text_from_pdf(pdf_file)
                results["processed_data"].append(result)
                
                if result["success"]:
                    results["kub_processed"] += 1
                    results["total_success"] += 1
                else:
                    results["total_errors"] += 1
        
        # KT dosyalarını işle
        if self.kt_dir.exists():
            kt_files = list(self.kt_dir.glob("*.pdf"))
            if limit:
                kt_files = kt_files[:limit//2]
                
            logger.info(f"🔄 {len(kt_files)} KT dosyası işleniyor...")
            for pdf_file in tqdm(kt_files, desc="KT Processing"):
                result = self.extract_text_from_pdf(pdf_file)
                results["processed_data"].append(result)
                
                if result["success"]:
                    results["kt_processed"] += 1
                    results["total_success"] += 1
                else:
                    results["total_errors"] += 1
        
        # Sonuçları kaydet
        output_file = self.processed_dir / "extracted_texts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ İşlem tamamlandı: {results['total_success']} başarılı, {results['total_errors']} hata")
        logger.info(f"📁 Sonuçlar kaydedildi: {output_file}")
        
        return results

def main():
    """Test için ana fonksiyon"""
    processor = PDFProcessor("data")
    
    # İlk 20 dosyayı test et
    results = processor.process_batch(limit=20)
    
    print("\n📊 İşlem Özeti:")
    print(f"KUB dosyaları: {results['kub_processed']}")
    print(f"KT dosyaları: {results['kt_processed']}")
    print(f"Toplam başarılı: {results['total_success']}")
    print(f"Toplam hata: {results['total_errors']}")

if __name__ == "__main__":
    main()