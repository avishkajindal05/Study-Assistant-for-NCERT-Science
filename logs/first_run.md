# 🧪 RUN REPORT — NCERT Study Assistant

## 📥 Input

- File: `motion.pdf`
- Chapter: *Describing Motion Around Us*

---

## 🧹 Cleaning Stage

### Operations performed:
- Removed repetitive headers and footers (e.g., page titles, page numbers)
- Normalized whitespace and fixed broken word splits
- Standardized equation and figure references (e.g., `(4.2a)` → `[EQUATION_4.2a]`, `Fig. 4.4` → `[FIGURE_4.4]`)

### Result:
- Text is cleaner and more consistent for downstream processing
- Scientific expressions, equations, and references are preserved (not removed)

---

## 🧱 Structuring Stage

Text blocks were labeled using rule-based heuristics:

| Type            | Description |
|-----------------|------------|
| concept         | Explanatory paragraphs |
| worked_example  | Example-based explanations |
| solution        | Solution sections |
| side_note       | Marginal or auxiliary notes |

### Observations:
- Side notes were detected using layout (bbox width) and merged into adjacent content
- Some blocks may still contain mixed content due to PDF extraction limitations

---

## ✂️ Chunking Stage

Chunking strategy used:

- Sequential block-based processing
- Fixed-size constraint (~300 words)
- Overlap of ~50 words between consecutive chunks
- Rule-based preservation:
  - Worked examples and solutions are not split
  - Equation-containing blocks are kept intact

### Output:
- Total chunks created: **(actual number from run)**
- Each chunk contains:
  - Combined text from multiple structured blocks
  - Metadata flags (`has_equation`, `has_figure`, `content_types`)

### Observations:
- Chunk boundaries are not strictly semantic; they depend on block order and size limits
- Overlap helps mitigate boundary fragmentation but introduces redundancy

---

## 🔍 Retrieval Stage

Query:
What is displacement?


### Retrieved Chunks (Top-3):
- Chunk IDs: `['ch_0039', 'ch_0027', 'ch_0044']`  ← (replace with actual output)

### Observations:
- Retrieved chunks include:
  - Definition-related content
  - Example involving distance vs displacement
- Retrieval is based purely on lexical matching (BM25)
- Ranking depends on token overlap, not semantic similarity

---

## 🤖 Generation Stage

- Model: `phi3` (Ollama, CPU mode)
- Temperature: 0 (deterministic)
- Prompt: grounded, restricted to retrieved context

### Behavior:
- Model generates answer using only provided chunks
- No external knowledge is injected

---

## ✅ Final Answer Generated

**Question:** What is displacement?

**Answer:**

Answer:
 Displacement refers to the change in position of an object. It's a vector quantity, which means it has both magnitude (how far) and direction from its starting point to its final position. Displacement can be different from distance traveled if there is a change in direction during travel; for example, returning back to the original position results in zero displacement despite having covered significant ground.

Chunks:
 ['ch_0039', 'ch_0027', 'ch_0044']
---

## 📊 Observations

- Retrieval returned relevant but partially redundant chunks
- Answer is consistent with textbook definition
- Output correctness depends heavily on retrieval quality
- No explicit verification mechanism ensures full grounding

---

## ⚠️ Limitations

- BM25 cannot handle semantic paraphrasing effectively
- Chunking is heuristic-based and may not align with true conceptual boundaries
- PDF extraction noise can propagate into chunks
- No confidence scoring or answer verification step

---

## 🚀 Conclusion

The system successfully demonstrates a working RAG pipeline:

- Structured extraction from textbook PDF
- Retrieval using lexical matching
- Grounded answer generation using a local LLM

However, system performance is primarily constrained by:
- Retrieval quality
- Chunking strategy
- Lack of semantic understanding in retrieval