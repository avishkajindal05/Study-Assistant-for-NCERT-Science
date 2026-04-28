from typing import List

class PromptBuilder:
    def build(self, question: str, chunks: List[str]) -> str:
        ctx = "\n\n".join(chunks)
        return f"""You are a NCERT Science assistant.
Answer ONLY using the context.
If not present, say: "I cannot answer this from the available textbook content."

Context:
{ctx}

Question: {question}

Answer:"""