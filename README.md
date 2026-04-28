# 📘 NCERT Science Study Assistant (RAG Pipeline)

## 🚀 Overview
This project implements a **Retrieval-Augmented Generation (RAG)** pipeline to answer questions from NCERT Science textbooks.

The system processes a PDF chapter, cleans and structures the content, splits it into semantic chunks, retrieves relevant context using BM25, and generates answers using an LLM (Ollama - phi3).

---

## 📂 Project Structure
```bash
Study-Assistant-for-NCERT-Science/
│
├── data/
│   ├── raw/                         # NCERT PDFs (not committed)
│   ├── processed/                   # cleaned text
│   └── chunks/
│       └── chunks.json              # final structured chunks
│
├── src/
│   ├── corpus/
│   │   ├── pdf_loader.py
│   │   ├── cleaner.py
│   │   ├── structure_parser.py      # detects examples, figures, equations
│   │   └── chunker.py
│   │
│   ├── retrieval/
│   │   ├── bm25_retriever.py
│   │   └── preprocessing.py         # tokenization symmetry
│   │
│   ├── generation/
│   │   ├── base_llm.py
│   │   ├── ollama_client.py
│   │   ├── gemini_client.py         # fallback
│   │   └── prompt.py
│   │
│   ├── pipeline/
│   │   └── qa_pipeline.py
│   │
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   ├── metrics.py
│   │   └── question_set.json
│   │
│   ├── utils/
│   │   ├── config.py
│   │   └── logger.py
│
├── notebooks/
│   └── notebook.ipynb
│
├── results/
│   ├── evaluation_results_v1.csv
│   ├── evaluation_results_v2.csv
│   └── logs/
│
├── prompts/
│   ├── prompt_v1.txt
│   └── prompt_v2.txt
│
├── reflection.md
├── README.md
├── requirements.txt
└── main.py
```

---

## ⚙️ Pipeline Architecture

### 1️⃣ PDF Extraction
- Input: NCERT PDF
- Output: Raw text with layout preserved (font, bbox, page)

---

### 2️⃣ Cleaning
- Removed:
  - Headers / footers
  - Page numbers
  - Noise (Grade labels, notes)
- Preserved:
  - Core scientific content
  - Paragraph structure

---

### 3️⃣ Structuring
Text is converted into structured blocks:
- `concept`
- `worked_example`
- `equation`
- `note`

Example:
> Motion is defined as change in position of an object with time :contentReference[oaicite:0]{index=0}

---

### 4️⃣ Chunking
- Semantic chunking with overlap
- Chunk size: ~200–300 words
- Maintains context continuity

---

### 5️⃣ Retrieval (BM25)
- Tokenization + preprocessing
- Top-K chunks selected for query

---

### 6️⃣ Generation (LLM)
- Model: **Ollama (phi3)**
- Grounded prompt:
  - Uses only retrieved chunks
  - Avoids hallucination

---

## 🧠 Features

- Context-aware answering
- Structured knowledge extraction
- Lightweight (no heavy embeddings required)
- Fully local pipeline

---

## 📊 Example Topics Covered

From NCERT Chapter: *Describing Motion Around Us*

- Linear motion
- Reference point
- Distance vs Displacement
- Average speed
- Average velocity

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python main.py
```

---
## 📌 Future Improvements
Add vector embeddings (FAISS)
Hybrid retrieval (BM25 + semantic)
UI (Streamlit)
Multi-chapter support

---

## 👨‍💻 Author

Avishka Jindal — PG Diploma (2026) + BTech AI/ML (2022–2026)

---