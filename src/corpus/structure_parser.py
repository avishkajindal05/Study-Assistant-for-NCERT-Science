import json, re, os
from typing import List, Dict

class StructureParser:
    def __init__(self, width_threshold: float = 200):
        self.width_threshold = width_threshold

    def load(self, p): 
        return json.load(open(p, "r", encoding="utf-8"))

    def save(self, blocks, p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(blocks, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    def is_side_note(self, b):
        x0,y0,x1,y1 = b["bbox"]
        return (x1-x0) < self.width_threshold

    def tag(self, blocks: List[Dict]) -> List[Dict]:
        out=[]
        for i,b in enumerate(blocks):
            t=b["text"].strip()
            ct="concept"
            if t.startswith("Example"): ct="worked_example"
            elif t.startswith("Solution"): ct="solution"
            elif "Exercise" in t: ct="exercise"
            elif self.is_side_note(b): ct="side_note"

            b["content_type"]=ct
            b["has_equation"]=bool(re.search(r"(=|/|\(\d+\.\d+[a-z]?\))", t))
            b["has_figure"]=bool(re.search(r"Fig\.\s*\d+\.\d+", t))
            b["block_index"]=i
            out.append(b)
        return out

    def merge_notes(self, blocks: List[Dict]) -> List[Dict]:
        merged=[]
        for b in blocks:
            if b["content_type"]=="side_note" and merged:
                merged[-1]["text"] += "\n[NOTE] " + b["text"]
                merged[-1]["has_note"]=True
            else:
                merged.append(b)
        return merged

    def run(self, inp, outp, merge_notes=True):
        blocks=self.load(inp)
        blocks=self.tag(blocks)
        if merge_notes: blocks=self.merge_notes(blocks)
        self.save(blocks, outp)
        print(f"Saved structured → {outp}")

if __name__=="__main__":
    StructureParser().run(
        "data/processed/cleaned_blocks.json",
        "data/processed/structured_blocks.json",
        merge_notes=True
    )