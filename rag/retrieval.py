import json
from pathlib import Path
from typing import Any

import faiss
from sentence_transformers import SentenceTransformer

from rag.config import EMBED_MODEL_NAME, INDEX_DIR


def build_faiss_index(chunks: list[dict[str, Any]], model_name: str = EMBED_MODEL_NAME):
    if not chunks:
        raise ValueError("Cannot build index: no chunks were generated.")

    model = SentenceTransformer(model_name)
    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    embeddings = embeddings.astype("float32")
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index, model


def save_index_and_metadata(
    index,
    chunks: list[dict[str, Any]],
    output_dir: str = INDEX_DIR,
    ingestion_report: dict[str, Any] | None = None,
) -> None:
    store_dir = Path(output_dir)
    store_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(store_dir / "faiss.index"))

    with open(store_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    if ingestion_report is not None:
        with open(store_dir / "ingestion_report.json", "w", encoding="utf-8") as f:
            json.dump(ingestion_report, f, ensure_ascii=False, indent=2)


def load_index_and_metadata(output_dir: str = INDEX_DIR):
    store_dir = Path(output_dir)
    index_path = store_dir / "faiss.index"
    chunks_path = store_dir / "chunks.json"

    if not index_path.exists() or not chunks_path.exists():
        raise FileNotFoundError(f"Missing index files in '{output_dir}'. Run: python main.py index")

    index = faiss.read_index(str(index_path))
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    model = SentenceTransformer(EMBED_MODEL_NAME)
    return index, chunks, model


def search(query: str, index, model, chunks: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        results.append(
            {
                "score": float(score),
                "filename": chunks[idx]["filename"],
                "section": chunks[idx]["section"],
                "content": chunks[idx]["content"],
            }
        )
    return results

