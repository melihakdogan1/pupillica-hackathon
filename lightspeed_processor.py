#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ LİGHT SPEED PDF PROCESSOR ⚡
Sadece PyPDF2 ve PDFPlumber ile hızlı processing
"""

import os
import sys
import time
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import json
import hashlib
from typing import List, Dict, Optional

# Lightweight PDF libraries
try:
    import PyPDF2
    import pdfplumber
except ImportError as e:
    print(f"❌ Eksik kütüphane: {e}")
    print("📦 Kurulum: pip install PyPDF2 pdfplumber")
    sys.exit(1)

# Simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_single_pdf(pdf_path_str: str) -> Optional[Dict]:
    """Single PDF extract function for multiprocessing"""
    try:
        pdf_path = Path(pdf_path_str)
        
        if not pdf_path.exists():
            return None
            
        # Hash hesaplama
        with open(pdf_path, 'rb') as f:
            chunk = f.read(8192)
            file_hash = hashlib.md5(chunk).hexdigest()
        
        text_content = ""
        metadata = {
            "file_name": pdf_path.name,
            "file_path": str(pdf_path),
            "file_size": pdf_path.stat().st_size,
            "file_hash": file_hash,
            "source_type": "kt" if "/kt/" in str(pdf_path) else "kub"
        }
        
        # PDFPlumber ile text extraction
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_count = min(len(pdf.pages), 30)  # İlk 30 sayfa
                for page_num in range(page_count):
                    try:
                        page_text = pdf.pages[page_num].extract_text()
                        if page_text and len(page_text.strip()) > 20:
                            text_content += f"\\n\\n--- Sayfa {page_num + 1} ---\\n{page_text.strip()}"
                    except:
                        continue
                        
            metadata["extraction_method"] = "pdfplumber"
            metadata["pages_processed"] = page_count
            
        except Exception as e:
            # PyPDF2 fallback
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = min(len(pdf_reader.pages), 30)
                    for page_num in range(page_count):
                        try:
                            page_text = pdf_reader.pages[page_num].extract_text()
                            if page_text and len(page_text.strip()) > 20:
                                text_content += f"\\n\\n--- Sayfa {page_num + 1} ---\\n{page_text.strip()}"
                        except:
                            continue
                            
                metadata["extraction_method"] = "PyPDF2"
                metadata["pages_processed"] = page_count
                
            except Exception as e2:
                return None
        
        # Text quality check
        text_content = text_content.strip()
        if len(text_content) < 100:
            return None
            
        metadata["text_length"] = len(text_content)
        metadata["extraction_time"] = time.time()
        
        return {
            "text": text_content,
            "metadata": metadata
        }
        
    except Exception as e:
        return None

class LightSpeedProcessor:
    def __init__(self):
        self.base_dir = Path("C:/pupillicaHackathon")
        self.kt_dir = self.base_dir / "data/kt"
        self.kub_dir = self.base_dir / "data/kub"
        self.output_dir = self.base_dir / "data/processed/extracted"
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.start_time = time.time()
        self.processed_count = 0
        self.failed_count = 0
        
    def get_pdf_list(self) -> List[str]:
        """Get all PDF file paths"""
        pdf_files = []
        
        # KT PDFs
        if self.kt_dir.exists():
            kt_files = [str(f) for f in self.kt_dir.glob("*.pdf")]
            pdf_files.extend(kt_files)
            print(f"📁 KT: {len(kt_files)} PDFs")
        
        # KUB PDFs
        if self.kub_dir.exists():
            kub_files = [str(f) for f in self.kub_dir.glob("*.pdf")]
            pdf_files.extend(kub_files)
            print(f"📁 KUB: {len(kub_files)} PDFs")
            
        print(f"🎯 Total: {len(pdf_files)} PDFs found")
        return pdf_files
    
    def process_batch(self, pdf_files: List[str], max_workers: int = None) -> List[Dict]:
        """Process PDF files in parallel"""
        if max_workers is None:
            max_workers = min(cpu_count(), 6)  # Max 6 workers
            
        print(f"🚀 Starting {max_workers} parallel workers...")
        
        results = []
        total_files = len(pdf_files)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(extract_single_pdf, pdf_file): pdf_file 
                for pdf_file in pdf_files
            }
            
            # Process results
            for i, future in enumerate(as_completed(future_to_file)):
                pdf_file = future_to_file[future]
                
                try:
                    result = future.result(timeout=60)  # 1 minute timeout
                    if result:
                        results.append(result)
                        self.processed_count += 1
                        
                        # Save immediately to prevent loss
                        output_file = self.output_dir / f"doc_{self.processed_count:06d}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                            
                    else:
                        self.failed_count += 1
                        
                except Exception as e:
                    self.failed_count += 1
                    print(f"❌ Error processing {Path(pdf_file).name}: {e}")
                
                # Progress report every 100 files
                completed = self.processed_count + self.failed_count
                if completed % 100 == 0 or completed == total_files:
                    elapsed = time.time() - self.start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (total_files - completed) / rate if rate > 0 else 0
                    
                    print(f"⚡ Progress: {completed}/{total_files} "
                          f"({completed/total_files*100:.1f}%) - "
                          f"Success: {self.processed_count} - "
                          f"Rate: {rate:.1f} files/sec - "
                          f"ETA: {eta/60:.1f} min")
        
        return results
    
    def run_processing(self):
        """Main processing function"""
        print("🚀 LIGHT SPEED PDF PROCESSING STARTING!")
        print(f"🕐 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get PDF files
        pdf_files = self.get_pdf_list()
        if not pdf_files:
            print("❌ No PDF files found!")
            return False
        
        # Process files
        results = self.process_batch(pdf_files)
        
        # Final results
        elapsed = time.time() - self.start_time
        total_files = len(pdf_files)
        success_rate = (self.processed_count / total_files) * 100 if total_files > 0 else 0
        
        print(f"")
        print(f"🎯 PROCESSING COMPLETED!")
        print(f"📊 Total files: {total_files}")
        print(f"✅ Successful: {self.processed_count} ({success_rate:.1f}%)")
        print(f"❌ Failed: {self.failed_count}")
        print(f"⏱️ Total time: {elapsed/60:.1f} minutes")
        print(f"⚡ Average rate: {total_files/elapsed:.1f} files/second")
        
        # Count output files
        output_files = list(self.output_dir.glob("*.json"))
        print(f"💾 Output files created: {len(output_files)}")
        
        return self.processed_count > 0

if __name__ == "__main__":
    print("⚡ LIGHT SPEED PDF PROCESSOR ⚡")
    processor = LightSpeedProcessor()
    success = processor.run_processing()
    
    if success:
        print("🎉 Ready for ChromaDB loading!")
    else:
        print("❌ Processing failed!")
        sys.exit(1)