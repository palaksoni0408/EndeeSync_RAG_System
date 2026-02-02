"""
Retrieval module.
Performs similarity search on Endee vector database.
"""

import logging
from typing import List, Dict, Any

from . import config
from .store import get_endee_client, initialize_endee_index
from .embed import embed_query

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def format_results(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format Endee query results for easier consumption.
    
    Args:
        raw_results: Raw results from Endee query
        
    Returns:
        Formatted results with text and metadata
    """
    formatted = []
    
    for result in raw_results:
        formatted_result = {
            "id": result.get("id"),
            "similarity": result.get("similarity"),
            "distance": result.get("distance"),
            "text": result.get("meta", {}).get("text", ""),
            "source": result.get("meta", {}).get("source", ""),
            "chunk_index": result.get("meta", {}).get("chunk_index", 0)
        }
        formatted.append(formatted_result)
    
    return formatted


def retrieve_context(
    query: str,
    top_k: int = None,
    ef: int = None,
    index_name: str = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context chunks for a query.
    
    Args:
        query: User query string
        top_k: Number of results to retrieve (defaults to config.DEFAULT_TOP_K)
        ef: Search quality parameter (defaults to config.DEFAULT_EF)
        index_name: Name of the index to query (defaults to config.ENDEE_INDEX_NAME)
        
    Returns:
        List of relevant chunks with text and metadata
    """
    if top_k is None:
        top_k = config.DEFAULT_TOP_K
    
    if ef is None:
        ef = config.DEFAULT_EF
    
    if index_name is None:
        index_name = config.ENDEE_INDEX_NAME
    
    logger.info(f"Retrieving context for query: '{query[:100]}...'")
    logger.info(f"Parameters: top_k={top_k}, ef={ef}")
    
    try:
        # Embed the query
        query_embedding = embed_query(query)
        
        if query_embedding.size == 0:
            logger.warning("Empty query embedding, returning no results")
            return []
        
        # Get the index
        index = initialize_endee_index(index_name)
        
        # Query Endee
        raw_results = index.query(
            vector=query_embedding.tolist(),
            top_k=top_k,
            ef=ef
        )
        
        logger.info(f"Retrieved {len(raw_results)} results")
        
        # Format results
        formatted_results = format_results(raw_results)
        
        # Log top result for debugging
        if formatted_results:
            top_result = formatted_results[0]
            logger.info(f"Top result - Similarity: {top_result['similarity']:.4f}, Source: {top_result['source']}")
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        raise


def retrieve_with_filter(
    query: str,
    filters: List[Dict[str, Any]],
    top_k: int = None,
    ef: int = None,
    index_name: str = None
) -> List[Dict[str, Any]]:
    """
    Retrieve context with filters applied.
    
    Args:
        query: User query string
        filters: List of filter dictionaries (e.g., [{"source": {"$eq": "doc.txt"}}])
        top_k: Number of results to retrieve
        ef: Search quality parameter
        index_name: Name of the index to query
        
    Returns:
        List of filtered relevant chunks
    """
    if top_k is None:
        top_k = config.DEFAULT_TOP_K
    
    if ef is None:
        ef = config.DEFAULT_EF
    
    if index_name is None:
        index_name = config.ENDEE_INDEX_NAME
    
    logger.info(f"Retrieving with filters: {filters}")
    
    try:
        # Embed the query
        query_embedding = embed_query(query)
        
        # Get the index
        index = initialize_endee_index(index_name)
        
        # Query with filters
        raw_results = index.query(
            vector=query_embedding.tolist(),
            top_k=top_k,
            ef=ef,
            filter=filters
        )
        
        logger.info(f"Retrieved {len(raw_results)} filtered results")
        
        # Format results
        formatted_results = format_results(raw_results)
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error during filtered retrieval: {e}")
        raise


if __name__ == "__main__":
    # Test retrieval
    test_query = "What is a vector database?"
    
    print(f"Testing retrieval with query: '{test_query}'")
    
    try:
        results = retrieve_context(test_query, top_k=3)
        
        print(f"\nRetrieved {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Source: {result['source']}")
            print(f"Text: {result['text'][:200]}...")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to run ingestion first and that Endee server is running")
