import requests
from src.utils.config import CFG

class OllamaLLM:
    def __init__(self, model: str = None, temperature: float = None):
        self.model = model or CFG.OLLAMA_MODEL
        self.temperature = CFG.TEMPERATURE if temperature is None else temperature
        self.url = CFG.OLLAMA_URL

    def generate(self, prompt: str) -> str:
        r = requests.post(self.url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature}
        }, timeout=120)
        r.raise_for_status()
        return r.json()["response"]