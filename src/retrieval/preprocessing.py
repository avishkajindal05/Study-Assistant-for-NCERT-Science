import re
from typing import List


class TextPreprocessor:
    def __init__(self):
        pass

    def normalize(self, text: str) -> str:
        text = text.lower()

        # remove punctuation except important math symbols
        text = re.sub(r"[^\w\s=/.-]", "", text)

        # normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        text = self.normalize(text)
        return text.split()

    def preprocess(self, text: str) -> List[str]:
        return self.tokenize(text)