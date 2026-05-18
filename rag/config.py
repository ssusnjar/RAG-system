EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gemini-2.5-flash"
INDEX_DIR = "rag_store"
SIMILARITY_THRESHOLD = 0.28

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

