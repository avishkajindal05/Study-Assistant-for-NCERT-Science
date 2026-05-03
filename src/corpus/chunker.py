import json, os
from typing import List, Dict

class Chunker:
    def __init__(self, max_words: int = 300, overlap: int = 50):
        self.max_words = max_words
        self.overlap = overlap

    def load(self, p): 
        return json.load(open(p, "r", encoding="utf-8"))

    def save(self, chunks, p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(chunks, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    def _should_keep_together(self, b: Dict) -> bool:
        return b.get("content_type") in ("worked_example","solution") or b.get("has_equation", False)

    def build(self, blocks: List[Dict]) -> List[Dict]:
        chunks=[]
        cur_text=[]
        cur_meta=[]
        for b in blocks:
            words = b["text"].split()
            if not cur_text:
                cur_text = words[:]
                cur_meta = [b]
                continue
            # Force new chunk if this block starts a definition
            definition_starters = ["displacement is", "velocity is", "acceleration is", 
                                    "speed is", "is defined as", "let us now define"]
            block_start = b["text"].lower()[:60]
            if any(block_start.find(s) != -1 for s in definition_starters) and cur_text:
                chunks.append(self._pack(chunks, cur_text, cur_meta))
                cur_text = []
                cur_meta = []

            if len(cur_text)+len(words) <= self.max_words or self._should_keep_together(b):
                cur_text += words
                cur_meta.append(b)
            else:
                chunks.append(self._pack(chunks, cur_text, cur_meta))
                # overlap
                cur_text = cur_text[-self.overlap:] + words
                cur_meta = [b]

        if cur_text:
            chunks.append(self._pack(chunks, cur_text, cur_meta))
        return chunks

    def _pack(self, chunks, words, meta):
        text = " ".join(words)
        return {
            "chunk_id": f"ch_{len(chunks):04d}",
            "text": text,
            "content_types": list({m["content_type"] for m in meta}),
            "has_equation": any(m.get("has_equation", False) for m in meta),
            "has_figure": any(m.get("has_figure", False) for m in meta),
            "token_count_est": len(words)
        }

    def run(self, inp, outp):
        blocks=self.load(inp)
        chunks=self.build(blocks)
        self.save(chunks, outp)
        print(f"Saved {len(chunks)} chunks → {outp}")

if __name__=="__main__":
    Chunker().run(
        "data/processed/structured_blocks.json",
        "data/chunks/chunks.json"
    )