import re
import json
import os
from typing import List, Dict


class TextCleaner:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        # remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\d+o", "", text)  # fixes 'the0'

        # remove page numbers (simple heuristic)
        text = re.sub(r"\bPage\s*\d+\b", "", text)

        # fix broken hyphen words (e.g., velo-\ncity → velocity)
        text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

        # preserve equations but normalize spacing
        text = re.sub(r"\s*=\s*", " = ", text)
        text = re.sub(r"\s*/\s*", " / ", text)

        # preserve figure references
        text = re.sub(r"Fig\.\s*(\d+\.\d+)", r"[FIGURE_\1]", text)

        # preserve equation labels
        text = re.sub(r"\((\d+\.\d+[a-z]?)\)", r"[EQUATION_\1]", text)

        return text.strip()

    def process_blocks(self, blocks: List[Dict]) -> List[Dict]:
        cleaned = []

        for block in blocks:
            new_block = block.copy()
            new_block["text"] = self.clean_text(block["text"])
            cleaned.append(new_block)

        return cleaned

    def run(self, input_path: str, output_path: str):
        with open(input_path, "r", encoding="utf-8") as f:
            blocks = json.load(f)

        cleaned_blocks = self.process_blocks(blocks)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_blocks, f, indent=2, ensure_ascii=False)

        print(f"Cleaned {len(cleaned_blocks)} blocks → {output_path}")


if __name__ == "__main__":
    cleaner = TextCleaner()

    cleaner.run(
        input_path="data/processed/motion_blocks.json",
        output_path="data/processed/cleaned_blocks.json"
    )