# Failure Analysis

## Known Retrieval Failures (v1 evaluation)

### Q11 — "If an object returns to its starting point, what is the displacement?"
- **Retrieved:** ch_0002, ch_0003, ch_0007
- **Expected:** chunk containing "displacement is zero when object returns to origin"
- **Failure type:** Retrieval miss
- **Cause:** Query uses "returns to starting point" — corpus uses "comes back to its
  original position". BM25 found no term overlap with the definition chunk, returned
  early-chapter chunks instead.
- **Fix (pending):** Add query expansion or fix chunker to keep the zero-displacement
  example together with the definition.

### Q14 — "If velocity is not changing, what can you say about acceleration?"
- **Retrieved:** ch_0026, ch_0025, ch_0044
- **Failure type:** Retrieval miss
- **Cause:** Query is inferential — "if velocity is not changing" is a condition, not
  a term that appears verbatim in the corpus. BM25 matched on "velocity" and
  "acceleration" but returned chunks about velocity-time graphs, not the definition
  that acceleration = zero when velocity is constant.
- **Fix (pending):** BM25 cannot handle inferential queries. Requires dense retrieval
  (next week) or adding explicit Q&A pairs to the corpus.

### Q15 — "Even though a car moves at constant speed in a circle, is it accelerating?"
- **Retrieved:** ch_0044, ch_0015, ch_0045
- **Failure type:** Retrieval miss
- **Cause:** The answer exists in the circular motion chunks but the query phrase
  "constant speed in a circle" did not match the corpus phrasing "uniform circular
  motion". BM25 matched on "accelerating" and returned kinematics equation chunks
  instead.
- **Fix (pending):** Same as Q14 — vocabulary mismatch between natural query phrasing
  and textbook terminology. Dense retrieval would handle this.

---

## Pattern
All three failures share the same root cause: **vocabulary mismatch between how a
student phrases a question and how the textbook states the answer**. BM25 requires
term overlap to score relevance. When a student uses everyday language ("returns to
starting point", "not changing") instead of textbook terminology ("original position",
"zero acceleration"), BM25 fails silently — it returns plausible-looking but wrong
chunks, and the grounding prompt correctly refuses rather than hallucinating.

This is not a prompt problem. It is a fundamental BM25 limitation that dense
retrieval (semantic embeddings) addresses directly.

---

## Working Examples (v1)

### Q1 — "What is displacement?" → correct
Retrieved ch_0040 which contains the textbook definition directly.

### Q5 — "What does the slope of a velocity-time graph represent?" → correct
Retrieved ch_0032 which contains the exact phrasing from the textbook.

### Q16 — "Who is the Prime Minister of India?" → correct refusal
Retriever returned motion chunks with no relevant content, model refused cleanly.

### Q18 — "Explain nuclear fission using the concepts from this chapter." → correct refusal
This is the tricky out-of-scope case. Retriever returned equation chunks (keyword
overlap on "energy", "equations") but the grounding prompt correctly refused because
nuclear fission was not present in the context. This is the most important passing case.
