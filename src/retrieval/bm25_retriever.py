from rank_bm25 import BM25Okapi
import json
from typing import List, Dict
from src.retrieval.preprocessing import TextPreprocessor


class BM25Retriever:
    def __init__(self, chunks_path: str):
        self.preprocessor = TextPreprocessor()

        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.corpus = [
            self.preprocessor.preprocess(c["text"])
            for c in self.chunks
        ]

        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query: str, k: int = 3) -> List[Dict]:
        query_tokens = self.preprocessor.preprocess(query)

        scores = self.bm25.get_scores(query_tokens)

        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        return [self.chunks[i] for i in top_indices]