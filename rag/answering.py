import os
import re
from collections import defaultdict
from typing import Any

try:
    from google import genai as google_genai
except ImportError:
    google_genai = None


def _tokenize_for_match(text: str) -> list[str]:
    stopwords = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "to",
        "of",
        "and",
        "or",
        "in",
        "on",
        "for",
        "with",
        "by",
        "be",
        "as",
        "at",
        "it",
        "this",
        "that",
        "from",
        "can",
        "must",
        "should",
        "during",
        "new",
        "employee",
        "document",
        "documents",
        "described",
        "what",
        "how",
        "when",
        "where",
        "which",
        "who",
        "does",
        "do",
        "according",
        "policy",
        "procedure",
        "procedures",
        "summarize",
        "summary",
        "reference",
    }
    tokens = re.findall(r"\b[a-z0-9]{2,}\b", text.lower())
    return [t for t in tokens if t not in stopwords]


def _question_looks_multi_part(question: str) -> bool:
    q = question.lower()
    return any(marker in q for marker in [" and ", " as well as ", " both ", ", and "])


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


def build_context(results: list[dict[str, Any]]) -> str:
    parts = []
    for i, result in enumerate(results, start=1):
        parts.append(
            (
                f"[{i}] file={result['filename']} | section={result['section']} | score={result['score']:.3f}\n"
                f"{result['content']}"
            )
        )
    return "\n\n".join(parts)


def build_document_summaries(
    question: str,
    results: list[dict[str, Any]],
    max_docs: int = 3,
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        grouped[result["filename"]].append(result)

    ranked_docs: list[tuple[float, str, list[dict[str, Any]]]] = []
    for filename, doc_results in grouped.items():
        doc_score = max(r["score"] for r in doc_results)
        ranked_docs.append((doc_score, filename, doc_results))
    ranked_docs.sort(key=lambda x: x[0], reverse=True)

    summaries: list[dict[str, str]] = []
    for _, filename, doc_results in ranked_docs[:max_docs]:
        merged = " ".join(r.get("content", "") for r in doc_results[:3]).strip()
        summary = _pick_best_preview(question, merged, max_sentences=3)
        sections = sorted({r.get("section", "").strip() for r in doc_results if r.get("section", "").strip()})
        summaries.append(
            {
                "filename": filename,
                "summary": _clean_preview_text(summary),
                "sections": ", ".join(sections[:4]) if sections else "No section",
            }
        )
    return summaries


def build_document_summary_context(document_summaries: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for i, summary in enumerate(document_summaries, start=1):
        parts.append(f"[DOC {i}] file={summary['filename']} | sections={summary['sections']}\n{summary['summary']}")
    return "\n\n".join(parts)


def generate_answer_with_llm(question: str, results: list[dict[str, Any]], model_name: str) -> str:
    if google_genai is None:
        raise RuntimeError("google-genai package is not installed. Run: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    client = google_genai.Client(api_key=api_key)
    context = build_context(results)
    document_summaries = build_document_summaries(question, results)
    document_context = build_document_summary_context(document_summaries)

    system_prompt = (
        "You are a careful assistant answering questions strictly from provided internal documents. "
        "If information is missing or unclear in the provided context, explicitly say that the information "
        "is not available in the documents. Do not invent facts."
    )
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Document summaries:\n{document_context}\n\n"
        f"Context documents:\n{context}\n\n"
        "Instructions:\n"
        "1) Answer only using context.\n"
        "2) Prefer document-level understanding from summaries, then verify with chunks.\n"
        "3) Keep answer concise and practical.\n"
        "4) If not found, clearly state it's not available in documents.\n"
        "5) Do NOT include a Sources line — sources are displayed separately.\n"
    )

    response = client.models.generate_content(
        model=model_name,
        contents=f"{system_prompt}\n\n{user_prompt}",
    )
    answer = response.text.strip()
    answer = re.sub(r"\n*Sources:.*$", "", answer, flags=re.DOTALL).strip()
    return answer


def _pick_fallback_evidence(question: str, results: list[dict[str, Any]], max_items: int = 2) -> list[dict[str, Any]]:
    if not results:
        return []

    q_tokens = set(_tokenize_for_match(question))
    if not q_tokens:
        return [results[0]]

    scored: list[tuple[float, set[str], dict[str, Any]]] = []
    for result in results:
        section_tokens = set(_tokenize_for_match(result.get("section", "")))
        content_tokens = set(_tokenize_for_match(result.get("content", "")))
        overlap_tokens = q_tokens & (section_tokens | content_tokens)
        overlap = len(overlap_tokens)
        rank_score = (overlap * 2.0) + (result["score"] * 0.5)
        scored.append((rank_score, overlap_tokens, result))

    scored.sort(key=lambda x: x[0], reverse=True)
    picked: list[dict[str, Any]] = []
    covered_tokens: set[str] = set()

    first = scored[0][2]
    picked.append(first)
    covered_tokens |= scored[0][1]

    if max_items <= 1 or len(scored) == 1:
        return picked

    want_two = _question_looks_multi_part(question)
    for _, overlap_tokens, candidate in scored[1:]:
        same_source = any(
            p["filename"] == candidate["filename"] and p["section"] == candidate["section"] for p in picked
        )
        if same_source:
            continue

        adds_new_info = len(overlap_tokens - covered_tokens) >= 1
        if want_two and adds_new_info:
            picked.append(candidate)
            break

        if (not want_two) and len(overlap_tokens - covered_tokens) >= 2:
            picked.append(candidate)
            break

    if want_two and len(picked) == 1:
        for _, _, candidate in scored[1:]:
            same_source = any(
                p["filename"] == candidate["filename"] and p["section"] == candidate["section"] for p in picked
            )
            if not same_source:
                picked.append(candidate)
                break

    return picked


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

    evidence = _pick_fallback_evidence(question, results, max_items=4)
    document_summaries = build_document_summaries(question, evidence, max_docs=2)
    if not document_summaries:
        return "The information is not available in the documents."

    sources: list[str] = []
    for i, summary in enumerate(document_summaries, start=1):
        sources.append(f"[{i}] {summary['filename']} ({summary['sections']})")

    if len(document_summaries) == 1:
        answer_text = document_summaries[0]["summary"]
    else:
        answer_text = "\n".join(f"- {summary['filename']}: {summary['summary']}" for summary in document_summaries)

    return f"{answer_text}\nSources: " + ", ".join(sources)

