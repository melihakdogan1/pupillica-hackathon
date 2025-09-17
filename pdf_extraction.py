#!/usr/bin/env python3
"""
PUPILLICA - PDF Text Extraction Sistemi
Amaç: PDF prospektüslerinden strukturlu metin çıkarmak
"""

import os
import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from tqdm import tqdm
import re
import hashlib

# Dizinler
DATA_DIR = Path("data")
KT_DIR = DATA_DIR / "kt"
KUB_DIR = DATA_DIR / "kub"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"

class PDFTextExtractor:
    """PDF metin çıkarma sınıfı"""
    
    def __init__(self):
        self.methods = ['pdfplumber', 'pypdf2', 'pymupdf']
        self.stats = {
            'total_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'method_success': {method: 0 for method in self.methods}
        }
    
    def extract_with_pdfplumber(self, pdf_path):
        """pdfplumber ile metin çıkar"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip(), True
        except Exception as e:
            return f"pdfplumber error: {str(e)}", False
    
    def extract_with_pypdf2(self, pdf_path):
        """PyPDF2 ile metin çıkar"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip(), True
        except Exception as e:
            return f"PyPDF2 error: {str(e)}", False
    
    def extract_with_pymupdf(self, pdf_path):
        """PyMuPDF ile metin çıkar"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
            return text.strip(), True
        except Exception as e:
            return f"PyMuPDF error: {str(e)}", False
    
    def extract_text(self, pdf_path):
        """En iyi yöntemle metin çıkar"""
        results = {}
        
        # Her 3 yöntemi dene
        for method in self.methods:
            if method == 'pdfplumber':
                text, success = self.extract_with_pdfplumber(pdf_path)
            elif method == 'pypdf2':
                text, success = self.extract_with_pypdf2(pdf_path)
            elif method == 'pymupdf':
                text, success = self.extract_with_pymupdf(pdf_path)
            
            results[method] = {
                'text': text,
                'success': success,
                'length': len(text) if success else 0
            }
            
            if success:
                self.stats['method_success'][method] += 1
        
        # En iyi sonucu seç (en uzun geçerli metin)
        best_method = None
        best_text = ""
        best_length = 0
        
        for method, result in results.items():
            if result['success'] and result['length'] > best_length:
                best_method = method
                best_text = result['text']
                best_length = result['length']
        
        return best_text, best_method, results
    
    def clean_text(self, text):
        """Metni temizle"""
        if not text:
            return ""
        
        # Çok fazla boşluk ve yeni satırları temizle
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Çoklu boş satırları düzenle
        text = re.sub(r' +', ' ', text)  # Çoklu boşlukları tek yap
        text = text.strip()
        
        return text
    
    def extract_metadata(self, pdf_path):
        """PDF metadata çıkar"""
        metadata = {
            'file_name': pdf_path.name,
            'file_size': pdf_path.stat().st_size,
            'modification_date': datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat()
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata.update({
                    'page_count': len(pdf_reader.pages),
                    'pdf_metadata': dict(pdf_reader.metadata) if pdf_reader.metadata else {}
                })
        except:
            metadata['page_count'] = 0
            metadata['pdf_metadata'] = {}
        
        return metadata

def process_pdf_batch(pdf_files, extractor, batch_name):
    """PDF dosyalarının bir grubunu işle"""
    print(f"📝 {batch_name} dosyaları işleniyor... ({len(pdf_files)} dosya)")
    
    results = []
    
    for pdf_path in tqdm(pdf_files, desc=f"Extracting {batch_name}"):
        extractor.stats['total_processed'] += 1
        
        try:
            # Metin çıkar
            text, best_method, all_results = extractor.extract_text(pdf_path)
            
            # Metadata çıkar
            metadata = extractor.extract_metadata(pdf_path)
            
            # İlaç adını dosya adından çıkar
            drug_name = pdf_path.stem
            if drug_name.endswith('_KT'):
                drug_name = drug_name[:-3]
                doc_type = 'KT'
            elif drug_name.endswith('_KUB'):
                drug_name = drug_name[:-4]
                doc_type = 'KUB'
            else:
                doc_type = 'UNKNOWN'
            
            # Temizle
            clean_text = extractor.clean_text(text)
            
            # Sonuç
            result = {
                'drug_name': drug_name,
                'document_type': doc_type,
                'file_path': str(pdf_path),
                'extracted_text': clean_text,
                'text_length': len(clean_text),
                'extraction_method': best_method,
                'extraction_success': bool(clean_text),
                'metadata': metadata,
                'extraction_results': all_results,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            results.append(result)
            
            if clean_text:
                extractor.stats['successful_extractions'] += 1
            else:
                extractor.stats['failed_extractions'] += 1
        
        except Exception as e:
            print(f"❌ Hata ({pdf_path.name}): {e}")
            extractor.stats['failed_extractions'] += 1
    
    return results

def save_extracted_data(results, output_file):
    """Çıkarılan veriyi kaydet"""
    os.makedirs(output_file.parent, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Sonuçlar kaydedildi: {output_file}")

def generate_extraction_summary(kt_results, kub_results, extractor_stats):
    """Extraction özeti oluştur"""
    total_kt = len(kt_results)
    total_kub = len(kub_results)
    
    kt_success = sum(1 for r in kt_results if r['extraction_success'])
    kub_success = sum(1 for r in kub_results if r['extraction_success'])
    
    kt_avg_length = sum(r['text_length'] for r in kt_results) / total_kt if total_kt else 0
    kub_avg_length = sum(r['text_length'] for r in kub_results) / total_kub if total_kub else 0
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_files_processed': extractor_stats['total_processed'],
        'kt_summary': {
            'total_files': total_kt,
            'successful_extractions': kt_success,
            'success_rate': kt_success/total_kt if total_kt else 0,
            'average_text_length': kt_avg_length
        },
        'kub_summary': {
            'total_files': total_kub,
            'successful_extractions': kub_success,
            'success_rate': kub_success/total_kub if total_kub else 0,
            'average_text_length': kub_avg_length
        },
        'method_performance': extractor_stats['method_success'],
        'overall_stats': extractor_stats
    }
    
    return summary

def main():
    """Ana fonksiyon"""
    print("🚀 PDF TEXT EXTRACTION BAŞLIYOR...")
    print("=" * 60)
    
    # Gerekli kütüphaneleri kontrol et
    try:
        import PyPDF2
        import pdfplumber
        import fitz
        print("✅ Tüm kütüphaneler mevcut")
    except ImportError as e:
        print(f"❌ Eksik kütüphane: {e}")
        print("pip install PyPDF2 pdfplumber PyMuPDF komutunu çalıştırın")
        return
    
    # Extractor oluştur
    extractor = PDFTextExtractor()
    
    # Test için ilk 10 dosyayı işle
    kt_files = list(KT_DIR.glob("*.pdf"))[:10]
    kub_files = list(KUB_DIR.glob("*.pdf"))[:10]
    
    print(f"📊 Test modunda çalışıyor:")
    print(f"  KT dosyaları: {len(kt_files)}")
    print(f"  KUB dosyaları: {len(kub_files)}")
    
    # KT dosyalarını işle
    kt_results = process_pdf_batch(kt_files, extractor, "KT")
    
    # KUB dosyalarını işle
    kub_results = process_pdf_batch(kub_files, extractor, "KUB")
    
    # Sonuçları kaydet
    save_extracted_data(kt_results, EXTRACTED_DIR / "kt_extracted_test.json")
    save_extracted_data(kub_results, EXTRACTED_DIR / "kub_extracted_test.json")
    
    # Özet oluştur
    summary = generate_extraction_summary(kt_results, kub_results, extractor.stats)
    save_extracted_data(summary, EXTRACTED_DIR / "extraction_summary_test.json")
    
    # Sonuçları yazdır
    print(f"\n🎯 EXTRACTION ÖZETI:")
    print(f"  📁 Toplam işlenen: {extractor.stats['total_processed']}")
    print(f"  ✅ Başarılı: {extractor.stats['successful_extractions']}")
    print(f"  ❌ Başarısız: {extractor.stats['failed_extractions']}")
    print(f"  📊 Başarı oranı: {extractor.stats['successful_extractions']/extractor.stats['total_processed']*100:.1f}%")
    
    print(f"\n📈 YÖNTEM PERFORMANSI:")
    for method, success_count in extractor.stats['method_success'].items():
        print(f"  {method}: {success_count} başarılı")
    
    print(f"\n✅ TEST TAMAMLANDI!")
    print(f"📂 Sonuçlar: {EXTRACTED_DIR}")

if __name__ == "__main__":
    main()