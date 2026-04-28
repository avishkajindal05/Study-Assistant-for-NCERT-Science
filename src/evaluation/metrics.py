from typing import Dict


class Metrics:
    def __init__(self):
        pass

    def check_correctness(self, answer, expected):
        if expected is None:
            return "N/A"

        answer = answer.lower()

        if expected in answer:
            return "correct"
        elif any(word in answer for word in expected.split()):
            return "partial"
        else:
            return "incorrect"

    def check_refusal(self, answer: str) -> bool:
        return "cannot answer" in answer.lower()

    def evaluate(self, answer: str, expected: str, q_type: str) -> Dict:
        correctness = self.check_correctness(answer, expected)
        refusal = self.check_refusal(answer)

        refusal_appropriate = False
        if q_type == "out_of_scope":
            refusal_appropriate = refusal

        return {
            "correctness": correctness,
            "refusal": refusal,
            "refusal_appropriate": refusal_appropriate
        }
    def check_grounding(self, answer: str, chunks: list) -> bool:
        combined = " ".join(chunks).lower()
        return any(sentence.strip().lower() in combined for sentence in answer.split("."))