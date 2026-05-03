from typing import List

class PromptBuilder:
    def __init__(self, version: str = "v2"):
        self.version = version

    def build(self, question: str, chunks: List[str]) -> str:
        ctx = "\n\n---\n\n".join(chunks)

        with open(f"prompts/prompt_{self.version}.txt", "r", encoding="utf-8") as f:
            template = f.read()

        return template.replace("{ctx}", ctx).replace("{question}", question)