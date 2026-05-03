# src/utils/config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # Paths
    RAW_DIR: str = "data/raw"
    PROCESSED_DIR: str = "data/processed"
    CHUNKS_PATH: str = "data/chunks/wk10_chunks.json"

    # Retrieval
    TOP_K: int = 5

    # LLM
    LLM_BACKEND: str = "ollama"
    OLLAMA_MODEL: str = "llama3"
    TEMPERATURE: float = 0.0
    OLLAMA_URL: str = "http://localhost:11434/api/generate"

    # Embeddings (Ollama local — no OpenAI)
    EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_EMBED_URL: str = "http://localhost:11434/api/embeddings"

    # Prompt & results versioning
    PROMPT_VERSION: str = "v2"
    RESULTS_PATH: str = "results/eval_scored.csv"

    # Eval
    EVAL_PATH: str = "src/evaluation/question_set_wk10.json"

CFG = Config()