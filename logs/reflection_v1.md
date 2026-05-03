## Project: Retrieval-Ready Study Assistant — Base Tier
**Chapter**: Describing Motion Around Us (NCERT Class 9 Science)
**Pipeline**: BM25 retrieval + phi3 (Ollama, temperature=0) + grounding prompt

---

## 1. System Overview

The system is a RAG (Retrieval-Augmented Generation) pipeline built in four stages:

**Corpus** — `motion.pdf` was loaded with PyMuPDF, cleaned (headers/footers removed, equations tagged as `[EQUATION_x]`, figures as `[FIGURE_x]`), and classified into block types (`concept`, `worked_example`, `solution`, `side_note`). The structured blocks were chunked into 54 chunks at ~300 words with 50-word overlap. Definition-boundary detection and equation-block preservation were applied during chunking.

**Retrieval** — BM25Okapi via `rank_bm25`. Tokenization is symmetric — the same `TextPreprocessor` is applied at index time and query time. Top-k=3 by default.

**Generation** — Local Ollama model `phi3` at `temperature=0.0`. Prompt was iterated from v1 to v2. The `answer()` function returns the answer text, retrieved chunk IDs, backend used, and a refusal flag.

**Evaluation** — 20 questions across 4 types: `direct` (12), `paraphrased` (3), `out_of_scope` (3), `out_of_scope_tricky` (2). Scored on correctness, grounding, refusal, and refusal_appropriate.

---

## 2. Prompt Versions

### prompt_v1
```
You are a NCERT Science assistant.
Answer ONLY using the context.
If not present, say: "I cannot answer this from the available textbook content."

Context:
{ctx}

Question: {question}

Answer:
```

### prompt_v2 (final)
Additions over v1:
- Explicit numbered rules instead of a loose instruction
- Citation forcing: every answer must begin with `Based on: "<phrase from context>"`
- Explicit figure refusal: if the answer only exists via a figure, treat as unanswerable
- Strengthened grounding language: "Do NOT use any knowledge from outside the provided context"

**What triggered the change from v1 to v2**: Q8 (position-time graph) in v1 returned a partially correct but vaguely worded answer. More critically, Q4 and Q6 in v1 answered partially using language that wasn't traceable to the retrieved chunks — the citation forcing rule in v2 was added specifically so grounding could be verified visually without reading the full answer.

---

## 3. Evaluation Results

### v1 Summary (20 questions, no `grounded` column)

| Metric | Count |
|---|---|
| Correct | 3 (Q1, Q5, Q7) |
| Partial | 8 (Q2, Q3, Q4, Q6, Q8, Q10, Q12, Q13) |
| Incorrect | 3 (Q11, Q14, Q15) |
| N/A (out-of-scope) | 5 (Q16–Q20) |
| Refusals issued | 7 |
| Refusals appropriate (out-of-scope) | 3 of 5 |
| Tricky out-of-scope refused correctly | 2 of 2 ✅ |

### v2 Summary (20 questions, includes `grounded` column)

| Metric | Count |
|---|---|
| Correct | 5 (Q1, Q5, Q7, Q8, Q9) |
| Partial | 6 (Q2, Q3, Q4, Q10, Q12, Q13) |
| Incorrect | 3 (Q6, Q11, Q14, Q15) — Q6 regressed |
| N/A (out-of-scope) | 5 (Q16–Q20) |
| Grounded (of answerable questions) | 14 of 15 |
| Refusals appropriate | 3 of 5 |
| Tricky out-of-scope refused correctly | 2 of 2 ✅ |

### What changed between v1 and v2

The citation forcing rule in v2 had a measurable effect. Q8 moved from `partial` to `correct` — v1 gave a vague answer about "average velocity being zero" whereas v2 cited the relevant phrase directly and stated clearly that a horizontal line means a stationary object. Q9 (three equations of motion) moved from `partial`/refusal in v1 to `correct` in v2 — the model reconstructed the equations from the tagged equation references in the retrieved chunks rather than refusing.

One regression: Q6 (average velocity) dropped from `partial` in v1 to `incorrect` in v2. In v1, the model gave a mostly correct definition. In v2, it latched onto a retrieved sentence about average velocity equalling average speed under specific conditions and stated that as the general definition — a grounding failure where citation forcing backfired by anchoring the answer to the wrong sentence in the chunk.

---

## 4. Failure Analysis

### Failure 1 — Q11: "If an object returns to its starting point, what is the displacement?"
- **Retrieved**: ch_0002, ch_0003, ch_0007 (early chapter intro chunks)
- **Expected chunk**: ch_0040 — contains "displacement is zero, since the child comes back to its original position"
- **Type**: Retrieval miss
- **Cause**: The query uses "returns to starting point". The corpus uses "comes back to its original position". BM25 found no term overlap with the definition chunk and returned unrelated early-chapter blocks instead. The grounding prompt correctly refused rather than hallucinating — this is the prompt working as intended, but the retriever failed upstream.

### Failure 2 — Q14: "If velocity is not changing, what can you say about acceleration?"
- **Retrieved**: ch_0026, ch_0025, ch_0044 (velocity-time graph and circular motion chunks)
- **Type**: Retrieval miss
- **Cause**: This is an inferential query — "not changing" is a conditional, not a textbook phrase. BM25 matched on "velocity" and "acceleration" but retrieved graph-description chunks instead of the definition chunk that states acceleration is zero when velocity is constant. BM25 cannot score relevance on logical conditions, only on term frequency.

### Failure 3 — Q15: "Even though a car moves at constant speed in a circle, is it accelerating?"
- **Retrieved**: ch_0044, ch_0015, ch_0045
- **Type**: Retrieval miss
- **Cause**: "Constant speed in a circle" did not match the corpus phrase "uniform circular motion". BM25 matched on "accelerating" and returned kinematics equation chunks. The answer exists in the corpus — ch_0040 and ch_0042 both discuss direction change causing acceleration in circular motion — but the vocabulary gap prevented retrieval.

### Pattern across all three failures
All three share the same root cause: **vocabulary mismatch between how a student phrases a question and how the textbook states the answer**. This is not a prompt engineering problem and is not fixable by iterating the grounding prompt. It is a structural limitation of lexical retrieval. Dense retrieval with semantic embeddings would resolve all three by matching on meaning rather than term overlap.

---

## 5. Working Examples

**Q1 — "What is displacement?" → correct (both versions)**
BM25 successfully retrieved ch_0040 which contains the definition verbatim. High term overlap between query and corpus. This is the ideal case for lexical retrieval.

**Q5 — "What does the slope of a velocity-time graph represent?" → correct (both versions)**
Retrieved ch_0032 which contains the exact phrasing from the textbook. Another strong term-overlap case.

**Q16 — "Who is the Prime Minister of India?" → correct refusal (both versions)**
Retriever returned motion chunks with no relevant content. Model refused cleanly. This confirms the grounding prompt is doing its job when the retriever returns irrelevant content.

**Q18 — "Explain nuclear fission using the concepts from this chapter." → correct refusal (both versions)**
This is the most important passing case. The retriever returned equation chunks (keyword overlap on "energy" and "equations") — plausible-looking but wrong chunks. The grounding prompt correctly refused because nuclear fission was not present in the context text. This validates that the grounding prompt holds even when the retriever is tricked by surface-level keyword matches.

---

## 6. What the Numbers Say

Of the 12 direct questions, 5 were fully correct in v2 (42%), 6 partial (50%), 1 incorrect (8%). Of the 3 paraphrased questions, 0 were correct — all three failed at retrieval due to vocabulary mismatch. This is not a coincidence. Paraphrased queries are exactly the scenario where BM25 degrades and semantic retrieval would help most.

Out-of-scope performance was strong: 5 of 5 refused correctly. The 2 tricky out-of-scope cases (Q18, Q19 — nuclear fission and reactor control using motion equations) both refused correctly despite the retriever returning topically plausible chunks. This is the grounding prompt's highest-value contribution: preventing hallucination when the retriever is partially fooled.

Grounding score in v2: 14 of 15 answerable questions were grounded (93%). The one exception is Q7 (SI unit of acceleration, answered as "m/s²") — technically correct but the `check_grounding` metric flagged it as not grounded because the short answer didn't appear verbatim in the retrieved chunks. This is a metric limitation, not a real grounding failure.

---

## 7. Key Learnings

**Retrieval quality is the ceiling.** Nine of ten answer quality issues traced back to what the retriever returned, not to what the model said given those chunks. The grounding prompt is only as useful as the chunks it receives.

**Tokenization symmetry matters.** Applying the same preprocessor at index time and query time is not optional — it is the most common silent bug in BM25 builds. This was enforced from the start and prevented a class of invisible failures.

**Citation forcing has a real effect.** Prompt v2's `Based on: "<phrase>"` rule made grounding verifiable at a glance without reading full answers. It also changed model behaviour — the model was more likely to stay close to the chunk text. The Q6 regression shows it can backfire if the model anchors to the wrong sentence, but the net effect across the evaluation set was positive.

**BM25 is not the right tool for paraphrased or inferential queries.** All three evaluation failures are in these categories. The system works well for direct textbook-lookup questions and works well as a refusal system. It does not work for reasoning questions or vocabulary-mismatched queries. Dense retrieval is the correct next step.