# Updated Implementation Plan: Retrieval-Ready Study Assistant (Base Tier)

This document outlines the architecture, toolchain, and implementation strategy for the **Base** tier of PariShiksha's Retrieval-Ready Study Assistant for NCERT Science.

## Goal Description
The objective is to build a foundational, bounded study assistant that answers NCERT Class 9/10 Science questions reliably. The system must remain perfectly grounded in the provided textbook content to maintain the trust of parents and students. We will implement the Base tier comprising Corpus Extraction, Retrieval, Generation, and Evaluation stages.

## User Review Required
> [!NOTE]
> - "Motion" (Chapter 8) will be used as the primary corpus due to formula density.
> - Local Ollama (`llama3.2`, `mistral`, or `gemma2`) will be the **primary** LLM backend.
> - **Gemini free tier (`google-generativeai`) is the designated fallback** — set up the API key on Day 1 so it is ready instantly if Ollama causes time loss mid-week.
> - If switching to Gemini fallback, log the switch in your git commit message so eval results stay traceable.

## Open Questions
- None.

---

## Pipeline Architecture & Justification

### 1. Corpus Processing & Extraction
**Libraries**: `pymupdf` (fitz)
**Alternatives**: `pdfplumber` (slower, better table extraction — try if PyMuPDF gives garbled output on a specific page)

**Justification**: PyMuPDF is fast and exposes text block bounding boxes and font metadata, which is critical for detecting headers and separating content types without relying on pure keyword heuristics.

**Handling Messy Extraction**:
- **Formulas & Mojibake**: Run a post-extraction regex pass to flag chunks with a low alphabetic ratio (e.g., less than 60% alphabetic characters) or consecutive special characters. Tag these `content_type: formula_adjacent` so evaluation can isolate formula-driven failures from reasoning failures — these are two different problems.
- **Section Boundaries**: Use font size and boldness metadata from PyMuPDF blocks to detect section headers rather than relying on newlines alone.
- **Content Type Splitting**: Apply keyword-prefix heuristics — `"Example"`, `"Solution"`, `"Exercises"`, `"Q."` — to split the flat extracted stream into concept paragraphs, worked examples, and end-of-chapter questions. Assign each chunk a `content_type` field: `concept`, `worked_example`, `exercise`.
- **Dangling References**: Flag chunks containing phrases like "as shown in Figure" or "refer to diagram" — these reference images you don't have. Tag them `content_type: figure_dependent` so you know not to rely on them for grounded answers.

**Important**: After extraction, print a 5-chunk sample before writing any retrieval code. Confirm what the raw text actually looks like. A submission that says "the corpus was clean" failed this step.

---

### 2. Tokenization & Chunking Logic
**Libraries**: `transformers`, `tokenizers`

**Tokenizer Comparison**:
Compare all three on **5 representative passages** — pick passages that contain science-specific terms like `specific-heat-capacity`, `photosynthesis`, `velocity-time`, and worked example boundaries. For each passage record:
- Token count per tokenizer
- Where boundaries disagree (show this visually in the notebook, not just as a count table)
- How each handles hyphenated scientific terms specifically

The three tokenizers to compare:

| Tokenizer | Model | Key behavior to note |
|---|---|---|
| GPT-2 BPE | `gpt2` | Byte-level, handles unknown chars gracefully |
| BERT WordPiece | `bert-base-uncased` | Splits on `##` subwords, lowercases |
| T5 SentencePiece | `t5-small` | Unigram LM, handles whitespace differently |

**Chunking Strategy**:
- Start with `chunk_size=300` tokens, `overlap=50` tokens as the baseline
- **Critical**: before finalising chunk size, manually inspect your content and identify which semantic units must stay together — specifically worked examples and their solutions. A chunk boundary between an example setup and its solution is one of the most common retrieval bugs and the expert hints call it out directly.
- Use `RecursiveCharacterTextSplitter` logic — split on paragraph breaks first, then sentences, then words. Never split mid-sentence as the default.
- Store a `chunk_index` field (position in document) in metadata to resolve retrieval ties and help with debugging.

**Metadata per chunk** (enforce this schema from the start):

```
{
  "chunk_id": "ch08_012",
  "chapter": "Motion",
  "section": "8.3 Rate of Change of Velocity",
  "content_type": "concept | worked_example | exercise | formula_adjacent | figure_dependent",
  "chunk_index": 12,
  "token_count": 287
}
```

---

### 3. Retrieval Engine
**Libraries**: `rank_bm25`
**Alternatives**: Scikit-Learn `TfidfVectorizer` (use only if rank_bm25 gives installation issues)

**Justification**: BM25 handles variable-length chunks better than raw TF-IDF through term frequency saturation and document length normalisation — important because your chunks will vary significantly in length between a short exercise question and a long concept paragraph.

**Key implementation rules**:
- **Tokenization symmetry is non-negotiable**: the preprocessing applied to corpus chunks at index time must be identical to the preprocessing applied to queries at retrieval time. Use the same lowercasing, same punctuation handling, same tokenizer. Document this explicitly in code comments. This is the most common silent bug in first-time BM25 builds.
- Return top-k=3 chunks by default. Make k a parameter so you can experiment during evaluation without touching retrieval logic.
- Always print retrieved chunks for any failing query before touching the prompt or changing the model. Nine out of ten hallucinations trace back to a retrieval miss, not a model problem.
- Test retrieval on at least 3 questions before moving to generation. Confirm chunks are relevant by eye.

---

### 4. Grounded Generation & Anti-Hallucination Strategy

**Primary**: Local Ollama (`llama3.2`, `mistral`, or `gemma2`)
**Fallback**: Gemini free tier (`google-generativeai`) — **set this up on Day 1**

**Switching rule**: if Ollama setup costs more than 45 minutes, or if `temperature=0` output is non-deterministic across identical runs, switch to Gemini immediately and log it. Do not debug Ollama at the cost of your evaluation time.

**Gemini fallback setup** (do this on Day 1 regardless):
```python
# generator.py — keep both backends, switch via config flag
LLM_BACKEND = "ollama"  # switch to "gemini" if needed

if LLM_BACKEND == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
```

**Grounding Prompt — v1 starting point**:
```
You are a study assistant for NCERT Class 9 Science.
You must answer the question using ONLY the context provided below.
If the answer is not contained within the context, respond with exactly:
"I cannot answer this from the available textbook content."
Do not use any knowledge outside of the provided context.

Context:
{context}

Question: {question}

Answer:
```

**Iteration rule**: change one thing at a time between prompt versions. Commit after each change. Your git log becomes your experiment log. The reflection questionnaire asks for your v1 and v-final prompt with the specific query that caused each revision — you cannot reconstruct this at the end if you didn't log it.

**Citation forcing** (add to prompt after v1 baseline):
Once v1 baseline is measured, add: *"If you answer, begin with: 'Based on: [brief quote from context]'"* — this makes grounding evaluation much faster since you can verify it visually without reading the full answer.

**Additional rules**:
- `temperature=0.0` always during evaluation — if your local model doesn't respect this consistently across identical runs, that is your Ollama → Gemini switch trigger
- Every `answer()` call must return both the answer text and the retrieved chunk IDs so you can distinguish retrieval misses from generation errors during evaluation

**answer() function signature**:
```python
def answer(question: str) -> dict:
    return {
        "answer": str,
        "retrieved_chunk_ids": list[str],
        "retrieved_chunks": list[str],
        "backend_used": "ollama" | "gemini",
        "refusal": bool
    }
```

---

### 5. Evaluation Setup
**Libraries**: `pandas`

**Question set structure** (15–20 questions):

| Type | Count | Notes |
|---|---|---|
| Direct textbook | 10–12 | Lifted or near-lifted from the chapter |
| Paraphrased | 2–3 | Same concept, different wording |
| Out-of-scope (easy) | 2–3 | "Who is the PM of India?" — retriever returns nothing relevant |
| Out-of-scope (tricky) | 1–2 | "Explain nuclear fission using Class 9 concepts" — retriever returns Motion content with keyword overlap, grounding prompt must still refuse |

The tricky out-of-scope questions are the ones that matter most. Include at least one. This is where weak grounding prompts fail.

**Evaluation table columns**:
```
question | question_type | retrieved_chunk_ids | answer | correct | grounded | refusal_appropriate | notes
```

**Scoring axes**:
- `correct`: yes / partial / no
- `grounded`: is the answer supported by the retrieved chunks (yes/no)
- `refusal_appropriate`: for out-of-scope only — did the system refuse correctly (yes/no)

**Failure analysis rule**: identify 3 working examples and 2 failing examples. For each failure, one sentence on probable cause — trace it to either a retrieval miss or a generation error, not just "the model got it wrong."

**Prompt iteration logging**: every time you change the grounding prompt, re-run the full eval set and save results with a version suffix (`evaluation_results_v1.csv`, `evaluation_results_v2.csv`). Never overwrite.

---

## Module Breakdown

### Study-Assistant-for-NCERT-Science

#### [NEW] `src/corpus_processor.py`
PDF reading, font-based heuristics for content type detection, chunking with overlap, tokenizer comparison script. Outputs chunk store as a list of dicts with full metadata schema.

#### [NEW] `src/retriever.py`
BM25 chunk store with explicit tokenization symmetry enforcement. Top-k retrieval with configurable k. Prints retrieved chunks to stdout for debugging.

#### [NEW] `src/generator.py`
Dual-backend integration (Ollama primary, Gemini fallback) controlled by a single config flag. Grounding prompt versioning. Returns full `answer()` dict including chunk IDs and backend used.

#### [NEW] `src/evaluator.py`
Standalone evaluation loop — runs the full question set, scores on three axes, outputs versioned CSV. Can be re-run independently without re-running notebook stages.

#### [NEW] `notebook.ipynb`
Main driver that ties all stages together. Includes tokenizer boundary visualisation (not just count tables), retrieval spot-checks, and evaluation results display.

---

## Day-by-Day Pacing

| Day | Focus | Exit condition |
|---|---|---|
| Day 1 | Environment setup, PDF extraction, 5-chunk sanity check, Gemini API key ready | Raw chunks printed, content types visible, Gemini key tested |
| Day 2 | Tokenizer comparison + chunking strategy finalised | Boundary disagreement visualised in notebook, chunk schema locked |
| Day 3 | BM25 retriever built and spot-checked on 3 questions | Retrieved chunks confirmed relevant by eye |
| Day 4 | Generator integrated, v1 grounding prompt tested | `answer()` function callable, refusal working on one out-of-scope |
| Day 5 | Full evaluation set run, failures traced, prompt iterated | evaluation_results_v1.csv saved, 2 failures analysed |
| Day 6 | Reflection questionnaire written from actual results | reflection.md complete with real numbers and real prompt versions |
| Day 7 | Buffer — fix anything that broke, clean notebook, submit | Notebook runs end-to-end on fresh clone |

---

## Verification Plan

### Automated
- Full evaluation loop run against 15–20 question set
- Out-of-scope questions verified to produce explicit refusals, not hallucinated answers
- Versioned CSV output confirmed for each prompt iteration

### Manual
- 5-chunk sample printed and inspected after extraction before any retrieval code is written
- Retrieved chunks printed and confirmed relevant for 3 spot-check questions before generation is added
- 2 failure cases traced explicitly to retrieval miss vs generation error
- Notebook confirmed to run end-to-end on a fresh clone before submission (this is a pass/fail gate in the rubric)

---

## Submission Hygiene Checklist
- [ ] `README.md` with setup instructions and NCERT source link (PDF not committed)
- [ ] `notebook.ipynb` runs end-to-end on fresh clone
- [ ] `evaluation_results.md` or `.csv` present
- [ ] `reflection.md` complete with real numbers
- [ ] At least 3 intermediate commits in git history
- [ ] `.env` in `.gitignore` — API keys never committed
