from typing import Any

from rag.answering import extractive_fallback_answer, generate_answer_with_llm
from rag.config import INDEX_DIR, LLM_MODEL_NAME, SIMILARITY_THRESHOLD
from rag.ingestion import build_chunks, filter_documents, load_documents
from rag.retrieval import build_faiss_index, load_index_and_metadata, save_index_and_metadata, search


def run_index_flow() -> None:
    print("[LOG] Step 1/5: Loading markdown documents...")
    docs, unreadable_docs, duplicate_docs = load_documents()

    print("[LOG] Step 2/5: Filtering noisy/rubbish files...")
    kept_docs, filtered_docs = filter_documents(docs)

    print("[LOG] Step 3/5: Chunking kept documents...")
    all_chunks, chunk_warnings = build_chunks(kept_docs)

    print("[LOG] Step 4/5: Building embeddings + FAISS index...")
    index, _ = build_faiss_index(all_chunks)

    print("[LOG] Step 5/5: Saving index + chunk metadata...")
    ingestion_report = {
        "loaded_docs": len(docs),
        "kept_docs": len(kept_docs),
        "filtered_docs": len(filtered_docs),
        "duplicates": duplicate_docs,
        "unreadable_or_empty": unreadable_docs,
        "chunk_warnings": chunk_warnings,
    }
    save_index_and_metadata(
        index,
        all_chunks,
        output_dir=INDEX_DIR,
        ingestion_report=ingestion_report,
    )

    print("\nIndex build complete.")
    print(f"Loaded docs: {len(docs)}")
    print(f"Kept docs: {len(kept_docs)}")
    print(f"Filtered docs: {len(filtered_docs)}")
    print(f"Duplicates skipped: {len(duplicate_docs)}")
    print(f"Unreadable/empty skipped: {len(unreadable_docs)}")
    print(f"Docs with chunk warnings: {len(chunk_warnings)}")
    print(f"Total chunks: {len(all_chunks)}")
    if filtered_docs:
        print("Filtered files:", ", ".join(d["filename"] for d in filtered_docs))
    if duplicate_docs:
        print("Duplicate files:", ", ".join(d["filename"] for d in duplicate_docs))
    if unreadable_docs:
        print("Unreadable/empty files:", ", ".join(d["filename"] for d in unreadable_docs))
    if chunk_warnings:
        print("Chunk warnings for files:", ", ".join(d["filename"] for d in chunk_warnings))


def answer_question(
    question: str,
    index,
    chunks: list[dict[str, Any]],
    embed_model,
    top_k: int = 5,
    llm_model: str = LLM_MODEL_NAME,
) -> dict[str, Any]:
    step_log: list[str] = ["Step 1/4: Running semantic retrieval"]
    results = search(question, index, embed_model, chunks, top_k=top_k)

    step_log.append("Step 2/4: Evaluating retrieval confidence")
    if not results or results[0]["score"] < SIMILARITY_THRESHOLD:
        return {
            "answer": "The information is not available in the documents.",
            "results": results,
            "sources": [],
            "step_log": step_log,
            "used_fallback": True,
        }

    step_log.append("Step 3/4: Generating grounded answer")
    used_fallback = False
    try:
        answer = generate_answer_with_llm(question, results, model_name=llm_model)
    except Exception:
        used_fallback = True
        answer = extractive_fallback_answer(question, results)

    unique_sources = []
    seen = set()
    for result in results:
        key = (result["filename"], result["section"])
        if key not in seen:
            seen.add(key)
            unique_sources.append({"filename": result["filename"], "section": result["section"]})

    step_log.append("Step 4/4: Done")
    return {
        "answer": answer,
        "results": results,
        "sources": unique_sources,
        "step_log": step_log,
        "used_fallback": used_fallback,
    }


def run_ask_flow(question: str, top_k: int, llm_model: str) -> None:
    print("[LOG] Step 1/5: Loading FAISS index and chunk metadata...")
    index, chunks, embed_model = load_index_and_metadata(output_dir=INDEX_DIR)
    response = answer_question(
        question=question,
        index=index,
        chunks=chunks,
        embed_model=embed_model,
        top_k=top_k,
        llm_model=llm_model,
    )
    print("[LOG] Step 2/5: Retrieval and answer generation completed.")
    print("\nQuestion:", question)
    print("Answer:", response["answer"])
    if response["used_fallback"]:
        print("[LOG] Fallback mode used (LLM unavailable or disabled).")

    print("\nRetrieved sources:")
    if not response["sources"]:
        print("- none")
    for source in response["sources"]:
        label = source["section"] if source["section"] else "No section"
        print(f"- {source['filename']} ({label})")

