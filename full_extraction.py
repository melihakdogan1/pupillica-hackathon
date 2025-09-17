#!/usr/bin/env python3
"""
PUPILLICA - FULL SCALE PDF EXTRACTION
Amaç: Tüm 5,275 PDF'i işleyip text extraction yapmak
"""

import os
import json
from pathlib import Path
from pdf_extraction import PDFTextExtractor
from tqdm import tqdm
import multiprocessing as mp
from datetime import datetime
import pandas as pd

# Dizinler
DATA_DIR = Path("data")
KT_DIR = DATA_DIR / "kt"
KUB_DIR = DATA_DIR / "kub"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"

def get_all_pdfs():
    """Tüm PDF dosyalarını listele"""
    
    kt_files = list(KT_DIR.rglob("*.pdf"))
    kub_files = list(KUB_DIR.rglob("*.pdf"))
    
    print(f"📁 KT PDFs: {len(kt_files)}")
    print(f"📁 KUB PDFs: {len(kub_files)}")
    print(f"📁 TOPLAM: {len(kt_files) + len(kub_files)}")
    
    return kt_files, kub_files

def extract_single_pdf(pdf_path):
    """Tek PDF'i işle - multiprocessing için"""
    
    try:
        extractor = PDFTextExtractor()
        # extract_text method returns (text, method, results)
        text, method, results = extractor.extract_text(pdf_path)
        
        if text and len(text.strip()) > 50:  # En az 50 karakter
            # Dosya adından ilaç ismini çıkar
            file_name = Path(pdf_path).stem
            if '_KT' in file_name:
                drug_name = file_name.replace('_KT', '')
            elif '_KUB' in file_name:
                drug_name = file_name.replace('_KUB', '')
            else:
                drug_name = file_name
            
            return {
                'file_path': str(pdf_path),
                'drug_name': drug_name,
                'text': text,
                'text_length': len(text),
                'extraction_method': method,
                'success': True
            }
        else:
            return {
                'file_path': str(pdf_path),
                'success': False,
                'error': f'No text extracted or text too short (method: {method})'
            }
            
    except Exception as e:
        return {
            'file_path': str(pdf_path),
            'success': False,
            'error': str(e)
        }

def process_batch(pdf_files, doc_type, batch_size=100):
    """PDF'leri batch'ler halinde işle"""
    
    results = []
    total_batches = (len(pdf_files) + batch_size - 1) // batch_size
    
    print(f"🔄 {doc_type} işleniyor: {len(pdf_files)} dosya, {total_batches} batch")
    
    for i in range(0, len(pdf_files), batch_size):
        batch = pdf_files[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"📦 Batch {batch_num}/{total_batches} - {len(batch)} dosya")
        
        # Multiprocessing pool
        with mp.Pool(processes=4) as pool:
            batch_results = list(tqdm(
                pool.imap(extract_single_pdf, batch),
                total=len(batch),
                desc=f"{doc_type} Batch {batch_num}"
            ))
        
        results.extend(batch_results)
        
        # Batch sonuçlarını kaydet (memory management)
        save_batch_results(batch_results, doc_type, batch_num)
        
        # Memory temizle
        del batch_results
    
    return results

def save_batch_results(results, doc_type, batch_num):
    """Batch sonuçlarını kaydet"""
    
    batch_dir = EXTRACTED_DIR / "batches" / doc_type.lower()
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    # Başarılı extractions
    successful = [r for r in results if r['success']]
    if successful:
        batch_file = batch_dir / f"batch_{batch_num:03d}.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(successful, f, ensure_ascii=False, indent=2)
    
    # Error log
    errors = [r for r in results if not r['success']]
    if errors:
        error_file = batch_dir / f"errors_batch_{batch_num:03d}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)

def merge_batch_results(doc_type):
    """Batch sonuçlarını birleştir"""
    
    batch_dir = EXTRACTED_DIR / "batches" / doc_type.lower()
    all_results = []
    
    # Tüm batch dosyalarını oku
    for batch_file in sorted(batch_dir.glob("batch_*.json")):
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
            all_results.extend(batch_data)
    
    # Birleştirilmiş dosyayı kaydet
    output_file = EXTRACTED_DIR / f"{doc_type.lower()}_extracted_full.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    return all_results

def create_summary_report(kt_results, kub_results):
    """Özet rapor oluştur"""
    
    kt_successful = [r for r in kt_results if r['success']]
    kub_successful = [r for r in kub_results if r['success']]
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files_processed": len(kt_results) + len(kub_results),
        "kt_summary": {
            "total_files": len(kt_results),
            "successful_extractions": len(kt_successful),
            "success_rate": len(kt_successful) / len(kt_results) if kt_results else 0,
            "average_text_length": sum(r['text_length'] for r in kt_successful) / len(kt_successful) if kt_successful else 0
        },
        "kub_summary": {
            "total_files": len(kub_results),
            "successful_extractions": len(kub_successful),
            "success_rate": len(kub_successful) / len(kub_results) if kub_results else 0,
            "average_text_length": sum(r['text_length'] for r in kub_successful) / len(kub_successful) if kub_successful else 0
        },
        "overall": {
            "total_successful": len(kt_successful) + len(kub_successful),
            "overall_success_rate": (len(kt_successful) + len(kub_successful)) / (len(kt_results) + len(kub_results)),
            "total_text_extracted": sum(r['text_length'] for r in kt_successful + kub_successful)
        }
    }
    
    # Raporu kaydet
    summary_file = EXTRACTED_DIR / "extraction_summary_full.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return summary

def main():
    """Ana işleme fonksiyonu"""
    
    print("🚀 PUPILLICA - FULL SCALE PDF EXTRACTION")
    print("=" * 60)
    
    # Dizinleri oluştur
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Tüm PDF'leri listele
    kt_files, kub_files = get_all_pdfs()
    
    if not kt_files and not kub_files:
        print("❌ Hiç PDF dosyası bulunamadı!")
        return
    
    # KT dosyalarını işle
    print(f"\n📋 KT DÖKÜMANLARı İŞLENİYOR...")
    kt_results = process_batch(kt_files, "KT", batch_size=100)
    kt_merged = merge_batch_results("KT")
    
    print(f"✅ KT tamamlandı: {len([r for r in kt_results if r['success']])}/{len(kt_results)} başarılı")
    
    # KUB dosyalarını işle
    print(f"\n📋 KUB DÖKÜMANLARı İŞLENİYOR...")
    kub_results = process_batch(kub_files, "KUB", batch_size=100)
    kub_merged = merge_batch_results("KUB")
    
    print(f"✅ KUB tamamlandı: {len([r for r in kub_results if r['success']])}/{len(kub_results)} başarılı")
    
    # Özet rapor
    summary = create_summary_report(kt_results, kub_results)
    
    print(f"\n📊 ÖZET RAPOR:")
    print(f"  Toplam dosya: {summary['total_files_processed']}")
    print(f"  Başarılı extraction: {summary['overall']['total_successful']}")
    print(f"  Başarı oranı: {summary['overall']['overall_success_rate']:.1%}")
    print(f"  Toplam metin: {summary['overall']['total_text_extracted']:,} karakter")
    
    print(f"\n🎯 SONRAKİ ADIM: Vector database'e indexleme")
    
    return summary

if __name__ == "__main__":
    # Multiprocessing için gerekli
    mp.set_start_method('spawn', force=True)
    
    summary = main()