import hashlib
import re
from pathlib import Path
from typing import Any


def _content_fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


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


def load_documents() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    documents: list[dict[str, str]] = []
    unreadable_docs: list[dict[str, str]] = []
    duplicate_docs: list[dict[str, str]] = []
    folder = Path("documents")
    seen_fingerprints: dict[str, str] = {}

    if not folder.exists():
        return [], [{"filename": "documents/", "reason": "Documents folder does not exist."}], []

    for file in sorted(folder.glob("*.md"), key=lambda p: p.name.lower()):
        try:
            text = file.read_text(encoding="utf-8")
        except Exception as exc:
            unreadable_docs.append(
                {
                    "filename": file.name,
                    "reason": f"Could not read file: {exc}",
                }
            )
            continue

        if not text.strip():
            unreadable_docs.append(
                {
                    "filename": file.name,
                    "reason": "File is empty.",
                }
            )
            continue

        fingerprint = _content_fingerprint(text)
        if fingerprint in seen_fingerprints:
            duplicate_docs.append(
                {
                    "filename": file.name,
                    "reason": f"Duplicate content of {seen_fingerprints[fingerprint]}",
                }
            )
            continue

        seen_fingerprints[fingerprint] = file.name
        documents.append({"filename": file.name, "content": text, "doc_hash": fingerprint})

    return documents, unreadable_docs, duplicate_docs


def split_markdown_into_chunks(
    text: str,
    filename: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[dict[str, Any]]:
    sections = re.split(r"(?m)(?=^#{1,3}\s)", text)
    chunks: list[dict[str, Any]] = []

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


def build_chunks(kept_docs: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    all_chunks = []
    chunk_warnings: list[dict[str, str]] = []
    for doc in kept_docs:
        chunks = split_markdown_into_chunks(doc["content"], doc["filename"])
        if not chunks:
            chunk_warnings.append(
                {
                    "filename": doc["filename"],
                    "reason": "No chunks created (document too short or malformed).",
                }
            )
            continue

        for i, chunk in enumerate(chunks, start=1):
            chunk["chunk_id"] = f"{doc['filename']}::chunk-{i}"
            chunk["doc_hash"] = doc.get("doc_hash", "")
            all_chunks.append(chunk)
    return all_chunks, chunk_warnings

