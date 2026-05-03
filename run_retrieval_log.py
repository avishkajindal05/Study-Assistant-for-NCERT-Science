# run_retrieval_log.py
import json
from src.retrieval.vector_store import retrieve

questions = [
    {"id": 1, "q": "What is displacement?", "expected_chunk": "ch_0007"},
    {"id": 2, "q": "What is acceleration?", "expected_chunk": "ch_0024"},
    {"id": 3, "q": "What does the slope of a velocity-time graph represent?", "expected_chunk": "ch_0029"},
    {"id": 4, "q": "What is the SI unit of acceleration?", "expected_chunk": "ch_0024"},
    {"id": 5, "q": "What does a horizontal line on a position-time graph mean?", "expected_chunk": "ch_0022"},
    {"id": 6, "q": "What is uniform circular motion?", "expected_chunk": "ch_0065"},
    {"id": 7, "q": "If an object returns to starting point what is displacement?", "expected_chunk": "ch_0007"},
    {"id": 8, "q": "If velocity is not changing what is acceleration?", "expected_chunk": "ch_0029"},
    {"id": 9, "q": "Constant speed in a circle is it accelerating?", "expected_chunk": "ch_0065"},
    {"id": 10, "q": "What are the three equations of motion?", "expected_chunk": "ch_0056"},
]

log = []
for item in questions:
    hits = retrieve(item["q"], k=5)
    top1 = hits[0]
    correct = top1["chunk_id"] == item["expected_chunk"]
    log.append({
        "id": item["id"],
        "question": item["q"],
        "top1_chunk_id": top1["chunk_id"],
        "top1_score": top1["score"],
        "top1_correct": correct,
        "top5_chunk_ids": [h["chunk_id"] for h in hits],
        "expected_chunk": item["expected_chunk"]
    })
    status = "✓" if correct else "✗"
    print(f"Q{item['id']} {status} top1={top1['chunk_id']} (score={top1['score']}) expected={item['expected_chunk']}")

with open("retrieval_log.json", "w") as f:
    json.dump(log, f, indent=2)

hit_rate = sum(1 for r in log if r["top1_correct"]) / len(log)
print(f"\nTop-1 hit rate: {hit_rate:.0%} ({sum(1 for r in log if r['top1_correct'])}/{len(log)})")
print("Saved retrieval_log.json")