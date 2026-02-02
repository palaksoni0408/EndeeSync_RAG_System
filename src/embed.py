"""
Embedding generation module.
Generates vector embeddings using sentence-transformers.
"""

import logging
from typing import List, Union
import numpy as np

from sentence_transformers import SentenceTransformer

from . import config

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Global model instance (singleton pattern)
_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get or initialize the embedding model (singleton pattern).
    
    Returns:
        Initialized SentenceTransformer model
    """
    global _embedding_model
    
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        logger.info(f"Model loaded successfully. Embedding dimension: {config.VECTOR_DIMENSION}")
    
    return _embedding_model


def embed_texts(texts: List[str], batch_size: int = None, show_progress: bool = True) -> np.ndarray:
    """
    Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
        batch_size: Batch size for processing (defaults to config.EMBEDDING_BATCH_SIZE)
        show_progress: Whether to show progress bar
        
    Returns:
        Numpy array of embeddings with shape (len(texts), embedding_dim)
    """
    if not texts:
        logger.warning("No texts provided for embedding")
        return np.array([])
    
    if batch_size is None:
        batch_size = config.EMBEDDING_BATCH_SIZE
    
    model = get_embedding_model()
    
    logger.info(f"Generating embeddings for {len(texts)} texts")
    
    try:
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise


def embed_query(query: str) -> np.ndarray:
    """
    Generate embedding for a single query.
    
    Args:
        query: Query text
        
    Returns:
        Numpy array embedding vector
    """
    if not query or not query.strip():
        logger.warning("Empty query provided")
        return np.array([])
    
    model = get_embedding_model()
    
    try:
        embedding = model.encode(query, convert_to_numpy=True)
        return embedding
    
    except Exception as e:
        logger.error(f"Error embedding query: {e}")
        raise


def embed_chunks(chunks: List[dict], text_key: str = "text") -> List[dict]:
    """
    Add embeddings to chunk objects.
    
    Args:
        chunks: List of chunk dictionaries
        text_key: Key in chunk dict that contains the text to embed
        
    Returns:
        Chunks with added 'embedding' field
    """
    logger.info(f"Embedding {len(chunks)} chunks")
    
    # Extract texts
    texts = [chunk[text_key] for chunk in chunks]
    
    # Generate embeddings
    embeddings = embed_texts(texts)
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding.tolist()  # Convert to list for JSON serialization
    
    logger.info(f"Successfully embedded {len(chunks)} chunks")
    return chunks


if __name__ == "__main__":
    # Test the embedding module
    test_texts = [
        "This is a test sentence about vector databases.",
        "Semantic search enables finding similar content.",
        "RAG systems combine retrieval with generation."
    ]
    
    print("Testing embedding generation...")
    embeddings = embed_texts(test_texts)
    print(f"Generated embeddings shape: {embeddings.shape}")
    print(f"First embedding (first 10 dims): {embeddings[0][:10]}")
    
    # Test query embedding
    query = "What is semantic search?"
    query_embedding = embed_query(query)
    print(f"\nQuery embedding shape: {query_embedding.shape}")
    print(f"Query embedding (first 10 dims): {query_embedding[:10]}")
