from typing import List, Tuple

import gradio as gr

from main import (
    INDEX_DIR,
    answer_question,
    load_index_and_metadata,
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

    response = answer_question(
        question=question,
        index=INDEX,
        chunks=CHUNKS,
        embed_model=EMBED_MODEL,
        top_k=top_k,
    )

    source_lines: List[str] = []
    for source in response["sources"]:
        label = source["section"] if source["section"] else "No section"
        source_lines.append(f"- {source['filename']} ({label})")

    sources = "Retrieved sources:\n" + ("\n".join(source_lines) if source_lines else "- none")
    print("[UI LOG]\n" + "\n".join(response["step_log"]))
    return response["answer"], sources


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

