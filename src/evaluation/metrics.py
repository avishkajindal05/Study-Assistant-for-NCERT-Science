# src/evaluation/metrics.py
from typing import Dict


class Metrics:
    # All phrases that count as a refusal — must match your prompts
    REFUSAL_PHRASES = [
        "cannot answer",
        "i don't have that",
        "don't have that in my study",
        "not in my study materials",
        "i cannot answer"
    ]

    def check_correctness(self, answer: str, expected: str) -> str:
        if expected is None:
            return "N/A"
        answer_lower = answer.lower()
        expected_lower = expected.lower()
        # Exact match anywhere in answer
        if expected_lower in answer_lower:
            return "correct"
        # Partial: all individual words of expected appear somewhere in answer
        expected_words = [w for w in expected_lower.split() if len(w) > 3]
        if expected_words and all(w in answer_lower for w in expected_words):
            return "correct"
        # Partial: at least one meaningful word matches
        if any(w in answer_lower for w in expected_words):
            return "partial"
        return "incorrect"

    def check_refusal(self, answer: str) -> bool:
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in self.REFUSAL_PHRASES)

    def check_grounding(self, answer: str, chunks: list) -> bool:
        if not answer or not chunks:
            return False
        combined = " ".join(chunks).lower()
        answer_lower = answer.lower()

        # Split answer into sentences, ignore very short ones and citation lines
        sentences = [
            s.strip() for s in answer_lower.replace("\n", " ").split(".")
            if len(s.strip()) > 20
            and "[source:" not in s.lower()
            and "i don't have" not in s.lower()
        ]
        if not sentences:
            return False

        # Grounded if ANY meaningful sentence has significant word overlap with chunks
        for sentence in sentences:
            words = [w for w in sentence.split() if len(w) > 4]
            if not words:
                continue
            matches = sum(1 for w in words if w in combined)
            if len(words) > 0 and matches / len(words) >= 0.4:
                return True
        return False

    def evaluate(self, answer: str, expected: str, q_type: str) -> Dict:
        correctness = self.check_correctness(answer, expected)
        refusal = self.check_refusal(answer)

        is_oos = q_type in ("out_of_scope", "out_of_scope_tricky", "out_of_scope_plausible")
        refusal_appropriate = refusal if is_oos else False

        return {
            "correctness": correctness,
            "refusal": refusal,
            "refusal_appropriate": refusal_appropriate
        }