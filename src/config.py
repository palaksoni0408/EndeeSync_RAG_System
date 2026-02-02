"""
Configuration module for RAG system.
All configurable parameters are centralized here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===========================
# Project Paths
# ===========================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"

# ===========================
# Endee Configuration
# ===========================
ENDEE_BASE_URL = os.getenv("ENDEE_BASE_URL", "http://localhost:8080/api/v1")
ENDEE_AUTH_TOKEN = os.getenv("ENDEE_AUTH_TOKEN", "")  # Empty string for no auth
ENDEE_INDEX_NAME = "rag_documents"

# Index parameters
VECTOR_DIMENSION = 384  # Matches all-MiniLM-L6-v2
SPACE_TYPE = "cosine"
PRECISION = "INT8D"  # Options: BINARY, INT8D, INT16D, FLOAT16, FLOAT32
HNSW_M = 16  # Graph connectivity
HNSW_EF_CON = 128  # Construction parameter

# ===========================
# Embedding Model Configuration
# ===========================
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 32  # Batch size for embedding generation

# ===========================
# Document Processing
# ===========================
CHUNK_SIZE = 512  # Tokens per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks (tokens)
SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf"]

# ===========================
# Retrieval Configuration
# ===========================
DEFAULT_TOP_K = 5  # Number of results to retrieve
DEFAULT_EF = 128  # Search quality parameter (max 1024)

# ===========================
# LLM Configuration
# ===========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 500

# Groq Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast, high-quality model
# Alternatives: "llama-3.1-70b-versatile", "gemma2-9b-it"

# Fallback logic: OpenAI -> Groq -> Local LLM
USE_OPENAI = bool(OPENAI_API_KEY)
USE_GROQ = bool(GROQ_API_KEY)
USE_LOCAL_LLM = not (USE_OPENAI or USE_GROQ)
LOCAL_LLM_MODEL = "google/flan-t5-large"

# ===========================
# Logging Configuration
# ===========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ===========================
# Prompt Templates
# ===========================
RAG_PROMPT_TEMPLATE = """Context information is below:
---
{context}
---

Given the context above, answer the following question. If the context doesn't contain relevant information to answer the question, say "I don't have enough information in the provided context to answer this question."

Question: {query}

Answer:"""
