#!/usr/bin/env python3
"""
PUPILLICA - FULL SCALE PDF EXTRACTION (Optimized)
Tüm 5,275 PDF'i işleyip text extraction yapmak (seri processing)
"""

import os
import json
from pathlib import Path
from pdf_extraction import PDFTextExtractor
from tqdm import tqdm
from datetime import datetime
import time

# Dizinler
DATA_DIR = Path("data")
KT_DIR = DATA_DIR / "kt"
KUB_DIR = DATA_DIR / "kub"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"

def extract_single_pdf(pdf_path):
    """Tek PDF'i işle"""
    
    try:
        extractor = PDFTextExtractor()
        text, method, results = extractor.extract_text(pdf_path)
        
        if text and len(text.strip()) > 50:
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

def process_document_type(doc_files, doc_type, batch_size=500):
    """Bir doküman tipini işle (KT veya KUB)"""
    
    print(f"🔄 {doc_type} İŞLENİYOR - {len(doc_files)} dosya")
    
    all_results = []
    total_batches = (len(doc_files) + batch_size - 1) // batch_size
    
    for i in range(0, len(doc_files), batch_size):
        batch = doc_files[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"📦 Batch {batch_num}/{total_batches} - {len(batch)} dosya")
        
        batch_results = []
        
        # Batch'i işle
        for pdf_file in tqdm(batch, desc=f"{doc_type} Batch {batch_num}"):
            result = extract_single_pdf(pdf_file)
            batch_results.append(result)
        
        # Batch sonuçlarını kaydet
        save_batch_results(batch_results, doc_type, batch_num)
        all_results.extend(batch_results)
        
        # İstatistik göster
        successful = len([r for r in batch_results if r['success']])
        print(f"  ✅ Batch {batch_num}: {successful}/{len(batch_results)} başarılı")
        
        # Memory temizle
        del batch_results
    
    return all_results

def save_batch_results(results, doc_type, batch_num):
    """Batch sonuçlarını kaydet"""
    
    batch_dir = EXTRACTED_DIR / "full_batches" / doc_type.lower()
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

def merge_all_results(doc_type):
    """Tüm batch sonuçlarını birleştir"""
    
    batch_dir = EXTRACTED_DIR / "full_batches" / doc_type.lower()
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
    
    print(f"💾 {doc_type} birleştirilmiş: {len(all_results)} başarılı extraction")
    return all_results

def create_summary_report(kt_results, kub_results):
    """Özet rapor oluştur"""
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files_processed": len(kt_results) + len(kub_results),
        "kt_summary": {
            "total_files": len(kt_results),
            "successful_extractions": len([r for r in kt_results if r.get('success', False)]),
            "success_rate": len([r for r in kt_results if r.get('success', False)]) / len(kt_results) if kt_results else 0,
            "average_text_length": sum(r.get('text_length', 0) for r in kt_results if r.get('success', False)) / len([r for r in kt_results if r.get('success', False)]) if [r for r in kt_results if r.get('success', False)] else 0
        },
        "kub_summary": {
            "total_files": len(kub_results),
            "successful_extractions": len([r for r in kub_results if r.get('success', False)]),
            "success_rate": len([r for r in kub_results if r.get('success', False)]) / len(kub_results) if kub_results else 0,
            "average_text_length": sum(r.get('text_length', 0) for r in kub_results if r.get('success', False)) / len([r for r in kub_results if r.get('success', False)]) if [r for r in kub_results if r.get('success', False)] else 0
        }
    }
    
    kt_successful = [r for r in kt_results if r.get('success', False)]
    kub_successful = [r for r in kub_results if r.get('success', False)]
    
    summary["overall"] = {
        "total_successful": len(kt_successful) + len(kub_successful),
        "overall_success_rate": (len(kt_successful) + len(kub_successful)) / (len(kt_results) + len(kub_results)),
        "total_text_extracted": sum(r.get('text_length', 0) for r in kt_successful + kub_successful)
    }
    
    # Raporu kaydet
    summary_file = EXTRACTED_DIR / "extraction_summary_full.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return summary

def main():
    """Ana işleme fonksiyonu"""
    
    print("🚀 PUPILLICA - FULL SCALE PDF EXTRACTION (OPTIMIZED)")
    print("=" * 70)
    
    start_time = time.time()
    
    # Dizinleri oluştur
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Tüm PDF'leri listele
    kt_files = list(KT_DIR.rglob("*.pdf"))
    kub_files = list(KUB_DIR.rglob("*.pdf"))
    
    print(f"📁 KT PDFs: {len(kt_files)}")
    print(f"📁 KUB PDFs: {len(kub_files)}")
    print(f"📁 TOPLAM: {len(kt_files) + len(kub_files)}")
    
    if not kt_files and not kub_files:
        print("❌ Hiç PDF dosyası bulunamadı!")
        return
    
    # KT dosyalarını işle
    print(f"\n" + "="*50)
    kt_results = process_document_type(kt_files, "KT")
    kt_merged = merge_all_results("KT")
    
    # KUB dosyalarını işle
    print(f"\n" + "="*50)
    kub_results = process_document_type(kub_files, "KUB")
    kub_merged = merge_all_results("KUB")
    
    # Özet rapor
    print(f"\n" + "="*50)
    summary = create_summary_report(kt_results, kub_results)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n📊 FINAL ÖZET:")
    print(f"  Toplam dosya: {summary['total_files_processed']}")
    print(f"  KT başarılı: {summary['kt_summary']['successful_extractions']}/{summary['kt_summary']['total_files']} ({summary['kt_summary']['success_rate']:.1%})")
    print(f"  KUB başarılı: {summary['kub_summary']['successful_extractions']}/{summary['kub_summary']['total_files']} ({summary['kub_summary']['success_rate']:.1%})")
    print(f"  Toplam başarılı: {summary['overall']['total_successful']}")
    print(f"  Genel başarı oranı: {summary['overall']['overall_success_rate']:.1%}")
    print(f"  Toplam metin: {summary['overall']['total_text_extracted']:,} karakter")
    print(f"  İşlem süresi: {processing_time/60:.1f} dakika")
    
    print(f"\n🎯 SONRAKİ ADIM: Vector database'e indexleme")
    print(f"  Tahmini chunk sayısı: ~{summary['overall']['total_successful'] * 40:,}")
    
    return summary

if __name__ == "__main__":
    summary = main()