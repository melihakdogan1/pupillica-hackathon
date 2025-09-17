#!/usr/bin/env python3
"""
Test single PDF extraction
"""

from pathlib import Path
from pdf_extraction import PDFTextExtractor
import os

def test_single_extraction():
    """Tek PDF ile test"""
    
    # KT klasöründen bir PDF al
    kt_files = list(Path("data/kt").rglob("*.pdf"))
    if not kt_files:
        print("❌ KT PDF bulunamadı!")
        return
    
    test_file = kt_files[0]
    print(f"🧪 Test dosyası: {test_file.name}")
    
    try:
        extractor = PDFTextExtractor()
        text, method, results = extractor.extract_text(test_file)
        
        print(f"✅ Extraction başarılı:")
        print(f"  Method: {method}")
        print(f"  Text length: {len(text) if text else 0}")
        print(f"  Results: {len(results)} methods tried")
        
        if text:
            print(f"  İlk 200 karakter: {text[:200]}...")
            return True
        else:
            print("❌ Metin çıkarılamadı")
            print(f"  Results: {results}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_single_extraction()