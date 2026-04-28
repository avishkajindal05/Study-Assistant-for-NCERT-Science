from typing import Dict
from src.utils.config import CFG
from src.retrieval.bm25_retriever import BM25Retriever
from src.generation.ollama_client import OllamaLLM
from src.generation.prompt import PromptBuilder

class QAPipeline:
    def __init__(self):
        self.retriever = BM25Retriever(CFG.CHUNKS_PATH)
        self.llm = OllamaLLM(model=CFG.OLLAMA_MODEL)
        self.prompter = PromptBuilder()

    def answer(self, question: str) -> Dict:
        hits = self.retriever.search(question, k=CFG.TOP_K)
        texts = [h["text"] for h in hits]
        prompt = self.prompter.build(question, texts)
        ans = self.llm.generate(prompt)
        refusal = "cannot answer" in ans.lower()
        return {
            "answer": ans,
            "retrieved_chunk_ids": [h["chunk_id"] for h in hits],
            "retrieved_chunks": texts,
            "backend_used": "ollama",
            "refusal": refusal
        }