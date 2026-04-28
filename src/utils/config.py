import os
from dataclasses import dataclass

@dataclass
class Config:
    # Paths
    RAW_DIR: str = "data/raw"
    PROCESSED_DIR: str = "data/processed"
    CHUNKS_PATH: str = "data/chunks/chunks.json"

    # Retrieval
    TOP_K: int = 3

    # LLM
    LLM_BACKEND: str = "ollama"  # or "gemini"
    OLLAMA_MODEL: str = "phi3"
    TEMPERATURE: float = 0.0
    OLLAMA_URL: str = "http://localhost:11434/api/generate"

    # Eval
    EVAL_PATH: str = "src/evaluation/question_set.json"
    RESULTS_PATH: str = "results/evaluation_results_v1.csv"

CFG = Config()