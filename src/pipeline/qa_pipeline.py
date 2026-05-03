# src/pipeline/qa_pipeline.py
from typing import Dict
from src.utils.config import CFG
from src.retrieval.vector_store import retrieve
from src.generation.ollama_client import OllamaLLM
from src.generation.prompt import PromptBuilder


class QAPipeline:
    def __init__(self):
        self.llm = OllamaLLM(model=CFG.OLLAMA_MODEL)
        self.prompter = PromptBuilder(version=CFG.PROMPT_VERSION)

    def answer(self, question: str) -> Dict:
        hits = retrieve(question, k=CFG.TOP_K)
        texts = [h["text"] for h in hits]
        chunk_ids = [h["chunk_id"] for h in hits]
        scores = [h["score"] for h in hits]

        # Pass chunk_ids so prompt labels each context block
        prompt = self.prompter.build(question, texts, chunk_ids=chunk_ids)
        ans = self.llm.generate(prompt)

        refusal = any(
            phrase in ans.lower()
            for phrase in ["cannot answer", "i don't have that", "don't have that in my study"]
        )

        return {
            "answer": ans,
            "retrieved_chunk_ids": chunk_ids,
            "retrieved_chunks": texts,
            "retrieval_scores": scores,
            "backend_used": "ollama",
            "refusal": refusal
        }