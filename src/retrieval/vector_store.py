# src/retrieval/vector_store.py
import json
import requests
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from src.utils.config import CFG

COLLECTION_NAME = "ncert_motion_wk10"


class OllamaEmbeddingFunction(EmbeddingFunction):
    """Chroma-compatible embedding function using Ollama nomic-embed-text."""

    def __init__(self, model: str = "nomic-embed-text", url: str = "http://localhost:11434/api/embeddings"):
        self.model = model
        self.url = url

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": text},
                timeout=60
            )
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        return embeddings


def get_collection():
    """Returns the Chroma collection, embedding only if it doesn't exist yet."""
    client = chromadb.PersistentClient(path="./chroma_wk10")

    embedding_fn = OllamaEmbeddingFunction(
        model=CFG.EMBED_MODEL,
        url=CFG.OLLAMA_EMBED_URL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    if collection.count() == 0:
        print("Collection empty — embedding chunks...")
        _embed_chunks(collection, embedding_fn)
    else:
        print(f"Collection already has {collection.count()} chunks — skipping embed.")

    return collection


def _embed_chunks(collection, embedding_fn):
    with open(CFG.CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "content_types": str(c.get("content_types", [])),
            "has_equation": str(c.get("has_equation", False)),
            "token_count": c.get("token_count", 0),
            "page": str(c.get("page", "")),
            "source": c.get("source", "motion.pdf"),
            "section": c.get("section", "unknown")
        }
        for c in chunks
    ]

    # Embed in batches of 10 — Ollama is sequential, small batches keep it stable
    batch_size = 10
    for i in range(0, len(chunks), batch_size):
        batch_end = min(i + batch_size, len(chunks))
        collection.add(
            ids=ids[i:batch_end],
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end]
        )
        print(f"  Embedded {batch_end}/{len(chunks)} chunks")

    print(f"Done — {collection.count()} chunks persisted.")


def retrieve(query: str, k: int = 5):
    """Returns top-k chunks with similarity scores."""
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": round(1 - results["distances"][0][i], 4)
        })

    return hits