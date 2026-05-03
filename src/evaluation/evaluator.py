# src/evaluation/evaluator.py
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

    def run(self, output_path: str = None):
        questions = self.load_questions(CFG.EVAL_PATH)
        results = []

        for q in questions:
            print(f"\nQ{q['id']}: {q['question'][:60]}")
            output = self.qa.answer(q["question"])

            eval_metrics = self.metrics.evaluate(
                output["answer"],
                q["expected"],
                q["type"]
            )

            grounded = self.metrics.check_grounding(
                output["answer"],
                output["retrieved_chunks"]
            )

            row = {
                "id": q["id"],
                "question": q["question"],
                "type": q["type"],
                "answer": output["answer"],
                "retrieved_chunks": output["retrieved_chunk_ids"],
                "retrieval_scores": output.get("retrieval_scores", []),
                "correctness": eval_metrics["correctness"],
                "grounded": grounded,
                "refusal": eval_metrics["refusal"],
                "refusal_appropriate": eval_metrics["refusal_appropriate"],
                "notes": ""
            }

            results.append(row)
            print(f"  → correct: {row['correctness']} | grounded: {grounded} | refusal: {row['refusal']}")

        df = pd.DataFrame(results)
        path = output_path or CFG.RESULTS_PATH
        df.to_csv(path, index=False)
        print(f"\nSaved → {path}")

        # Print summary
        answerable = df[df["type"] != "out_of_scope"]
        oos = df[df["type"].isin(["out_of_scope", "out_of_scope_plausible"])]
        print(f"\n=== SUMMARY ===")
        print(f"Correct:   {(answerable['correctness']=='correct').sum()}/{len(answerable)}")
        print(f"Grounded:  {df['grounded'].sum()}/{len(df)}")
        print(f"OOS refused: {oos['refusal'].sum()}/{len(oos)}")


if __name__ == "__main__":
    Evaluator().run()