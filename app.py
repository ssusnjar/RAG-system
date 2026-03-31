import os
from typing import List, Tuple

import gradio as gr

from main import (
    SIMILARITY_THRESHOLD,
    INDEX_DIR,
    LLM_MODEL_NAME,
    load_index_and_metadata,
    search,
    build_context,
    generate_answer_with_llm,
    extractive_fallback_answer,
)


INDEX, CHUNKS, EMBED_MODEL = None, None, None


def _ensure_index_loaded():
    global INDEX, CHUNKS, EMBED_MODEL
    if INDEX is not None and CHUNKS is not None and EMBED_MODEL is not None:
        return
    INDEX, CHUNKS, EMBED_MODEL = load_index_and_metadata(output_dir=INDEX_DIR)


def answer(question: str, top_k: int = 5) -> Tuple[str, str]:
    """
    Minimal UI wrapper around your RAG pipeline.
    Returns: (answer_text, sources_text)
    """
    _ensure_index_loaded()

    step_log = []
    step_log.append("Step 1/4: retrieve relevant chunks")
    results = search(question, INDEX, EMBED_MODEL, CHUNKS, top_k=top_k)

    step_log.append("Step 2/4: check retrieval confidence")
    if not results or results[0]["score"] < SIMILARITY_THRESHOLD:
        sources = "Sources: none"
        print("[UI LOG]\n" + "\n".join(step_log))
        return "The information is not available in the documents.", sources

    # deduplicate sources for display
    seen = set()
    source_lines: List[str] = []
    for r in results:
        key = (r["filename"], r["section"])
        if key in seen:
            continue
        seen.add(key)
        label = r["section"] if r["section"] else "No section"
        source_lines.append(f"- {r['filename']} ({label})")

    step_log.append("Step 3/4: generate answer (Gemini LLM or fallback)")
    answer_text = ""
    try:
        llm_model = LLM_MODEL_NAME
        if os.getenv("GEMINI_API_KEY"):
            answer_text = generate_answer_with_llm(question, results, model_name=llm_model)
        else:
            raise RuntimeError("GEMINI_API_KEY not set")
    except Exception as exc:
        print(f"[UI LOG] Gemini unavailable ({exc}). Using extractive fallback.")
        answer_text = extractive_fallback_answer(question, results)

    step_log.append("Step 4/4: done")
    sources = "Retrieved sources:\n" + "\n".join(source_lines)
    print("[UI LOG]\n" + "\n".join(step_log))
    return answer_text, sources


CSS = """
.gradio-container {
    max-width: 75% !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
"""

with gr.Blocks(title="RAG Document QA", css=CSS) as demo:
    gr.Markdown("# Internal Documents RAG Tester")
    gr.Markdown("Ask a question. The app answers using retrieved chunks from your `documents/` knowledge base.")

    q = gr.Textbox(label="Question", placeholder="Example: How do we report a security incident?")
    top_k = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Top-K chunks to retrieve")
    run_btn = gr.Button("Answer")

    out_answer = gr.Textbox(label="Answer", lines=10)
    out_sources = gr.Textbox(label="Sources (documents used)", lines=8)

    run_btn.click(fn=answer, inputs=[q, top_k], outputs=[out_answer, out_sources])


if __name__ == "__main__":
    demo.launch()

