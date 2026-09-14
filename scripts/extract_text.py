import fitz
import pytesseract
from PIL import Image
import io
import os

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

def extract_pdf_text(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    full_text = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        full_text.append(text)
        print(f"Processed page {i + 1}/{len(doc)}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_text))

    print(f"Saved extracted text to {output_path}")

if __name__ == "__main__":
    extract_pdf_text("data/raw/ipc.pdf", "data/processed/ipc_raw.txt")