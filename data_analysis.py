#!/usr/bin/env python3
"""
PUPILLICA - Veri Analizi ve Temizleme
Amaç: 2,651 ilaç prospektüsünü (KT+KUB) analiz etmek
"""

import os
import pandas as pd
from pathlib import Path
import hashlib
from collections import defaultdict
import re
from datetime import datetime
import json

# Dizinler
DATA_DIR = Path("data")
KT_DIR = DATA_DIR / "kt"
KUB_DIR = DATA_DIR / "kub"
ANALYSIS_DIR = DATA_DIR / "analysis"

def analyze_file_structure():
    """Dosya yapısını analiz et"""
    print("📊 Dosya Yapısı Analizi")
    print("=" * 50)
    
    # KT dosyaları
    kt_files = list(KT_DIR.glob("*.pdf"))
    kub_files = list(KUB_DIR.glob("*.pdf"))
    
    print(f"KT (Prospektüs) dosyaları: {len(kt_files)}")
    print(f"KUB (Doktor bilgisi) dosyaları: {len(kub_files)}")
    
    # Dosya boyutları
    kt_sizes = [f.stat().st_size for f in kt_files]
    kub_sizes = [f.stat().st_size for f in kub_files]
    
    print(f"\nKT dosya boyutları:")
    print(f"  Ortalama: {sum(kt_sizes)/len(kt_sizes):.0f} bytes")
    print(f"  Min: {min(kt_sizes)} bytes")
    print(f"  Max: {max(kt_sizes)} bytes")
    
    print(f"\nKUB dosya boyutları:")
    print(f"  Ortalama: {sum(kub_sizes)/len(kub_sizes):.0f} bytes")
    print(f"  Min: {min(kub_sizes)} bytes")
    print(f"  Max: {max(kub_sizes)} bytes")
    
    return kt_files, kub_files

def extract_drug_names(files):
    """Dosya adlarından ilaç isimlerini çıkar"""
    drug_names = []
    
    for file_path in files:
        # Dosya adından _KT.pdf veya _KUB.pdf kısmını çıkar
        name = file_path.stem
        if name.endswith('_KT'):
            drug_name = name[:-3]
        elif name.endswith('_KUB'):
            drug_name = name[:-4]
        else:
            drug_name = name
        
        drug_names.append(drug_name)
    
    return drug_names

def find_matched_pairs():
    """KT ve KUB dosyalarının eşleşen çiftlerini bul"""
    print("\n🔍 KT-KUB Eşleştirme Analizi")
    print("=" * 50)
    
    kt_files = list(KT_DIR.glob("*.pdf"))
    kub_files = list(KUB_DIR.glob("*.pdf"))
    
    kt_drugs = {extract_drug_names([f])[0]: f for f in kt_files}
    kub_drugs = {extract_drug_names([f])[0]: f for f in kub_files}
    
    # Eşleşen çiftler
    matched_pairs = []
    kt_only = []
    kub_only = []
    
    all_drugs = set(kt_drugs.keys()) | set(kub_drugs.keys())
    
    for drug in all_drugs:
        if drug in kt_drugs and drug in kub_drugs:
            matched_pairs.append({
                'drug_name': drug,
                'kt_file': kt_drugs[drug],
                'kub_file': kub_drugs[drug]
            })
        elif drug in kt_drugs:
            kt_only.append(drug)
        else:
            kub_only.append(drug)
    
    print(f"✅ Tam eşleşen çiftler: {len(matched_pairs)}")
    print(f"⚠️ Sadece KT olanlar: {len(kt_only)}")
    print(f"⚠️ Sadece KUB olanlar: {len(kub_only)}")
    
    if kt_only[:5]:
        print(f"KT-only örnekler: {kt_only[:5]}")
    if kub_only[:5]:
        print(f"KUB-only örnekler: {kub_only[:5]}")
    
    return matched_pairs, kt_only, kub_only

def analyze_drug_names():
    """İlaç isimlerini analiz et"""
    print("\n💊 İlaç İsimleri Analizi")
    print("=" * 50)
    
    kt_files = list(KT_DIR.glob("*.pdf"))
    drug_names = extract_drug_names(kt_files)
    
    # İsim uzunlukları
    name_lengths = [len(name) for name in drug_names]
    print(f"İsim uzunlukları:")
    print(f"  Ortalama: {sum(name_lengths)/len(name_lengths):.1f} karakter")
    print(f"  En kısa: {min(name_lengths)} ({[n for n in drug_names if len(n) == min(name_lengths)][0]})")
    print(f"  En uzun: {max(name_lengths)} ({[n for n in drug_names if len(n) == max(name_lengths)][0]})")
    
    # Yaygın kelimeler
    word_freq = defaultdict(int)
    for name in drug_names:
        words = re.split(r'[,\s]+', name.upper())
        for word in words:
            if len(word) > 2:  # 3+ karakter olan kelimeler
                word_freq[word] += 1
    
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nEn yaygın kelimeler:")
    for word, freq in top_words:
        print(f"  {word}: {freq} kez")
    
    return drug_names, word_freq

def detect_duplicates():
    """Potansiyel duplicate dosyaları tespit et"""
    print("\n🔄 Duplicate Tespiti")
    print("=" * 50)
    
    kt_files = list(KT_DIR.glob("*.pdf"))
    kub_files = list(KUB_DIR.glob("*.pdf"))
    
    # Dosya boyutuna göre gruplama
    size_groups = defaultdict(list)
    
    for file_path in kt_files + kub_files:
        size = file_path.stat().st_size
        size_groups[size].append(file_path)
    
    duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
    
    print(f"Aynı boyutta olan dosya grupları: {len(duplicates)}")
    
    for size, files in list(duplicates.items())[:5]:  # İlk 5 grup
        print(f"  Boyut {size}: {[f.name for f in files]}")
    
    return duplicates

def generate_summary_report():
    """Özet rapor oluştur"""
    print("\n📋 ÖZET RAPOR OLUŞTURULUYOR...")
    
    # Analiz sonuçları
    kt_files, kub_files = analyze_file_structure()
    matched_pairs, kt_only, kub_only = find_matched_pairs()
    drug_names, word_freq = analyze_drug_names()
    duplicates = detect_duplicates()
    
    # Rapor
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_kt_files': len(kt_files),
            'total_kub_files': len(kub_files),
            'matched_pairs': len(matched_pairs),
            'kt_only': len(kt_only),
            'kub_only': len(kub_only),
            'unique_drugs': len(set(drug_names)),
            'potential_duplicates': len(duplicates)
        },
        'top_drug_words': dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]),
        'sample_matched_pairs': [p['drug_name'] for p in matched_pairs[:10]],
        'sample_kt_only': kt_only[:10],
        'sample_kub_only': kub_only[:10]
    }
    
    # Raporu kaydet
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    report_file = ANALYSIS_DIR / "data_analysis_report.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Rapor kaydedildi: {report_file}")
    
    # Konsol özeti
    print(f"\n🎯 ÖZETİ:")
    print(f"  📁 Toplam KT dosyaları: {report['summary']['total_kt_files']}")
    print(f"  📁 Toplam KUB dosyaları: {report['summary']['total_kub_files']}")
    print(f"  🔗 Tam eşleşen çiftler: {report['summary']['matched_pairs']}")
    print(f"  💊 Benzersiz ilaç sayısı: {report['summary']['unique_drugs']}")
    print(f"  ⚠️ Potansiyel duplikatlar: {report['summary']['potential_duplicates']}")
    
    return report

def main():
    """Ana fonksiyon"""
    print("🚀 PUPILLICA VERİ ANALİZİ BAŞLIYOR...")
    print("=" * 60)
    
    try:
        report = generate_summary_report()
        
        print(f"\n✅ ANALİZ TAMAMLANDI!")
        print(f"📊 Sonuç: {report['summary']['matched_pairs']} ilaç için hem KT hem KUB mevcut")
        print(f"🎯 Sonraki adım: PDF text extraction için hazırız!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()