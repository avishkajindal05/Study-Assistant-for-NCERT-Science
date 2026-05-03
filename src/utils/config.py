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
    PROMPT_VERSION: str = "v2"
    RESULTS_PATH: str = f"results/evaluation_results_{PROMPT_VERSION}.csv"

CFG = Config()