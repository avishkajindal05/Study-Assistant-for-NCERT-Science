import fitz
import json
import os
from typing import List, Dict

class PDFLoader:
    def __init__(self):
        pass

    def extract_blocks(self, pdf_path: str) -> List[Dict]:
        doc = fitz.open(pdf_path)
        out = []
        for pno, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" not in b:
                    continue
                text, fonts, sizes = "", [], []
                for line in b["lines"]:
                    for span in line["spans"]:
                        t = span["text"].strip()
                        if not t:
                            continue
                        text += t + " "
                        fonts.append(span["font"])
                        sizes.append(span["size"])
                text = text.strip()
                if not text:
                    continue
                out.append({
                    "page": pno + 1,
                    "text": text,
                    "bbox": b["bbox"],
                    "avg_font_size": (sum(sizes) / len(sizes)) if sizes else 0.0,
                    "fonts": list(set(fonts))
                })
        return out

    def save(self, blocks: List[Dict], out_path: str):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)

def run(pdf_path: str, out_path: str):
    loader = PDFLoader()
    blocks = loader.extract_blocks(pdf_path)
    loader.save(blocks, out_path)
    print(f"Saved {len(blocks)} blocks → {out_path}")

if __name__ == "__main__":
    run("data/raw/motion.pdf", "data/processed/motion_blocks.json")