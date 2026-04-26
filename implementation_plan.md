# Implementation Plan: Retrieval-Ready Study Assistant (Base Tier)

This document outlines the architecture, toolchain, and implementation strategy for the **Base** tier of PariShiksha's Retrieval-Ready Study Assistant for NCERT Science.

## Goal Description
The objective is to build a foundational, bounded study assistant that answers NCERT Class 9/10 Science questions reliably. Crucially, the system must remain perfectly grounded in the provided textbook content to maintain the trust of parents and students. We will implement the Base tier comprising Corpus Extraction, Retrieval, Generation, and Evaluation stages.


## Pipeline Architecture & Justification

### 1. Corpus Processing & Extraction
**Libraries**: `pymupdf` (fitz)
**Alternatives**: `pdfplumber` (slower, but better table extraction)
**Justification**: `pymupdf` is fast and provides excellent text block bounding box and font information, which is critical for identifying headers and separating concept paragraphs from examples.

**Handling Messy Extraction**:
- **Formulas & Mojibake**: PDFs often render complex formulas as mojibake. After extraction, we will run a quick regex-based pass to detect and tag chunks containing likely formula fragments (e.g., consecutive special characters or very low alphabetic ratio). We will tag these with `content_type: formula_adjacent` so evaluation can separate formula-driven failures from others.
- **Section Boundaries**: We will utilize font properties (boldness, size) extracted by PyMuPDF to detect section headers.
- **Content Splitting**: Heuristics based on keyword prefixes (e.g., "Example", "Solution", "Exercises") will separate concept paragraphs, worked examples, and end-of-chapter questions.

### 2. Tokenization & Chunking Logic
**Libraries**: `transformers`, `tokenizers`
**Strategy**: We will compare GPT-2 BPE, BERT WordPiece, and T5 SentencePiece tokenizers. We will chunk text with an explicit overlap to ensure worked examples are not severed from their solutions.

### 3. Retrieval Engine
**Libraries**: `rank_bm25`
**Alternatives**: Scikit-Learn `TfidfVectorizer`
**Justification**: BM25 is superior to basic TF-IDF as it handles varying document lengths better and saturates term frequencies, which is vital for chunks of differing lengths (e.g., short examples vs. long paragraphs). As per the "Base" tier, we will stick to lexical search to ensure token alignment and avoid black-box embedding issues early on.

**Key Considerations**:
- **Tokenization Symmetry**: We must ensure query preprocessing perfectly matches corpus preprocessing (e.g., lowercasing and simple word tokenization). We will explicitly document and enforce this in code.
- **Metadata**: Each chunk will include `chunk_index` (position in document) to help resolve ties when two chunks are equally relevant.

### 4. Grounded Generation & Anti-Hallucination Strategy
**Libraries**: `ollama` (local LLM, preferring `llama3.2`, `mistral`, or `gemma2`)
**Alternatives**: `google-generativeai` (Gemini), `openai`
**Justification**: Running a local LLM via Ollama provides complete control and privacy. The chosen models (`llama3.2`, `mistral`, or `gemma2`) possess the necessary instruction-following capacity for strict grounding. We will explicitly test `temperature=0` behavior, as it varies by local model.

**Anti-Hallucination Strategy**:
- **Strict Grounding Prompt**: We will use a constraint-based prompt: *"You must answer the question using ONLY the provided context. If the answer is not contained within the context, you must refuse to answer. If you answer, begin your response with 'Based on: [brief quote or paraphrase from context]' before giving the full answer."* This explicitly forces citation, accelerating evaluation.
- **Zero Temperature**: We will use `temperature = 0.0` to ensure completely deterministic output, which is mandatory for reliable evaluations.
- **Transparency**: Every answer will explicitly return the retrieved chunks it was based on, allowing us to distinguish between retrieval misses and model hallucinations.

### 5. Evaluation Setup
**Libraries**: `pandas`
**Strategy**: A manually curated set of 15-20 questions (10-12 direct, 2-3 paraphrased, 3-5 out-of-scope). We will include at least one **"tricky out-of-scope" question** (e.g., "Explain nuclear fission using Class 9 concepts") to test the grounding constraint against retrieved keyword overlaps.
**Evaluation Table Structure**: Columns will be `question`, `question_type`, `retrieved_chunk_ids`, `answer`, `correct`, `grounded`, `refusal_appropriate`, and `notes` (for failure analyses).

## Module Breakdown

### Study-Assistant-for-NCERT-Science

#### [NEW] src/corpus_processor.py
Handles PDF reading, font-based heuristics for splitting headers/examples, and chunking with overlap. Implements the tokenizer comparison script.

#### [NEW] src/retriever.py
Implements the BM25 chunk store and provides top-k retrieval functions.

#### [NEW] src/generator.py
Integrates with the local Ollama backend, housing the strict grounding prompt and `temperature=0` constraints.

#### [NEW] src/evaluator.py
A standalone script to run the evaluation loop and output results, allowing iterative testing without re-running notebook stages.

#### [NEW] notebook.ipynb
The main driver notebook that ties all stages together, visualizes tokenizer differences, and runs the evaluation loop.

## Verification Plan

### Automated Tests
- We will execute the evaluation loop against the 15-20 question set.
- We will verify that out-of-scope questions result in an explicit refusal instead of a hallucinated answer.

### Manual Verification
- We will inspect 2 failure cases and trace them back to either the retrieval chunks or the generation prompt to categorize the error correctly.
