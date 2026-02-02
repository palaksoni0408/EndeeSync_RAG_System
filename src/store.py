"""
Endee storage module.
Handles vector storage and index management in Endee vector database.
"""

import logging
from typing import List, Dict, Any

from endee import Endee, Precision

from . import config

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Global Endee client instance
_endee_client = None


def get_endee_client() -> Endee:
    """
    Get or initialize the Endee client (singleton pattern).
    
    Returns:
        Initialized Endee client
    """
    global _endee_client
    
    if _endee_client is None:
        logger.info("Initializing Endee client")
        
        # Initialize with or without authentication
        if config.ENDEE_AUTH_TOKEN:
            _endee_client = Endee(config.ENDEE_AUTH_TOKEN)
            logger.info("Endee client initialized with authentication")
        else:
            _endee_client = Endee()
            logger.info("Endee client initialized without authentication")
        
        # Set custom base URL if different from default
        if config.ENDEE_BASE_URL != "http://localhost:8080/api/v1":
            _endee_client.set_base_url(config.ENDEE_BASE_URL)
            logger.info(f"Endee base URL set to: {config.ENDEE_BASE_URL}")
    
    return _endee_client


def get_precision_enum(precision_str: str) -> Precision:
    """
    Convert precision string to Endee Precision enum.
    
    Args:
        precision_str: Precision string (BINARY, INT8D, INT16D, FLOAT16, FLOAT32)
        
    Returns:
        Precision enum value
    """
    precision_map = {
        "BINARY": Precision.BINARY2,  # Endee uses BINARY2
        "BINARY2": Precision.BINARY2,
        "INT8D": Precision.INT8D,
        "INT16D": Precision.INT16D,
        "FLOAT16": Precision.FLOAT16,
        "FLOAT32": Precision.FLOAT32
    }
    return precision_map.get(precision_str, Precision.INT8D)


def initialize_endee_index(index_name: str = None) -> Any:
    """
    Create or get existing Endee index.
    
    Args:
        index_name: Name of the index (defaults to config.ENDEE_INDEX_NAME)
        
    Returns:
        Endee index object
    """
    if index_name is None:
        index_name = config.ENDEE_INDEX_NAME
    
    client = get_endee_client()
    
    try:
        # Try to get existing index
        existing_indexes = client.list_indexes()
        logger.info(f"Existing indexes: {existing_indexes}")
        
        # list_indexes() returns a list of index names (strings)
        if index_name in existing_indexes:
            logger.info(f"Index '{index_name}' already exists, retrieving it")
            index = client.get_index(name=index_name)
        else:
            # Create new index
            logger.info(f"Creating new index '{index_name}'")
            try:
                client.create_index(
                    name=index_name,
                    dimension=config.VECTOR_DIMENSION,
                    space_type=config.SPACE_TYPE,
                    precision=get_precision_enum(config.PRECISION),
                    M=config.HNSW_M,
                    ef_con=config.HNSW_EF_CON
                )
                logger.info(f"Index '{index_name}' created successfully")
            except Exception as create_error:
                # Index might have been created between list and create calls
                if "already exists" in str(create_error).lower():
                    logger.warning(f"Index '{index_name}' was created by another process, retrieving it")
                else:
                    raise
            
            index = client.get_index(name=index_name)
        
        # Log index info
        index_info = index.describe()
        logger.info(f"Index details: {index_info}")
        
        return index
    
    except Exception as e:
        logger.error(f"Error initializing Endee index: {e}")
        raise


def batch_upsert(index: Any, vectors: List[Dict[str, Any]], batch_size: int = 1000) -> None:
    """
    Upsert vectors to Endee in batches.
    Max batch size is 1000 per Endee documentation.
    
    Args:
        index: Endee index object
        vectors: List of vector dictionaries with id, vector, and meta fields
        batch_size: Number of vectors per batch (max 1000)
    """
    total_vectors = len(vectors)
    logger.info(f"Upserting {total_vectors} vectors in batches of {batch_size}")
    
    for i in range(0, total_vectors, batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(batch)
            logger.info(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")
        except Exception as e:
            logger.error(f"Error upserting batch {i // batch_size + 1}: {e}")
            raise
    
    logger.info(f"Successfully upserted all {total_vectors} vectors")


def store_embeddings(chunks: List[Dict[str, Any]], index_name: str = None) -> None:
    """
    Store embedded chunks in Endee vector database.
    
    Args:
        chunks: List of chunk dictionaries with id, text, embedding, and metadata
        index_name: Name of the index (defaults to config.ENDEE_INDEX_NAME)
    """
    logger.info(f"Storing {len(chunks)} chunks in Endee")
    
    # Initialize index
    index = initialize_endee_index(index_name)
    
    # Prepare vectors for Endee
    vectors = []
    for chunk in chunks:
        vector_obj = {
            "id": chunk["id"],
            "vector": chunk["embedding"],
            "meta": {
                "text": chunk["text"],
                "source": chunk["metadata"]["source"],
                "chunk_index": chunk["metadata"]["chunk_index"],
                "total_chunks": chunk["metadata"]["total_chunks"]
            }
        }
        vectors.append(vector_obj)
    
    # Upsert in batches (max 1000 per batch per Endee docs)
    batch_upsert(index, vectors, batch_size=1000)
    
    logger.info("Storage complete")


def delete_index(index_name: str = None) -> None:
    """
    Delete an Endee index.
    
    Args:
        index_name: Name of the index to delete (defaults to config.ENDEE_INDEX_NAME)
    """
    if index_name is None:
        index_name = config.ENDEE_INDEX_NAME
    
    client = get_endee_client()
    
    try:
        client.delete_index(index_name)
        logger.info(f"Index '{index_name}' deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting index '{index_name}': {e}")
        raise


if __name__ == "__main__":
    # Test Endee connection
    print("Testing Endee connection...")
    client = get_endee_client()
    
    try:
        indexes = client.list_indexes()
        print(f"Connected to Endee successfully!")
        print(f"Existing indexes: {indexes}")
    except Exception as e:
        print(f"Error connecting to Endee: {e}")
        print("Make sure Endee server is running on the configured URL")
