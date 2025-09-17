#!/usr/bin/env python3
"""
PUPILLICA - Test Batch Extraction
Küçük batch ile test etme
"""

import os
import json
from pathlib import Path
from pdf_extraction import PDFTextExtractor
from tqdm import tqdm
import multiprocessing as mp
from datetime import datetime

# Dizinler
DATA_DIR = Path("data")
KT_DIR = DATA_DIR / "kt"
KUB_DIR = DATA_DIR / "kub"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"

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

def test_small_batch():
    """Küçük batch test et"""
    
    print("🧪 KÜÇÜK BATCH TEST")
    print("=" * 40)
    
    # 10 KT + 10 KUB dosyası al
    kt_files = list(KT_DIR.rglob("*.pdf"))[:10]
    kub_files = list(KUB_DIR.rglob("*.pdf"))[:10]
    
    print(f"📁 Test dosyaları: {len(kt_files)} KT + {len(kub_files)} KUB")
    
    all_files = kt_files + kub_files
    
    # Seri işlem (debugging için)
    print("\n🔄 Seri işlem test...")
    results = []
    for pdf_file in tqdm(all_files, desc="Processing"):
        result = extract_single_pdf(pdf_file)
        results.append(result)
    
    # Sonuçları analiz et
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n📊 SONUÇLAR:")
    print(f"  Toplam: {len(results)}")
    print(f"  Başarılı: {len(successful)}")
    print(f"  Başarısız: {len(failed)}")
    print(f"  Başarı oranı: {len(successful)/len(results)*100:.1f}%")
    
    if successful:
        avg_length = sum(r['text_length'] for r in successful) / len(successful)
        print(f"  Ortalama metin uzunluğu: {avg_length:.0f} karakter")
        
        # Method distribution
        methods = {}
        for r in successful:
            method = r['extraction_method']
            methods[method] = methods.get(method, 0) + 1
        print(f"  Method dağılımı: {methods}")
    
    if failed:
        print(f"\n❌ HATALAR:")
        error_types = {}
        for r in failed:
            error = r['error']
            error_types[error] = error_types.get(error, 0) + 1
        for error, count in error_types.items():
            print(f"  {error}: {count} dosya")
    
    # Başarılı sonuçları kaydet
    if successful:
        test_dir = EXTRACTED_DIR / "test_batch"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        with open(test_dir / "successful.json", 'w', encoding='utf-8') as f:
            json.dump(successful, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Başarılı sonuçlar kaydedildi: {test_dir / 'successful.json'}")
    
    return len(successful) > 0

if __name__ == "__main__":
    success = test_small_batch()