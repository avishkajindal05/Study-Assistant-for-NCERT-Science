# src/corpus/chunker.py
import json, os
from typing import List, Dict
import tiktoken

class Chunker:
    def __init__(self, max_tokens: int = 250, overlap_tokens: int = 50):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        # cl100k_base is the tokenizer for text-embedding-3-small — use same here
        self.enc = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, words: List[str]) -> int:
        return len(self.enc.encode(" ".join(words)))

    def load(self, p):
        return json.load(open(p, "r", encoding="utf-8"))

    def save(self, chunks, p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(chunks, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    def _should_keep_together(self, b: Dict) -> bool:
        return b.get("content_type") in ("worked_example", "solution") or b.get("has_equation", False)

    def build(self, blocks: List[Dict]) -> List[Dict]:
        chunks = []
        cur_words = []
        cur_meta = []

        for b in blocks:
            words = b["text"].split()
            if not cur_words:
                cur_words = words[:]
                cur_meta = [b]
                continue

            # Force new chunk at definition boundaries
            definition_starters = [
                "displacement is", "velocity is", "acceleration is",
                "speed is", "is defined as", "let us now define"
            ]
            block_start = b["text"].lower()[:60]
            if any(s in block_start for s in definition_starters) and cur_words:
                chunks.append(self._pack(chunks, cur_words, cur_meta))
                cur_words = []
                cur_meta = []

            new_token_count = self._count_tokens(cur_words + words)

            if new_token_count <= self.max_tokens or self._should_keep_together(b):
                cur_words += words
                cur_meta.append(b)
            else:
                chunks.append(self._pack(chunks, cur_words, cur_meta))
                # overlap: take last overlap_tokens worth of words (approx)
                overlap_words = cur_words[-self.overlap_tokens:]
                cur_words = overlap_words + words
                cur_meta = [b]

        if cur_words:
            chunks.append(self._pack(chunks, cur_words, cur_meta))

        return chunks

    def _pack(self, chunks, words, meta):
        text = " ".join(words)
        token_count = self._count_tokens(words)

        # Extract page: use the first block's page if available, else None
        pages = [m.get("page") for m in meta if m.get("page") is not None]
        page = pages[0] if pages else None

        return {
            "chunk_id": f"ch_{len(chunks):04d}",
            "text": text,
            "content_types": list({m["content_type"] for m in meta}),
            "has_equation": any(m.get("has_equation", False) for m in meta),
            "has_figure": any(m.get("has_figure", False) for m in meta),
            "token_count": token_count,          # now actual tokens, not word estimate
            "page": page,                         # NEW — required for Wk10
            "source": "motion.pdf",               # NEW — required for Wk10
            "section": self._infer_section(meta)  # NEW — best-effort
        }

    def _infer_section(self, meta: List[Dict]) -> str:
        # Use section field from block metadata if your structure_parser sets it
        for m in meta:
            if m.get("section"):
                return m["section"]
        return "unknown"

    def run(self, inp, outp):
        blocks = self.load(inp)
        chunks = self.build(blocks)
        self.save(chunks, outp)
        print(f"Saved {len(chunks)} chunks → {outp}")
        print(f"Token counts — min: {min(c['token_count'] for c in chunks)}, "
              f"max: {max(c['token_count'] for c in chunks)}, "
              f"avg: {sum(c['token_count'] for c in chunks) // len(chunks)}")

if __name__ == "__main__":
    Chunker().run(
        "data/processed/structured_blocks.json",
        "data/chunks/wk10_chunks.json"   # new output file — don't overwrite wk9
    )