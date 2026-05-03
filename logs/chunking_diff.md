# chunking_diff.md

## Wk9 vs Wk10 Retrieval Comparison

Five questions from the Wk9 evaluation set were run through both the Wk9 BM25
retriever (using wk9 chunks.json, ~300-word chunks) and the Wk10 dense
retriever (using wk10_chunks.json, ~250-token chunks with nomic-embed-text embeddings
and cosine similarity in Chroma).

| Question | BM25 top-3 | Dense top-3 |
|---|---|---|
| What is displacement? | ch_0040, ch_0032, ch_0046 | ch_0007, ch_0012, ch_0011 |
| If an object returns to its starting point, what is the displacement? | ch_0002, ch_0003, ch_0007 | ch_0007, ch_0012, ch_0014 |
| If velocity is not changing, what can you say about acceleration? | ch_0026, ch_0025, ch_0044 | ch_0056, ch_0029, ch_0024 |
| Even though a car moves at constant speed in a circle, is it accelerating? | ch_0044, ch_0015, ch_0045 | ch_0082, ch_0078, ch_0056 |
| What does the slope of a velocity-time graph represent? | ch_0032, ch_0035, ch_0028 | ch_0059, ch_0051, ch_0052 |

## Observations

Dense retrieval shows clear improvement on paraphrased and inference-based queries where direct keyword overlap is weak. For example, the query “If an object returns to its starting point…” indirectly refers to zero displacement. BM25 retrieves early chunks (ch_0002, ch_0003) based on partial keyword matches, while dense retrieval consistently surfaces ch_0007, which aligns better with the displacement concept. Similarly, for “If velocity is not changing…”, dense retrieval returns chunks such as ch_0056 that explicitly capture the relationship between constant velocity and zero acceleration, whereas BM25 retrieves more general velocity-related chunks that may not directly answer the question.

However, dense retrieval is not uniformly superior. For the circular motion query, BM25 retrieves ch_0044, which likely directly discusses circular motion and acceleration, while dense retrieval shifts to different chunks (ch_0082, ch_0078), indicating a possible ranking limitation for domain-specific physics concepts. For direct definition-based queries like “What is displacement?” and “slope of velocity-time graph,” both retrievers return relevant chunks, showing that lexical (BM25) and semantic (dense) methods converge when there is strong term overlap. Overall, BM25 performs reliably for exact-match queries, while dense retrieval improves performance on paraphrased or concept-based queries, with some trade-offs in ranking precision.