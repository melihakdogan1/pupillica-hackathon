#!/usr/bin/env python3
"""
PUPILLICA - ULTRA FAST PDF EXTRACTION
Multiprocessing ile hızlandırılmış versiyon
"""

import os
import json
from pathlib import Path
from pdf_extraction import PDFTextExtractor
from tqdm import tqdm
from datetime import datetime
import time
from multiprocessing import Pool, cpu_count

# Dizinler
DATA_DIR = Path("data")
KT_DIR = DATA_DIR / "kt"
KUB_DIR = DATA_DIR / "kub"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"

def extract_single_pdf(pdf_path):
    """Tek PDF'i işle - optimize edilmiş"""
    
    try:
        extractor = PDFTextExtractor()
        text, method, results = extractor.extract_text(pdf_path)
        
        if text and len(text.strip()) > 50:
            # İlaç ismini optimize edilmiş şekilde çıkar
            file_name = Path(pdf_path).stem
            drug_name = file_name.replace('_KT', '').replace('_KUB', '')
            
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

def process_document_type_parallel(doc_files, doc_type, batch_size=500):
    """Bir doküman tipini PARALEL olarak işle (KT veya KUB)"""
    
    print(f"🚀 {doc_type} PARALEL İŞLENİYOR - {len(doc_files)} dosya")
    
    all_results = []
    total_batches = (len(doc_files) + batch_size - 1) // batch_size
    
    # Kullanılabilir CPU çekirdeği sayısını al (veya bir eksiğini kullan)
    num_workers = max(1, cpu_count() - 1)
    print(f"⚙️ {num_workers} adet CPU çekirdeği ile çalışılıyor...")
    
    for i in range(0, len(doc_files), batch_size):
        batch = doc_files[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"📦 Batch {batch_num}/{total_batches} - {len(batch)} dosya")
        
        batch_start_time = time.time()
        
        # Paralel işlem havuzunu oluştur
        with Pool(processes=num_workers) as pool:
            # tqdm ile ilerlemeyi gösterirken, pool.imap_unordered ile verimli bir şekilde işle
            # imap_unordered, görevler tamamlandıkça sonuçları verdiği için ilerleme çubuğu anlık güncellenir
            results_iterator = pool.imap_unordered(extract_single_pdf, batch)
            
            batch_results = []
            for result in tqdm(results_iterator, total=len(batch), desc=f"{doc_type} Batch {batch_num} (PARALLEL)"):
                batch_results.append(result)

        batch_end_time = time.time()
        batch_duration = batch_end_time - batch_start_time
        
        # Batch sonuçlarını kaydet
        save_batch_results(batch_results, doc_type, batch_num, parallel=True)
        all_results.extend(batch_results)
        
        # İstatistik göster
        successful = len([r for r in batch_results if r['success']])
        files_per_second = len(batch_results) / batch_duration
        print(f"  ✅ Batch {batch_num}: {successful}/{len(batch_results)} başarılı")
        print(f"  ⚡ Hız: {files_per_second:.1f} dosya/saniye, Süre: {batch_duration:.1f}s")
        
        # Memory temizle
        del batch_results
    
    return all_results

def save_batch_results(results, doc_type, batch_num, parallel=False):
    """Batch sonuçlarını kaydet"""
    
    batch_type = "parallel" if parallel else "serial"
    batch_dir = EXTRACTED_DIR / f"{batch_type}_batches" / doc_type.lower()
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

def merge_all_results(doc_type, parallel=False):
    """Tüm batch sonuçlarını birleştir"""
    
    batch_type = "parallel" if parallel else "serial"
    batch_dir = EXTRACTED_DIR / f"{batch_type}_batches" / doc_type.lower()
    all_results = []
    
    # Tüm batch dosyalarını oku
    for batch_file in sorted(batch_dir.glob("batch_*.json")):
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
            all_results.extend(batch_data)
    
    # Birleştirilmiş dosyayı kaydet
    output_file = EXTRACTED_DIR / f"{doc_type.lower()}_extracted_{batch_type}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 {doc_type} birleştirilmiş ({batch_type}): {len(all_results)} başarılı extraction")
    return all_results

def create_summary_report(kt_results, kub_results, processing_time, parallel=False):
    """Özet rapor oluştur"""
    
    batch_type = "parallel" if parallel else "serial"
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "processing_type": batch_type,
        "processing_time_minutes": round(processing_time / 60, 2),
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
    
    total_files = len(kt_results) + len(kub_results)
    files_per_second = total_files / processing_time if processing_time > 0 else 0
    
    summary["overall"] = {
        "total_successful": len(kt_successful) + len(kub_successful),
        "overall_success_rate": (len(kt_successful) + len(kub_successful)) / (len(kt_results) + len(kub_results)),
        "total_text_extracted": sum(r.get('text_length', 0) for r in kt_successful + kub_successful),
        "files_per_second": round(files_per_second, 2),
        "estimated_chunks": (len(kt_successful) + len(kub_successful)) * 40  # ~40 chunk per PDF
    }
    
    # Raporu kaydet
    summary_file = EXTRACTED_DIR / f"extraction_summary_{batch_type}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return summary

def main():
    """Ana işleme fonksiyonu - ULTRA FAST VERSION"""
    
    print("🚀 PUPILLICA - ULTRA FAST PDF EXTRACTION (MULTIPROCESSING)")
    print("=" * 80)
    
    start_time = time.time()
    
    # Dizinleri oluştur
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    
    # CPU bilgisi
    cpu_cores = cpu_count()
    workers = max(1, cpu_cores - 1)
    print(f"💻 Sistem: {cpu_cores} CPU çekirdeği, {workers} worker kullanılacak")
    
    # Tüm PDF'leri listele
    kt_files = list(KT_DIR.rglob("*.pdf"))
    kub_files = list(KUB_DIR.rglob("*.pdf"))
    
    print(f"📁 KT PDFs: {len(kt_files)}")
    print(f"📁 KUB PDFs: {len(kub_files)}")
    print(f"📁 TOPLAM: {len(kt_files) + len(kub_files)}")
    
    if not kt_files and not kub_files:
        print("❌ Hiç PDF dosyası bulunamadı!")
        return
    
    # Hız tahmini
    estimated_files_per_second = workers * 1.5  # Tahmini hız
    estimated_time_minutes = (len(kt_files) + len(kub_files)) / (estimated_files_per_second * 60)
    print(f"⏱️ Tahmini süre: {estimated_time_minutes:.1f} dakika (vs seri: {(len(kt_files) + len(kub_files)) / 90:.1f} dakika)")
    
    # KT dosyalarını paralel işle
    print(f"\n" + "="*60)
    kt_results = process_document_type_parallel(kt_files, "KT")
    kt_merged = merge_all_results("KT", parallel=True)
    
    # KUB dosyalarını paralel işle
    print(f"\n" + "="*60)
    kub_results = process_document_type_parallel(kub_files, "KUB")
    kub_merged = merge_all_results("KUB", parallel=True)
    
    # Özet rapor
    print(f"\n" + "="*60)
    end_time = time.time()
    processing_time = end_time - start_time
    summary = create_summary_report(kt_results, kub_results, processing_time, parallel=True)
    
    print(f"\n🎯 ULTRA FAST ÖZET:")
    print(f"  Toplam dosya: {summary['total_files_processed']}")
    print(f"  KT başarılı: {summary['kt_summary']['successful_extractions']}/{summary['kt_summary']['total_files']} ({summary['kt_summary']['success_rate']:.1%})")
    print(f"  KUB başarılı: {summary['kub_summary']['successful_extractions']}/{summary['kub_summary']['total_files']} ({summary['kub_summary']['success_rate']:.1%})")
    print(f"  Toplam başarılı: {summary['overall']['total_successful']}")
    print(f"  Genel başarı oranı: {summary['overall']['overall_success_rate']:.1%}")
    print(f"  Toplam metin: {summary['overall']['total_text_extracted']:,} karakter")
    print(f"  ⚡ İşlem süresi: {processing_time/60:.1f} dakika")
    print(f"  ⚡ Hız: {summary['overall']['files_per_second']:.1f} dosya/saniye")
    print(f"  📊 Tahmini chunk: ~{summary['overall']['estimated_chunks']:,}")
    
    # Hız karşılaştırması
    serial_estimated_time = len(kt_files + kub_files) / 90  # 90 dosya/dakika seri
    speedup = serial_estimated_time / (processing_time / 60)
    print(f"\n🔥 HIZ KAZANCI:")
    print(f"  Seri işlem tahmini: {serial_estimated_time:.1f} dakika")
    print(f"  Paralel gerçek: {processing_time/60:.1f} dakika")
    print(f"  Hızlanma: {speedup:.1f}x daha hızlı!")
    
    print(f"\n🎯 SONRAKİ ADIM: Vector database'e indexleme")
    
    return summary

if __name__ == "__main__":
    # Windows için multiprocessing fix
    if os.name == 'nt':
        # Windows'ta multiprocessing için gerekli
        pass
    
    summary = main()