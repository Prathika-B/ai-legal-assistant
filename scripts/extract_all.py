import fitz
import pytesseract
from PIL import Image
import io
import os

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

# filename in data/raw -> output name in data/processed
ACTS = {
    "ipc.pdf": "ipc_raw.txt",
    "motor_vehicles_act.pdf": "motor_vehicles_act_raw.txt",
    "consumer_protection_act.pdf": "consumer_protection_act_raw.txt",
    "negotiable_instruments_act.pdf": "negotiable_instruments_act_raw.txt",
    "industrial_disputes_act.pdf": "industrial_disputes_act_raw.txt",
    "transfer_of_property_act.pdf": "transfer_of_property_act_raw.txt",
    "bns.pdf": "bns_raw.txt",
    "bnss.pdf": "bnss_raw.txt",
    "bsa.pdf": "bsa_raw.txt",
    "it_act.pdf": "it_act_raw.txt",
    "posh_act.pdf": "posh_act_raw.txt",
    "domestic_violence_act.pdf": "domestic_violence_act_raw.txt",    
    "specific_relief_act_1963.pdf": "specific_relief_act_1963_raw.txt",
    
}
def extract_pdf_text(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    full_text = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        full_text.append(text)
        print(f"  page {i + 1}/{len(doc)}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_text))

if __name__ == "__main__":
    for pdf_name, txt_name in ACTS.items():
        pdf_path = os.path.join("data", "raw", pdf_name)
        output_path = os.path.join("data", "processed", txt_name)

        if os.path.exists(output_path):
            print(f"Skipping {pdf_name} — already extracted.")
            continue

        print(f"Extracting {pdf_name}...")
        extract_pdf_text(pdf_path, output_path)
        print(f"Done: {output_path}\n")

    print("All acts processed.")