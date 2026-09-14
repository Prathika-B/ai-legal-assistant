import os
import json
import fitz
import pytesseract
from PIL import Image
import io
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0.1,
)

SUMMARY_PROMPT = """You are a legal document analysis assistant. Analyze the document text below and respond with ONLY valid JSON (no markdown, no extra text) in exactly this shape:

{{
  "summary": "2-3 sentence plain-language summary of what this document is",
  "key_points": ["point 1", "point 2", "..."],
  "key_clauses": ["clause description 1", "clause description 2", "..."],
  "legal_terms": [{{"term": "term name", "meaning": "plain-language explanation"}}],
  "risks": ["potential risk or concern 1", "..."]
}}

Document text:
{document_text}
"""

prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)


def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = []

    for page in doc:
        # try direct text extraction first (fast path for clean PDFs)
        text = page.get_text()
        if len(text.strip()) < 30:
            # fall back to OCR for scanned/image-based pages
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
        full_text.append(text)

    return "\n\n".join(full_text)


def summarize_document(file_bytes):
    document_text = extract_text_from_pdf(file_bytes)

    # cap length to avoid overly long prompts on huge documents
    truncated_text = document_text[:15000]

    chain = prompt | llm
    response = chain.invoke({"document_text": truncated_text})

    raw_content = response.content.strip()
    # strip markdown code fences if the model added them despite instructions
    if raw_content.startswith("```"):
        raw_content = raw_content.strip("`")
        if raw_content.startswith("json"):
            raw_content = raw_content[4:]

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        return {
            "summary": "Could not parse a structured summary. Raw model output below.",
            "key_points": [],
            "key_clauses": [],
            "legal_terms": [],
            "risks": [],
            "raw_output": raw_content,
        }