import json
import pandas as pd
from src.pipeline.qa_pipeline import QAPipeline
from src.evaluation.metrics import Metrics
from src.utils.config import CFG


class Evaluator:
    def __init__(self):
        self.qa = QAPipeline()
        self.metrics = Metrics()

    def load_questions(self, path):
        with open(path, "r") as f:
            return json.load(f)["questions"]

    def run(self):
        questions = self.load_questions(CFG.EVAL_PATH)

        results = []

        for q in questions:
            print(f"\nQ: {q['question']}")

            output = self.qa.answer(q["question"])

            eval_metrics = self.metrics.evaluate(
                output["answer"],
                q["expected"],
                q["type"]
            )

            row = {
                "id": q["id"],
                "question": q["question"],
                "type": q["type"],
                "answer": output["answer"],
                "retrieved_chunks": output["retrieved_chunk_ids"],
                "correctness": eval_metrics["correctness"],
                "refusal": eval_metrics["refusal"],
                "refusal_appropriate": eval_metrics["refusal_appropriate"]
            }

            results.append(row)

        df = pd.DataFrame(results)
        df.to_csv(CFG.RESULTS_PATH, index=False)

        print(f"\nSaved results → {CFG.RESULTS_PATH}")


if __name__ == "__main__":
    Evaluator().run()