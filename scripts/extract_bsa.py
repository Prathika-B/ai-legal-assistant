import fitz
import pytesseract
from PIL import Image
import io
import re

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

COMMON_WORDS = {
    "the", "of", "and", "in", "to", "or", "shall", "court", "means", "any",
    "act", "this", "section", "person", "which", "under", "for", "be",
}

def looks_english(text):
    if len(text.strip()) < 20:
        return False
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if len(words) < 10:
        return False
    common_count = sum(1 for w in words if w in COMMON_WORDS)
    return (common_count / len(words)) > 0.08
doc = fitz.open("data/raw/bsa.pdf")
english_pages = []
skipped = 0

for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img)

    if looks_english(text):
        english_pages.append(text)
    else:
        skipped += 1

    print(f"page {i+1}/{len(doc)} -- {'kept' if looks_english(text) else 'skipped (non-English)'}")

with open("data/processed/bsa_raw.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(english_pages))

print(f"\nDone. Kept {len(english_pages)} pages, skipped {skipped} non-English pages.")