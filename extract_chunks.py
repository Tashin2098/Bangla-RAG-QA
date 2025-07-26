import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re

# ---- SET THESE PATHS ----
POPPLER_PATH = r"C:\Users\HP\AppData\Local\Temp\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # <-- Your Poppler bin
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # <-- Your Tesseract install path
PDF_PATH = "data/HSC26-Bangla1st-Paper.pdf"
CHUNKS_PATH = "vector_store/chunks.txt"

# ---- Configure Tesseract ----
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_pdf(pdf_path, poppler_path, start_page=6, end_page=17):
    """Extract Bangla text from each PDF page image using OCR, only main story pages."""
    pages = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=300)
    # PDF pages are 1-based, so slice accordingly
    selected_pages = pages[start_page-1:end_page]
    all_texts = []
    for idx, page_img in enumerate(selected_pages, start=start_page):
        print(f"OCR extracting from PDF page {idx}...")
        text = pytesseract.image_to_string(page_img, lang='ben')
        # Remove weird OCR line breaks and clean up
        text = re.sub(r'[ \t]+\n', '\n', text)
        all_texts.append(text.strip())
    return all_texts

def chunk_text(paragraphs, min_len=30):
    """Split page texts into paragraph-based chunks (separated by blank lines) for RAG."""
    chunks = []
    for page_text in paragraphs:
        # Normalize double/triple newlines just in case
        page_text = re.sub(r'\n{2,}', '\n\n', page_text)
        paras = [p.strip() for p in page_text.split('\n\n') if len(p.strip()) > min_len]
        chunks.extend(paras)
    return chunks

def remove_watermarks(chunk):
    patterns = [
        r"HSC ?26",
        r"অনলাইন ব্যাচ",
        r"10 ?MINUTE ?SCHOOL",
        r"মিনিট স্কুল",
        r"Minute School",
        r"কল ?আল্লাইন ব্যাচ"
    ]
    cleaned_lines = []
    for line in chunk.split('\n'):
        if not any(re.search(pat, line, re.IGNORECASE) for pat in patterns):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

if __name__ == "__main__":
    os.makedirs('vector_store', exist_ok=True)
    # OCR extraction for main story (pages 6–17 only)
    page_texts = extract_text_from_pdf(PDF_PATH, POPPLER_PATH, start_page=6, end_page=17)
    print(f"OCR extracted from {len(page_texts)} pages (main story).")

    # Chunking
    chunks = chunk_text(page_texts)
    print(f"Total {len(chunks)} chunks before cleaning.")

    # Clean chunks: remove watermarks/logos
    cleaned_chunks = [remove_watermarks(c) for c in chunks if len(remove_watermarks(c).strip()) > 30]
    print(f"Total {len(cleaned_chunks)} chunks after cleaning.")

    # Write cleaned chunks
    with open(CHUNKS_PATH, 'w', encoding='utf-8') as f:
        for c in cleaned_chunks:
            f.write(c.replace('\n', ' ').strip() + "\n---chunk---\n")
    print(f"Cleaned chunks saved to {CHUNKS_PATH}")
