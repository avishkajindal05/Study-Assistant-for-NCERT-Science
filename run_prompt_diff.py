# run_prompt_diff.py — run once, captures both prompt versions on 3 queries
from src.retrieval.vector_store import retrieve
from src.generation.ollama_client import OllamaLLM
from src.utils.config import CFG

llm = OllamaLLM()

test_questions = [
    "What is displacement?",                          # in-scope direct
    "If velocity is not changing, what is acceleration?",  # in-scope paraphrased
    "What is photosynthesis?"                          # out-of-scope
]

def build_prompt(template_path, question, chunks):
    ctx = "\n\n---\n\n".join(chunks)
    with open(template_path, "r") as f:
        template = f.read()
    return template.replace("{ctx}", ctx).replace("{question}", question)

results = []
for q in test_questions:
    hits = retrieve(q, k=5)
    texts = [h["text"] for h in hits]
    chunk_ids = [h["chunk_id"] for h in hits]

    permissive_prompt = build_prompt("prompts/prompt_permissive.txt", q, texts)
    strict_prompt = build_prompt("prompts/prompt_v2.txt", q, texts)

    permissive_ans = llm.generate(permissive_prompt)
    strict_ans = llm.generate(strict_prompt)

    results.append({
        "question": q,
        "chunk_ids": chunk_ids,
        "permissive": permissive_ans,
        "strict": strict_ans
    })
    print(f"Done: {q[:50]}")

# Write prompt_diff.md
with open("prompt_diff.md", "w") as f:
    f.write("# prompt_diff.md\n\n")
    f.write("## Prompt Versions Compared\n\n")
    f.write("**Permissive prompt**: 'Answer the question using the context below.' — no refusal instruction, no citation requirement.\n\n")
    f.write("**Strict prompt (v2)**: Numbered rules, explicit refusal phrase, [Source: chunk_id] citation after every claim, figure refusal.\n\n---\n\n")
    for r in results:
        f.write(f"## Q: {r['question']}\n")
        f.write(f"**Retrieved chunks:** {r['chunk_ids']}\n\n")
        f.write(f"### Permissive answer\n{r['permissive']}\n\n")
        f.write(f"### Strict answer\n{r['strict']}\n\n---\n\n")

print("Saved prompt_diff.md")