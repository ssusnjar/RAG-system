# RAG System — Internal Document QA

A small AI system that answers questions based on internal company documents (policies and procedures).

## Features

- Loads and filters `.md` documents from `documents/`
- Handles unreadable/empty/duplicate documents during ingestion
- Automatically excludes noisy/rubbish files (symbol-heavy or repetitive gibberish)
- Splits documents into chunks (heading-aware, with overlap)
- Embeds chunks using `sentence-transformers` (`all-MiniLM-L6-v2`)
- Stores vectors in a FAISS index for fast similarity search
- Stores an ingestion report (`rag_store/ingestion_report.json`) for traceability
- Answers questions grounded strictly in the documents
- Builds document-level summaries from multiple retrieved chunks before final answering
- States which documents and sections were used (sources/citations)
- Clearly states when information is not available in the documents
- Displays a short step-by-step log of what the system did
- Includes a simple Gradio web UI for testing and sharing

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### 1. Build the index (once, or when documents change)

```bash
python main.py index
```

### 2. Ask a question (CLI)

```bash
python main.py ask --q "What is the deadline for submitting expense claims?"
```

### 3. Web UI

```bash
python app.py
```

Open `http://127.0.0.1:7860` in your browser.

### Optional: enable LLM-generated answers

Create a `.env` file in the project root (you can copy `.env.example`) and set:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

You can get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

Without the key, the system uses an extractive fallback (returns the most relevant chunk directly).

## Project structure

```
RAG-system/
├── main.py            # Thin CLI entrypoint (`index`, `ask`)
├── app.py             # Gradio web UI
├── rag/
│   ├── config.py      # Shared config/constants + .env loading
│   ├── ingestion.py   # Document loading, filtering, chunking
│   ├── retrieval.py   # Embedding, FAISS index I/O, semantic search
│   ├── answering.py   # LLM prompting + extractive fallback logic
│   └── pipeline.py    # Orchestration flows used by CLI and UI
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment variables for Gemini API
├── documents/         # Source markdown files (policies, procedures)
└── rag_store/         # Generated: FAISS index + chunk metadata (created by `main.py index`)
```

## Pipeline overview

```
Load .md files
    ↓
Filter out noisy/rubbish documents (heuristics: word count, diversity, symbol ratio)
    ↓
Split into chunks (by markdown headings, with sliding window + overlap for long sections)
    ↓
Embed chunks (sentence-transformers, all-MiniLM-L6-v2)
    ↓
Store in FAISS (cosine similarity via normalized inner product)
    ↓
User asks a question
    ↓
Embed the question → retrieve top-K most similar chunks
    ↓
Check retrieval confidence (similarity threshold)
    ↓
Generate answer (Gemini LLM or extractive fallback)
    ↓
Display answer + sources + step log
```

## Nice-to-have improvements (not implemented)

The following techniques are commonly used in production RAG systems. They were considered but intentionally not included because the current document set is small (15 files, ~13 after filtering, ~311 chunks) and the existing pipeline already provides accurate retrieval and grounded answers at this scale.

### Re-ranking with a cross-encoder

After FAISS retrieves the top-K chunks, a cross-encoder model (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) can re-score each (question, chunk) pair more accurately than the initial bi-encoder similarity. This helps when the top-K from FAISS contains false positives.

**Why not needed here:** With only ~311 chunks from 13 policy documents, FAISS retrieval is already precise. The top results consistently match the correct sections. Re-ranking adds latency and model complexity without measurable improvement at this scale.

### Query rewriting

Before searching, an LLM can reformulate the user's question to improve retrieval (e.g. expanding abbreviations, rephrasing vague queries, or generating multiple search variants).

**Why not needed here:** The documents are in clear English with well-structured headings. User questions about policies tend to be direct and well-formed (e.g. "What is the expense submission deadline?"). At this scale and domain, the embedding model handles natural-language queries well without rewriting.

### Hybrid search (keyword + semantic)

Combining BM25/TF-IDF keyword search with vector semantic search can improve recall, especially when exact terms matter (e.g. searching for a specific policy number or exact phrase).

**Why not needed here:** The documents are narrative policy text without codes, IDs, or highly specific terminology that would benefit from exact keyword matching. Semantic search alone covers the retrieval needs. Hybrid search adds infrastructure complexity (maintaining a keyword index alongside FAISS) that is not justified for this document set.

### When these would matter

These techniques become valuable when:
- The document corpus grows to hundreds or thousands of files
- Documents contain mixed formats, technical jargon, or codes
- User queries are conversational, vague, or in a different language than the documents
- Retrieval precision visibly degrades (wrong chunks appearing in top results)

## Known limitation: semantically valid but nonsensical documents

The document set includes `zulmar_policy.md`, which is structured like a real policy document but contains entirely fictional/nonsensical content (made-up terminology like "flarnic channels", "dravonic stabilization", etc.).

The filtering step correctly removes obviously broken documents (e.g. `symbolic_reference.md` which is pure symbols, or `krzth_monkey_document.md` which is gibberish). However, `zulmar_policy.md` passes filtering because it has valid sentence structure, sufficient word count, reasonable diversity, and low symbol ratio — it looks like real text.

As a result, the system will answer questions about "zulmar fragmentation" as if the document were real. This is expected behavior for a RAG system: it answers strictly from whatever documents are in the index, without judging whether the content is factually meaningful. The system is grounded, not fact-checked.

In a production setting, this would be addressed at the document ingestion level (e.g. manual review, domain-specific validation, or an LLM-based quality gate) rather than at query time.

## Recent updates (what was added and why)

### 1) Cleaner UI output in `app.py`

**What was added/changed:**
- The `Answer` box now shows only the answer text.
- Step-by-step logs are no longer shown to end users in the UI.
- Internal step logs are printed to terminal for debugging.

**Why:**
- End users should see a clean answer, not internal pipeline traces.
- Debug information is still available for development without cluttering the interface.

### 2) Smarter extractive fallback in `rag/answering.py`

**What was added/changed:**
- Added token-based helpers to pick the most question-relevant retrieved chunk.
- Added a small stopword filter so common words ("the", "is", "and", etc.) do not dominate overlap scoring.
- Added sentence selection that prefers sentences with stronger overlap with the question.
- Fallback now uses the best-matching chunk/sentences instead of always using the first retrieved chunk.

**Why:**
- The previous fallback could return generic text (for example a broad "Purpose" section) even when a more precise chunk was retrieved.
- The new logic improves answer relevance when LLM generation is unavailable (e.g., no `GEMINI_API_KEY`).

### 3) Removed generic fallback prefix text

**What was added/changed:**
- Removed the hardcoded fallback prefix: `Based on the documents, the most relevant information is:`

**Why:**
- The prefix was verbose and made responses feel templated.
- Answers are now more direct and natural while still grounded in sources.

### 4) Better fallback coverage for multi-part questions

**What was added/changed:**
- Added multi-part question detection (for prompts containing patterns like "and"/"both").
- Fallback evidence selection can now include two distinct high-relevance chunks instead of only one.
- Fallback output now cites multiple sources when multiple evidence chunks are used.

**Why:**
- Some questions ask about two topics in one sentence (for example "system access and company equipment").
- Previously, fallback could focus on only one topic even when retrieval found both.
- The updated logic improves completeness and aligns the final answer better with retrieved sources.

### 5) Fallback relevance check

**What was added/changed:**
- Before returning a fallback answer, the system now checks whether the retrieved chunks actually relate to the question using keyword overlap.
- If overlap is too low (e.g. the question asks about a filtered-out document), the system returns "The information is not available in the documents" instead of an irrelevant chunk.

**Why:**
- Without this check, the fallback could return unrelated text when no relevant chunk existed in the index (for example, questions about filtered documents like `symbolic_reference.md` would return chunks from `quantum_synergy_policy.md` simply because they had the highest similarity score).
- This makes the fallback behave more like the LLM path, which can recognize when retrieved context does not answer the question.

### 6) Switched from OpenAI to Google Gemini (free tier)

**What was added/changed:**
- Replaced the OpenAI SDK with `google-genai` for LLM answer generation.
- The default model is `gemini-2.5-flash` (free tier, no billing required).
- Added `.env` support via `python-dotenv` so the API key is loaded automatically from a `.env` file instead of requiring manual shell environment setup.
- The LLM model name is defined as a constant in `rag/config.py` (`LLM_MODEL_NAME`) rather than in `.env`, since it is not sensitive.

**Why:**
- OpenAI requires a paid API key. Gemini offers a free tier sufficient for this project's scale.
- `.env` file support makes setup simpler and avoids needing to set environment variables manually before each run.

### 7) More robust ingestion + cleaner answer architecture

**What was added/changed:**
- Ingestion now handles unreadable files, empty files, and duplicate-content files using content fingerprinting.
- The index build now writes `rag_store/ingestion_report.json` with skipped-file reasons and chunking warnings.
- Added a central `answer_question(...)` orchestration function used by both CLI and UI so retrieval/confidence/answering logic is no longer duplicated.
- Answer generation now includes document-level summaries (combined from multiple chunks of the same document), instead of relying only on single chunk snippets.

**Why:**
- Prevents silent ingestion failures that previously made some documents unavailable at query time.
- Makes debugging and QA easier by exposing ingestion decisions explicitly.
- Improves code organization (clearer layer separation between retrieval and answering).
- Improves answer quality for broader questions by summarizing at document level, not only chunk level.
