import fitz
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

doc = fitz.open("data/raw/ipc.pdf")
page = doc[2]

pix = page.get_pixmap(dpi=300)
img = Image.open(io.BytesIO(pix.tobytes("png")))

text = pytesseract.image_to_string(img)
print(text[:500])