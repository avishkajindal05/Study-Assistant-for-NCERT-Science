from src.pipeline.qa_pipeline import QAPipeline

if __name__ == "__main__":
    qa = QAPipeline()
    q = "What is displacement?"
    out = qa.answer(q)
    print("\nAnswer:\n", out["answer"])
    print("\nChunks:\n", out["retrieved_chunk_ids"])