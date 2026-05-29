"""OCR scanned PDFs using EasyOCR backend, save extracted text to files.

Usage:
    python scripts/ocr_scanned_pdfs.py           # all 5 files
    python scripts/ocr_scanned_pdfs.py --file 2022  # single file by keyword
    python scripts/ocr_scanned_pdfs.py --dry-run    # check which are scanned
"""

import sys
sys.path.insert(0, ".")

import os
from pathlib import Path

PACKAGE_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包")
OUTPUT_DIR = Path(__file__).parent / "ocr_output"
OUTPUT_DIR.mkdir(exist_ok=True)

SCANNED_PDFS = [
    ("2022-2025真题/2022年上海第二工业大学804真题.pdf", "2022真题"),
    ("2022-2025真题/2023年上海第二工业大学804真题.pdf", "2023真题"),
    ("2022-2025真题/25二工大804回忆版.pdf", "2025回忆版"),
    ("C语言知识点总结/题库3-c语言10套卷含答案【32页】.pdf", "题库3-10套卷"),
    ("C语言知识点总结/题库6-c语言程序填空题库【28页】.pdf", "题库6-程序填空"),
]


def check_if_scanned(pdf_path: Path) -> bool:
    import pdfplumber
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            total_chars = 0
            pages_to_check = min(5, len(pdf.pages))
            for page in pdf.pages[:pages_to_check]:
                text = page.extract_text()
                if text:
                    total_chars += sum(1 for c in text if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            return (total_chars / pages_to_check) < 50
    except Exception:
        return True


def ocr_pdf(pdf_path: Path) -> str:
    from app.services.ocr_service import ocr_pdf as do_ocr
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
    was_scanned, text = do_ocr(file_bytes)
    return text


def main():
    dry_run = "--dry-run" in sys.argv
    target_keyword = None
    for arg in sys.argv[1:]:
        if arg.startswith("--file="):
            target_keyword = arg.split("=", 1)[1]
        elif arg == "--file":
            idx = sys.argv.index("--file")
            target_keyword = sys.argv[idx + 1]

    for rel_path, label in SCANNED_PDFS:
        if target_keyword and target_keyword not in label and target_keyword not in rel_path:
            continue

        pdf_path = PACKAGE_DIR / rel_path
        if not pdf_path.exists():
            print(f"SKIP (not found): {rel_path}")
            continue

        output_file = OUTPUT_DIR / f"{label}.txt"

        if dry_run:
            is_scan = check_if_scanned(pdf_path)
            status = "SCANNED" if is_scan else "TEXT-BASED"
            print(f"[DRY RUN] {label}: {status} ({pdf_path.stat().st_size/1024:.0f}KB)")
            if not is_scan:
                print(f"  WARNING: Not scanned! Would extract via pdfplumber instead.")
            continue

        print(f"OCR: {label} ({pdf_path.stat().st_size/1024:.0f}KB)...", end=" ", flush=True)
        try:
            text = ocr_pdf(pdf_path)
            output_file.write_text(text, encoding="utf-8")
            print(f"DONE ({len(text)} chars -> {output_file.name})")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
