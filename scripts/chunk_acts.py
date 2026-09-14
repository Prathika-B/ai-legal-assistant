import os
import re
import json

RAW_DIR = os.path.join("data", "processed")
OUTPUT_FILE = os.path.join("data", "processed", "chunks.json")

FILES = {
    "ipc_raw.txt": "Indian Penal Code, 1860",
    "motor_vehicles_act_raw.txt": "Motor Vehicles Act, 1988",
    "consumer_protection_act_raw.txt": "Consumer Protection Act, 2019",
    "negotiable_instruments_act_raw.txt": "Negotiable Instruments Act, 1881",
    "industrial_disputes_act_raw.txt": "Industrial Disputes Act, 1947",
    "transfer_of_property_act_raw.txt": "Transfer of Property Act, 1882",
    "bns_raw.txt": "Bharatiya Nyaya Sanhita, 2023",
    "bnss_raw.txt": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bsa_raw.txt": "Bharatiya Sakshya Adhiniyam, 2023",
    "it_act_raw.txt": "Information Technology Act, 2000",
    "posh_act_raw.txt": "Sexual Harassment of Women at Workplace Act, 2013",
    "domestic_violence_act_raw.txt": "Protection of Women from Domestic Violence Act, 2005",
}


def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_sections(text, loose=False):
    if loose:
        # Fallback for clean Gazette-format acts with no footnotes,
        # where OCR sometimes drops the section's heading word.
        pattern = re.compile(r"\n(?=\d{1,4}[A-Z]?\.\s)")
    else:
        # Splits wherever a line starts with a number followed by a period,
        # e.g. "302." or "138." -- a common pattern for section starts in bare acts.
        pattern = re.compile(r"\n(?=\d{1,4}[A-Z]?\.\s+[A-Z][a-zA-Z\s]{3,80}[\.\u2014:])")
    parts = pattern.split(text)
    return [p.strip() for p in parts if len(p.strip()) > 30]


FOOTNOTE_PREFIX = re.compile(
    r"^\d{1,3}[A-Za-z]?\.\s+(Subs\.|Ins\.|Rep\.|Omitted|Added|Cl\.|The words).*$",
    re.MULTILINE,
)


def strip_footnote_lines(text):
    lines = text.split("\n")
    while lines and FOOTNOTE_PREFIX.match(lines[0].strip()):
        lines.pop(0)
    return "\n".join(lines).strip()


def main():
    all_chunks = []
    chunk_id = 0

    for filename, act_name in FILES.items():
        path = os.path.join(RAW_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        cleaned = clean_text(raw)
        use_loose = filename in ("bnss_raw.txt", "bsa_raw.txt")
        sections = split_into_sections(cleaned, loose=use_loose)

        for section_text in sections:
            section_text = strip_footnote_lines(section_text)

            # Skip TOC-style entries: title-only lines with no real body text
            first_line_end = section_text.find(".", section_text.find(".") + 1)
            remainder = section_text[first_line_end:].strip() if first_line_end != -1 else ""
            if len(remainder) < 60:
                continue
            if "ACT NO." in section_text and "[6th October" in section_text:
                continue  # cover page artifact

            chunk_id += 1
            all_chunks.append({
                "id": f"chunk_{chunk_id:04d}",
                "act": act_name,
                "source": filename,
                "text": section_text[:2000],
            })

        print(f"{act_name}: {len(sections)} chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()