import argparse
from rag.config import LLM_MODEL_NAME
from rag.pipeline import run_ask_flow, run_index_flow


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