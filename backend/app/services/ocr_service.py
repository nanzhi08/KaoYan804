import logging
from io import BytesIO
from typing import Tuple

logger = logging.getLogger(__name__)

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    return _reader


def is_scanned_pdf(file_bytes: bytes) -> bool:
    """Return True if the PDF has little to no extractable text (scanned/image-based)."""
    import pdfplumber
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            total_chars = 0
            pages_to_check = min(5, len(pdf.pages))
            if pages_to_check == 0:
                return True
            for page in pdf.pages[:pages_to_check]:
                text = page.extract_text()
                if text:
                    # Only count CJK characters and ASCII letters/digits
                    total_chars += sum(1 for c in text if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            return (total_chars / pages_to_check) < 50
    except Exception:
        return True


def ocr_image(image_bytes: bytes) -> str:
    """Run OCR on a single image (PNG/JPEG) and return extracted text."""
    import numpy as np
    from PIL import Image

    reader = _get_reader()
    image = Image.open(BytesIO(image_bytes))
    image_np = np.array(image)
    results = reader.readtext(image_np)
    # Sort by vertical position, then horizontal
    results.sort(key=lambda r: (r[0][0][1], r[0][0][0]))
    texts = [text for (_, text, _) in results if text.strip()]
    return "\n".join(texts)


def ocr_pdf(file_bytes: bytes) -> Tuple[bool, str]:
    """
    Extract text from a PDF. Returns (was_scanned, text).
    Text-based PDFs use pdfplumber; scanned PDFs are rendered to images and OCR'd.
    """
    if not is_scanned_pdf(file_bytes):
        import pdfplumber
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            texts = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
            return (False, "\n".join(texts))

    import fitz
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    all_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        page_text = ocr_image(img_bytes)
        if page_text:
            all_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
    doc.close()
    return (True, "\n\n".join(all_text))
