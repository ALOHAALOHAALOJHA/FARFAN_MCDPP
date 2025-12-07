#!/usr/bin/env python3
"""Generate PDF documentation from all Python files using enscript + ps2pdf.

Splits files into 30 organized PDFs for code audit.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List

# Configuration
REPO_ROOT = Path(__file__).parent
OUTPUT_DIR = REPO_ROOT / "code_audit_pdfs"
NUM_PDFS = 30
EXCLUDE_DIRS = {"farfan-env", "__pycache__", ".git", "node_modules", ".venv", "venv"}

def collect_python_files() -> List[Path]:
    """Collect all Python files in the repository."""
    python_files = []
    
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return sorted(python_files)

def split_into_batches(files: List[Path], num_batches: int) -> List[List[Path]]:
    """Split files into approximately equal batches."""
    batch_size = len(files) // num_batches + 1
    batches = []
    
    for i in range(0, len(files), batch_size):
        batches.append(files[i:i + batch_size])
    
    return batches

def create_combined_file(batch: List[Path], batch_num: int) -> Path:
    """Create a combined text file for a batch."""
    temp_file = OUTPUT_DIR / f"batch_{batch_num:02d}_combined.txt"
    
    with open(temp_file, 'w', encoding='utf-8') as out:
        out.write("=" * 80 + "\n")
        out.write(f"F.A.R.F.A.N PIPELINE CODE AUDIT - BATCH {batch_num}\n")
        out.write("=" * 80 + "\n")
        out.write(f"Generated: {datetime.utcnow().isoformat()}\n")
        out.write(f"Files in this batch: {len(batch)}\n")
        out.write("=" * 80 + "\n\n")
        
        for file_path in batch:
            try:
                relative = file_path.relative_to(REPO_ROOT)
            except ValueError:
                relative = file_path
            
            out.write("\n" + "=" * 80 + "\n")
            out.write(f"FILE: {relative}\n")
            out.write("=" * 80 + "\n\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
                    out.write(src.read())
            except Exception as e:
                out.write(f"# ERROR READING FILE: {e}\n")
            
            out.write("\n\n")
    
    return temp_file

def convert_to_pdf(txt_path: Path, batch_num: int) -> Path:
    """Convert text file to PDF using enscript + ps2pdf."""
    pdf_path = OUTPUT_DIR / f"FARFAN_Code_Batch_{batch_num:02d}.pdf"
    ps_path = OUTPUT_DIR / f"batch_{batch_num:02d}.ps"
    
    try:
        # Convert to PostScript using enscript
        enscript_cmd = [
            'enscript',
            '--font=Courier8',
            '--line-numbers',
            '--columns=1',
            '--fancy-header',
            '--landscape',
            '--output', str(ps_path),
            str(txt_path)
        ]
        
        result = subprocess.run(enscript_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ✗ enscript failed: {result.stderr}")
            return None
        
        # Convert PostScript to PDF
        ps2pdf_cmd = ['ps2pdf', str(ps_path), str(pdf_path)]
        result = subprocess.run(ps2pdf_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ✗ ps2pdf failed: {result.stderr}")
            return None
        
        # Clean up temporary files
        ps_path.unlink()
        txt_path.unlink()
        
        return pdf_path
    
    except Exception as e:
        print(f"  ✗ Conversion failed: {e}")
        return None

def main():
    print("=" * 80)
    print("F.A.R.F.A.N CODE AUDIT PDF GENERATOR")
    print("=" * 80)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"✓ Output directory: {OUTPUT_DIR}")
    print()
    
    # Collect files
    print("Collecting Python files...")
    all_files = collect_python_files()
    print(f"✓ Found {len(all_files)} Python files")
    print()
    
    # Split into batches
    print(f"Splitting into {NUM_PDFS} batches...")
    batches = split_into_batches(all_files, NUM_PDFS)
    actual_batches = len(batches)
    print(f"✓ Created {actual_batches} batches")
    
    files_per_batch = [len(b) for b in batches]
    print(f"  Files per batch: min={min(files_per_batch)}, max={max(files_per_batch)}, avg={sum(files_per_batch)//len(files_per_batch)}")
    print()
    
    # Generate PDFs
    print("Generating PDFs...")
    print("(This will take several minutes...)")
    print()
    
    successful = 0
    failed = 0
    
    for i, batch in enumerate(batches, 1):
        print(f"[{i:02d}/{actual_batches:02d}] Processing {len(batch)} files...", end=' ', flush=True)
        
        # Create combined text file
        txt_path = create_combined_file(batch, i)
        
        # Convert to PDF
        pdf_path = convert_to_pdf(txt_path, i)
        
        if pdf_path:
            file_size = pdf_path.stat().st_size / (1024 * 1024)
            print(f"✓ {pdf_path.name} ({file_size:.1f} MB)")
            successful += 1
        else:
            print(f"✗ Failed")
            failed += 1
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Python files: {len(all_files)}")
    print(f"Batches created: {actual_batches}")
    print(f"PDFs generated: {successful}")
    print(f"Failed: {failed}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print()
    
    if successful > 0:
        print("✓ PDF generation complete!")
        print("\nGenerated files:")
        for pdf in sorted(OUTPUT_DIR.glob("FARFAN_Code_Batch_*.pdf")):
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"  - {pdf.name} ({size_mb:.1f} MB)")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    exit(main())
