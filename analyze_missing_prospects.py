#!/usr/bin/env python3
"""
Eksik Prospektüs Analiz Script'i
Scraping işlemi bitince hangi prospektüslerin eksik olduğunu tespit eder
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import re

def analyze_missing_prospects():
    """Eksik prospektüsleri analiz et"""
    print("📊 EKSİK PROSPEKTÜS ANALİZİ BAŞLATIYOR...")
    print("=" * 60)
    
    # Progress dosyasını oku
    try:
        with open("progress.json", "r", encoding="utf-8") as f:
            progress = json.load(f)
        
        total_processed = progress.get("total_processed", 0)
        current_page = progress.get("current_page", 0)
        success_rate = progress.get("success_rate", 0)
        
        print(f"📋 İşlenen İlaç Sayısı: {total_processed:,}")
        print(f"📄 Son İşlenen Sayfa: {current_page}")
        print(f"✅ Genel Başarı Oranı: {success_rate:.1f}%")
        
    except FileNotFoundError:
        print("❌ Progress dosyası bulunamadı!")
        return
    
    # Dosya sayılarını kontrol et
    kt_dir = Path("data/kt")
    kub_dir = Path("data/kub")
    
    if not kt_dir.exists() or not kub_dir.exists():
        print("❌ Veri klasörleri bulunamadı!")
        return
    
    kt_files = list(kt_dir.glob("*.pdf"))
    kub_files = list(kub_dir.glob("*.pdf"))
    
    print(f"\n📁 DOSYA SAYILARI:")
    print(f"📄 KT Prospektüsleri: {len(kt_files):,}")
    print(f"📄 KÜB Prospektüsleri: {len(kub_files):,}")
    print(f"📊 Toplam İndirilen: {len(kt_files) + len(kub_files):,}")
    
    # Beklenen vs gerçek analizi
    expected_total = total_processed * 2  # Her ilaç için KT + KÜB
    actual_total = len(kt_files) + len(kub_files)
    missing_count = expected_total - actual_total
    
    print(f"\n🎯 EKSİK DOSYA ANALİZİ:")
    print(f"📈 Beklenen Toplam: {expected_total:,} dosya")
    print(f"📊 İndirilen Toplam: {actual_total:,} dosya")
    print(f"❌ Eksik Dosya: {missing_count:,} dosya")
    print(f"📉 Eksiklik Oranı: {(missing_count/expected_total)*100:.1f}%")
    
    # İlaç isimlerini extract et
    kt_drug_names = extract_drug_names(kt_files)
    kub_drug_names = extract_drug_names(kub_files)
    
    # Sadece KT'si olan ilaçlar
    only_kt = kt_drug_names - kub_drug_names
    # Sadece KÜB'ü olan ilaçlar  
    only_kub = kub_drug_names - kt_drug_names
    # Her ikisi de olan ilaçlar
    both_available = kt_drug_names & kub_drug_names
    
    print(f"\n🔍 PROSPEKTÜS DAĞILIMI:")
    print(f"✅ Hem KT hem KÜB: {len(both_available):,} ilaç")
    print(f"📄 Sadece KT: {len(only_kt):,} ilaç")
    print(f"📄 Sadece KÜB: {len(only_kub):,} ilaç")
    
    # Eksik prospektüs örnekleri
    if only_kt:
        print(f"\n📋 SADECE KT'Sİ OLAN İLAÇLAR (İlk 10):")
        for drug in list(only_kt)[:10]:
            print(f"   • {drug}")
        if len(only_kt) > 10:
            print(f"   ... ve {len(only_kt)-10} ilaç daha")
    
    if only_kub:
        print(f"\n📋 SADECE KÜB'Ü OLAN İLAÇLAR (İlk 10):")
        for drug in list(only_kub)[:10]:
            print(f"   • {drug}")
        if len(only_kub) > 10:
            print(f"   ... ve {len(only_kub)-10} ilaç daha")
    
    # Jüri sunumu için özet
    print(f"\n🎤 JÜRİ SUNUMU ÖZETİ:")
    print(f"=" * 40)
    print(f"📊 Toplam İşlenen İlaç: {total_processed:,}")
    print(f"📁 Toplam İndirilen PDF: {actual_total:,}")
    print(f"✅ Veri Toplama Başarısı: {(actual_total/expected_total)*100:.1f}%")
    print(f"📈 Tam Prospektüs (KT+KÜB): {len(both_available):,} ilaç")
    print(f"📄 Kısmi Prospektüs: {len(only_kt) + len(only_kub):,} ilaç")
    
    if missing_count > 0:
        remaining_pages = 1516 - current_page  # Toplam sayfa sayısı - mevcut
        print(f"\n🔄 DEVAM PLANI:")
        print(f"📄 Kalan Sayfa: ~{remaining_pages} sayfa")
        print(f"⏱️ Tahmini Süre: {remaining_pages * 0.5:.0f}-{remaining_pages * 1:.0f} saat")
        print(f"🎯 Hedef: %95+ veri toplama başarısı")
    
    # Raporu dosyaya kaydet
    save_analysis_report(progress, kt_files, kub_files, only_kt, only_kub, both_available)
    
    print(f"\n📄 Detaylı rapor 'analysis_report.json' dosyasına kaydedildi.")

def extract_drug_names(file_list):
    """PDF dosya isimlerinden ilaç isimlerini çıkar"""
    drug_names = set()
    for file_path in file_list:
        # Dosya isminden KT/KUB sonekini kaldır
        name = file_path.stem
        name = re.sub(r'_(KT|KUB)$', '', name, flags=re.IGNORECASE)
        # Türkçe karakterleri normalize et
        name = name.strip()
        if name:
            drug_names.add(name)
    return drug_names

def save_analysis_report(progress, kt_files, kub_files, only_kt, only_kub, both_available):
    """Analiz raporunu JSON dosyasına kaydet"""
    report = {
        "timestamp": progress.get("timestamp"),
        "scraping_stats": {
            "total_processed": progress.get("total_processed", 0),
            "current_page": progress.get("current_page", 0),
            "success_rate": progress.get("success_rate", 0)
        },
        "file_counts": {
            "kt_files": len(kt_files),
            "kub_files": len(kub_files),
            "total_downloaded": len(kt_files) + len(kub_files)
        },
        "prospect_distribution": {
            "both_available": len(both_available),
            "only_kt": len(only_kt),
            "only_kub": len(only_kub)
        },
        "missing_analysis": {
            "expected_total": progress.get("total_processed", 0) * 2,
            "actual_total": len(kt_files) + len(kub_files),
            "missing_count": (progress.get("total_processed", 0) * 2) - (len(kt_files) + len(kub_files)),
            "data_completeness": ((len(kt_files) + len(kub_files)) / (progress.get("total_processed", 0) * 2)) * 100
        },
        "sample_missing": {
            "only_kt_samples": list(only_kt)[:20],
            "only_kub_samples": list(only_kub)[:20]
        }
    }
    
    with open("analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    analyze_missing_prospects()