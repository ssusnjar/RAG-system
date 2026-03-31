from pathlib import Path
import argparse
import json
import os
import re
from typing import Any

import faiss
from sentence_transformers import SentenceTransformer

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from google import genai as google_genai
except ImportError:
    google_genai = None

if load_dotenv is not None:
    load_dotenv()

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gemini-2.5-flash"
INDEX_DIR = "rag_store"
SIMILARITY_THRESHOLD = 0.28


def looks_meaningful(text: str) -> bool:
    t = text.strip()
    if not t:
        return False

    words = re.findall(r"\b[A-Za-z]{2,}\b", t)

    if len(words) < 30:
        return False

    unique_words = len({w.lower() for w in words})
    diversity_ratio = unique_words / len(words)
    if diversity_ratio < 0.12:
        return False

    punct = len(re.findall(r"[^\w\s]", t))
    punct_ratio = punct / len(t)
    if punct_ratio > 0.20:
        return False

    return True


def load_documents():
    documents = []
    folder = Path("documents")

    for file in folder.glob("*.md"):
        text = file.read_text(encoding="utf-8")
        documents.append({"filename": file.name, "content": text})

    return sorted(documents, key=lambda d: d["filename"].lower())


def split_markdown_into_chunks(
    text: str,
    filename: str,
    chunk_size: int = 1000,
    overlap: int = 150,
):
    sections = re.split(r"(?m)(?=^#{1,3}\s)", text)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.splitlines()
        heading = lines[0] if lines and lines[0].startswith("#") else ""
        body = "\n".join(lines[1:]).strip() if heading else section
        section_text = (heading + "\n" + body).strip() if heading else body

        if len(section_text) <= chunk_size:
            if len(section_text) >= 120:
                chunks.append(
                    {
                        "filename": filename,
                        "section": heading.replace("#", "").strip(),
                        "content": section_text,
                    }
                )
            continue

        start = 0
        part = 1
        while start < len(section_text):
            end = min(start + chunk_size, len(section_text))
            piece = section_text[start:end].strip()

            if len(piece) >= 120:
                chunks.append(
                    {
                        "filename": filename,
                        "section": heading.replace("#", "").strip(),
                        "content": piece,
                        "part": part,
                    }
                )

            if end == len(section_text):
                break

            start = max(end - overlap, start + 1)
            part += 1

    return chunks


def filter_documents(documents: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    kept_docs = []
    filtered_docs = []
    for doc in documents:
        if looks_meaningful(doc["content"]):
            kept_docs.append(doc)
        else:
            filtered_docs.append(doc)
    return kept_docs, filtered_docs


def build_chunks(kept_docs: list[dict[str, str]]) -> list[dict[str, Any]]:
    all_chunks = []
    for doc in kept_docs:
        all_chunks.extend(split_markdown_into_chunks(doc["content"], doc["filename"]))
    return all_chunks


def build_faiss_index(chunks: list[dict], model_name: str = EMBED_MODEL_NAME):
    model = SentenceTransformer(model_name)
    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    embeddings = embeddings.astype("float32")

    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    return index, model


def save_index_and_metadata(index, chunks: list[dict], output_dir: str = INDEX_DIR):
    store_dir = Path(output_dir)
    store_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(store_dir / "faiss.index"))

    with open(store_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def load_index_and_metadata(output_dir: str = INDEX_DIR):
    store_dir = Path(output_dir)
    index_path = store_dir / "faiss.index"
    chunks_path = store_dir / "chunks.json"

    if not index_path.exists() or not chunks_path.exists():
        raise FileNotFoundError(
            f"Missing index files in '{output_dir}'. Run: python main.py index"
        )

    index = faiss.read_index(str(index_path))
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    model = SentenceTransformer(EMBED_MODEL_NAME)
    return index, chunks, model


def search(query: str, index, model, chunks: list[dict], top_k: int = 5):
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


def build_context(results: list[dict[str, Any]]) -> str:
    parts = []
    for i, r in enumerate(results, start=1):
        parts.append(
            (
                f"[{i}] file={r['filename']} | section={r['section']} | score={r['score']:.3f}\n"
                f"{r['content']}"
            )
        )
    return "\n\n".join(parts)


def generate_answer_with_llm(question: str, results: list[dict[str, Any]], model_name: str) -> str:
    if google_genai is None:
        raise RuntimeError("google-genai package is not installed. Run: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    client = google_genai.Client(api_key=api_key)
    context = build_context(results)

    system_prompt = (
        "You are a careful assistant answering questions strictly from provided internal documents. "
        "If information is missing or unclear in the provided context, explicitly say that the information "
        "is not available in the documents. Do not invent facts."
    )
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Context documents:\n{context}\n\n"
        "Instructions:\n"
        "1) Answer only using context.\n"
        "2) Keep answer concise and practical.\n"
        "3) If not found, clearly state it's not available in documents.\n"
        "4) Do NOT include a Sources line — sources are displayed separately.\n"
    )

    response = client.models.generate_content(
        model=model_name,
        contents=f"{system_prompt}\n\n{user_prompt}",
    )
    answer = response.text.strip()
    answer = re.sub(r"\n*Sources:.*$", "", answer, flags=re.DOTALL).strip()
    return answer


def _tokenize_for_match(text: str) -> list[str]:
    stopwords = {
        "the", "a", "an", "is", "are", "to", "of", "and", "or", "in", "on", "for",
        "with", "by", "be", "as", "at", "it", "this", "that", "from", "can", "must",
        "should", "during", "new", "employee", "document", "documents", "described",
        "what", "how", "when", "where", "which", "who", "does", "do", "according",
        "policy", "procedure", "procedures", "summarize", "summary", "reference",
    }
    tokens = re.findall(r"\b[a-z0-9]{2,}\b", text.lower())
    return [t for t in tokens if t not in stopwords]


def _pick_best_result_for_question(question: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    if len(results) == 1:
        return results[0]

    q_tokens = set(_tokenize_for_match(question))
    if not q_tokens:
        return results[0]

    best = results[0]
    best_score = float("-inf")
    for r in results:
        section_tokens = set(_tokenize_for_match(r.get("section", "")))
        content_tokens = set(_tokenize_for_match(r.get("content", "")))

        section_overlap = len(q_tokens & section_tokens)
        content_overlap = len(q_tokens & content_tokens)
        score = (section_overlap * 2.0) + (content_overlap * 1.0) + (r["score"] * 0.5)

        if score > best_score:
            best_score = score
            best = r

    return best


def _question_looks_multi_part(question: str) -> bool:
    q = question.lower()
    return any(marker in q for marker in [" and ", " as well as ", " both ", ", and "])


def _pick_fallback_evidence(question: str, results: list[dict[str, Any]], max_items: int = 2) -> list[dict[str, Any]]:
    if not results:
        return []

    q_tokens = set(_tokenize_for_match(question))
    if not q_tokens:
        return [results[0]]

    scored: list[tuple[float, set[str], dict[str, Any]]] = []
    for r in results:
        section_tokens = set(_tokenize_for_match(r.get("section", "")))
        content_tokens = set(_tokenize_for_match(r.get("content", "")))
        overlap_tokens = q_tokens & (section_tokens | content_tokens)
        overlap = len(overlap_tokens)
        rank_score = (overlap * 2.0) + (r["score"] * 0.5)
        scored.append((rank_score, overlap_tokens, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    picked: list[dict[str, Any]] = []
    covered_tokens: set[str] = set()

    # Always take the strongest evidence first.
    first = scored[0][2]
    picked.append(first)
    covered_tokens |= scored[0][1]

    if max_items <= 1 or len(scored) == 1:
        return picked

    want_two = _question_looks_multi_part(question)
    for _, overlap_tokens, candidate in scored[1:]:
        same_source = any(
            p["filename"] == candidate["filename"] and p["section"] == candidate["section"]
            for p in picked
        )
        if same_source:
            continue

        adds_new_info = len(overlap_tokens - covered_tokens) >= 1
        if want_two and adds_new_info:
            picked.append(candidate)
            break

        # For non-multipart questions, only add another source if it meaningfully expands coverage.
        if (not want_two) and len(overlap_tokens - covered_tokens) >= 2:
            picked.append(candidate)
            break

    # For explicit multi-part questions, prefer at least two distinct evidence chunks.
    if want_two and len(picked) == 1:
        for _, _, candidate in scored[1:]:
            same_source = any(
                p["filename"] == candidate["filename"] and p["section"] == candidate["section"]
                for p in picked
            )
            if not same_source:
                picked.append(candidate)
                break

    return picked


def _pick_best_preview(question: str, content: str, max_sentences: int = 2) -> str:
    normalized = content.replace("\n", " ").strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", normalized) if s.strip()]
    if not sentences:
        return normalized[:300].strip()

    q_tokens = set(_tokenize_for_match(question))
    if not q_tokens:
        return " ".join(sentences[:max_sentences]).strip()

    scored = []
    for i, sentence in enumerate(sentences):
        s_tokens = set(_tokenize_for_match(sentence))
        overlap = len(q_tokens & s_tokens)
        # Keep slight preference for earlier sentences when overlap is equal.
        score = overlap - (i * 0.01)
        scored.append((score, i, sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = sorted(scored[:max_sentences], key=lambda x: x[1])
    picked = [s for _, _, s in top if s]
    return " ".join(picked).strip() if picked else sentences[0]


def _clean_preview_text(text: str) -> str:
    cleaned = text.replace("\n", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"^\s*#{1,6}\s*", "", cleaned)
    cleaned = cleaned.replace("�", "'")
    return cleaned.strip()


def _fallback_relevance_ok(question: str, results: list[dict[str, Any]]) -> bool:
    q_tokens = set(_tokenize_for_match(question))
    if not q_tokens:
        return True

    all_content = " ".join(r.get("section", "") + " " + r.get("content", "") for r in results)
    content_tokens = set(_tokenize_for_match(all_content))
    overlap = q_tokens & content_tokens

    if len(overlap) == 0:
        return False

    if len(overlap) >= 2:
        return True

    if len(overlap) == 1 and results and results[0]["score"] >= 0.55:
        return True

    return False


def extractive_fallback_answer(question: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return "The information is not available in the documents."

    if not _fallback_relevance_ok(question, results):
        return "The information is not available in the documents."

    evidence = _pick_fallback_evidence(question, results, max_items=2)
    previews: list[str] = []
    sources: list[str] = []
    for i, ev in enumerate(evidence, start=1):
        preview = _clean_preview_text(ev["content"])
        if not preview:
            preview = ev["content"][:500].replace("\n", " ").strip()
        previews.append(preview)
        sources.append(f"[{i}] {ev['filename']} ({ev['section']})")

    if len(previews) == 1:
        answer_text = previews[0]
    else:
        answer_text = "\n".join(f"- {p}" for p in previews)

    return f"{answer_text}\nSources: " + ", ".join(sources)


def run_index_flow() -> None:
    print("[LOG] Step 1/5: Loading markdown documents...")
    docs = load_documents()

    print("[LOG] Step 2/5: Filtering noisy/rubbish files...")
    kept_docs, filtered_docs = filter_documents(docs)

    print("[LOG] Step 3/5: Chunking kept documents...")
    all_chunks = build_chunks(kept_docs)

    print("[LOG] Step 4/5: Building embeddings + FAISS index...")
    index, _ = build_faiss_index(all_chunks)

    print("[LOG] Step 5/5: Saving index + chunk metadata...")
    save_index_and_metadata(index, all_chunks, output_dir=INDEX_DIR)

    print("\nIndex build complete.")
    print(f"Loaded docs: {len(docs)}")
    print(f"Kept docs: {len(kept_docs)}")
    print(f"Filtered docs: {len(filtered_docs)}")
    print(f"Total chunks: {len(all_chunks)}")
    if filtered_docs:
        print("Filtered files:", ", ".join(d["filename"] for d in filtered_docs))


def run_ask_flow(question: str, top_k: int, llm_model: str) -> None:
    print("[LOG] Step 1/5: Loading FAISS index and chunk metadata...")
    index, chunks, embed_model = load_index_and_metadata(output_dir=INDEX_DIR)

    print("[LOG] Step 2/5: Running semantic retrieval...")
    results = search(question, index, embed_model, chunks, top_k=top_k)

    print("[LOG] Step 3/5: Evaluating retrieval confidence...")
    if not results or results[0]["score"] < SIMILARITY_THRESHOLD:
        print("Answer: The information is not available in the documents.")
        print("Sources: none")
        return

    print("[LOG] Step 4/5: Generating grounded answer...")
    try:
        answer = generate_answer_with_llm(question, results, model_name=llm_model)
    except Exception as exc:
        print(f"[LOG] Gemini unavailable ({exc}). Using extractive fallback.")
        answer = extractive_fallback_answer(question, results)

    print("[LOG] Step 5/5: Displaying answer and sources...")
    print("\nQuestion:", question)
    print("Answer:", answer)

    unique_sources = []
    seen = set()
    for r in results:
        key = (r["filename"], r["section"])
        if key not in seen:
            seen.add(key)
            unique_sources.append(key)

    print("\nRetrieved sources:")
    for fname, section in unique_sources:
        label = section if section else "No section"
        print(f"- {fname} ({label})")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Small RAG system for internal policy/procedure documents."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("index", help="Build embeddings and FAISS index from documents.")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against indexed documents.")
    ask_parser.add_argument("--q", required=True, help="Question in natural language.")
    ask_parser.add_argument("--top-k", type=int, default=5, help="How many chunks to retrieve.")
    ask_parser.add_argument(
        "--llm-model",
        default=LLM_MODEL_NAME,
        help="Gemini model for final answer generation.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "index":
        run_index_flow()
    elif args.command == "ask":
        run_ask_flow(args.q, top_k=args.top_k, llm_model=args.llm_model)