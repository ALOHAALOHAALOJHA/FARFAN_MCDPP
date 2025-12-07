#!/usr/bin/env python3
"""Generate PDF documentation from all Python files in the repository.

Splits files into 30 organized PDFs for code audit.
"""

import os
import subprocess
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
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return sorted(python_files)

def organize_files_by_directory(files: List[Path]) -> dict[str, List[Path]]:
    """Organize files by their top-level directory."""
    organized = {}
    
    for file in files:
        try:
            relative = file.relative_to(REPO_ROOT)
            top_level = str(relative.parts[0]) if len(relative.parts) > 1 else "root"
        except ValueError:
            top_level = "other"
        
        if top_level not in organized:
            organized[top_level] = []
        organized[top_level].append(file)
    
    return organized

def split_into_batches(organized: dict[str, List[Path]], num_batches: int) -> List[List[Path]]:
    """Split files into approximately equal batches."""
    all_files = []
    for files in organized.values():
        all_files.extend(files)
    
    batch_size = len(all_files) // num_batches + 1
    batches = []
    
    for i in range(0, len(all_files), batch_size):
        batches.append(all_files[i:i + batch_size])
    
    return batches

def create_markdown_for_batch(batch: List[Path], batch_num: int) -> Path:
    """Create a markdown file for a batch of Python files."""
    md_path = OUTPUT_DIR / f"batch_{batch_num:02d}.md"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# F.A.R.F.A.N Pipeline Code Audit - Batch {batch_num}\n\n")
        f.write(f"**Generated**: {datetime.utcnow().isoformat()}\n\n")
        f.write(f"**Files in this batch**: {len(batch)}\n\n")
        f.write("---\n\n")
        
        for file_path in batch:
            try:
                relative = file_path.relative_to(REPO_ROOT)
            except ValueError:
                relative = file_path
            
            f.write(f"## File: `{relative}`\n\n")
            f.write("```python\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
                    content = src.read()
                    f.write(content)
            except Exception as e:
                f.write(f"# ERROR READING FILE: {e}\n")
            
            f.write("\n```\n\n")
            f.write("---\n\n")
    
    return md_path

def convert_markdown_to_pdf(md_path: Path) -> Path:
    """Convert markdown to PDF using pandoc."""
    pdf_path = md_path.with_suffix('.pdf')
    
    cmd = [
        'pandoc',
        str(md_path),
        '-o', str(pdf_path),
        '--pdf-engine=xelatex',
        '-V', 'geometry:margin=1in',
        '-V', 'fontsize=9pt',
        '-V', 'mainfont=DejaVu Sans Mono',
        '--highlight-style=tango',
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Generated: {pdf_path.name}")
        return pdf_path
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate PDF for {md_path.name}")
        print(f"  Error: {e.stderr}")
        return None
    except FileNotFoundError:
        print("✗ pandoc not found. Please install pandoc:")
        print("  brew install pandoc  # macOS")
        print("  or visit: https://pandoc.org/installing.html")
        return None

def check_dependencies() -> bool:
    """Check if required tools are available."""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pandoc found: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ pandoc not found")
    print("\nInstallation instructions:")
    print("  macOS:   brew install pandoc basictex")
    print("  Ubuntu:  sudo apt-get install pandoc texlive-xetex")
    print("  Windows: choco install pandoc miktex")
    return False

def main():
    print("=" * 80)
    print("F.A.R.F.A.N Code Audit PDF Generator")
    print("=" * 80)
    print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"✓ Output directory: {OUTPUT_DIR}")
    print()
    
    # Collect files
    print("Collecting Python files...")
    all_files = collect_python_files()
    print(f"✓ Found {len(all_files)} Python files")
    print()
    
    # Organize by directory
    print("Organizing files by directory...")
    organized = organize_files_by_directory(all_files)
    for dir_name, files in sorted(organized.items()):
        print(f"  {dir_name}: {len(files)} files")
    print()
    
    # Split into batches
    print(f"Splitting into {NUM_PDFS} batches...")
    batches = split_into_batches(organized, NUM_PDFS)
    actual_batches = len(batches)
    print(f"✓ Created {actual_batches} batches")
    for i, batch in enumerate(batches, 1):
        print(f"  Batch {i:02d}: {len(batch)} files")
    print()
    
    # Generate PDFs
    print("Generating PDFs...")
    print("(This may take several minutes...)")
    print()
    
    successful = 0
    failed = 0
    
    for i, batch in enumerate(batches, 1):
        print(f"Processing batch {i}/{actual_batches}...", end=' ')
        
        # Create markdown
        md_path = create_markdown_for_batch(batch, i)
        
        # Convert to PDF
        pdf_path = convert_markdown_to_pdf(md_path)
        
        if pdf_path:
            successful += 1
            # Optionally remove markdown after successful conversion
            # md_path.unlink()
        else:
            failed += 1
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(all_files)}")
    print(f"PDFs generated: {successful}")
    print(f"Failed: {failed}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print()
    
    if successful > 0:
        print("✓ PDF generation complete!")
        print("\nYou can now review the code in organized PDF batches.")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    exit(main())
