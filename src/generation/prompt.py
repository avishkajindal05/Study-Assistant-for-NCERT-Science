# src/generation/prompt.py
from typing import List


class PromptBuilder:
    def __init__(self, version: str = "v2"):
        self.version = version

    def build(self, question: str, chunks: List[str], chunk_ids: List[str] = None) -> str:
        # Label each chunk with its ID so the model can cite correctly
        if chunk_ids:
            labeled = []
            for cid, text in zip(chunk_ids, chunks):
                labeled.append(f"[{cid}]\n{text}")
            ctx = "\n\n---\n\n".join(labeled)
        else:
            ctx = "\n\n---\n\n".join(chunks)

        with open(f"prompts/prompt_{self.version}.txt", "r", encoding="utf-8") as f:
            template = f.read()

        return template.replace("{ctx}", ctx).replace("{question}", question)