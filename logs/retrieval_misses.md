# retrieval_misses.md

## Top-1 Retrieval Hit Rate

2/10 questions returned the correct chunk as top-1 (dense retrieval,
nomic-embed-text, Chroma cosine similarity, k=5).

## Three Misses

### Miss 1 — Q2
- **Top-1 returned:** ch_0032 (score: 0.7727)
- **Expected chunk:** ch_0024
- **Diagnosis:** retrieval ranking + semantic confusion  
  The query likely required understanding a specific physics concept, but the retrieved chunk shares overlapping terms (e.g., motion or graph-related terminology) without actually containing the answer. The embedding model prioritized general similarity rather than precise conceptual relevance, causing the correct chunk to be ranked lower.

---

### Miss 2 — Q3
- **Top-1 returned:** ch_0059 (score: 0.8595)
- **Expected chunk:** ch_0029
- **Diagnosis:** embedding limitation (paraphrase / inference)  
  The query involves reasoning (e.g., linking velocity and acceleration), while the correct chunk likely expresses the concept more explicitly. The embedding model failed to capture this inferential relationship and instead retrieved a chunk with higher lexical similarity but weaker conceptual alignment.

---

### Miss 3 — Q4
- **Top-1 returned:** ch_0026 (score: 0.7452)
- **Expected chunk:** ch_0024
- **Diagnosis:** synonym mismatch  
  The query uses student-style phrasing, while the textbook uses more formal terminology. The retrieved chunk likely contains overlapping keywords but in a different conceptual context. This mismatch between query phrasing and textbook language caused the embedding model to retrieve a semantically adjacent but incorrect chunk.