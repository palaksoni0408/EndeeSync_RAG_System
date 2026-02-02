"""
API Handlers for EndeeSync RAG System.

This module contains handler functions for all API endpoints,
implementing document ingestion, RAG querying, semantic search, and summarization.
"""

import time
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from src import config
from src.store import get_endee_client, initialize_endee_index
from src.embed import embed_query, embed_texts
from src.rag import generate_answer as rag_generate_answer
from src.retrieve import retrieve_context, retrieve_with_filter


def ingest_document(text: str, source: Optional[str] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Ingest a document by chunking and storing in Endee.
    
    Args:
        text: Document text content
        source: Source identifier (filename, title, etc.)
        tags: List of tags for filtering
        metadata: Additional metadata
        
    Returns:
        Dict with document_id, chunk_count, message
    """
    start_time = time.time()
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Chunk the text (simple sentence-based chunking for now)
    chunks = chunk_text(text, max_chunk_size=config.CHUNK_SIZE)
    
    # Get Endee index
    index = initialize_endee_index("rag_documents")
    
    # Store each chunk
    vectors = []
    for idx, chunk in enumerate(chunks):
        # Get embedding
        embedding = embed_query(chunk)
        
        # Prepare metadata
        chunk_metadata = {
            "document_id": document_id,
            "chunk_index": idx,
            "source": source or "unknown",
            "tags": tags or [],
            "text": chunk,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        vectors.append({
            "id": f"{document_id}_{idx}",
            "vector": embedding,
            "meta": chunk_metadata
        })
    
    # Upsert to Endee
    index.upsert(vectors)
    
    elapsed = time.time() - start_time
    
    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "message": f"Document ingested successfully in {elapsed:.2f}s"
    }


def list_documents(limit: int = 100) -> Dict[str, Any]:
    """
    List all ingested documents.
    
    Args:
        limit: Maximum number of documents to return
        
    Returns:
        Dict with documents list and total count
    """
    index = initialize_endee_index("rag_documents")
    
    # Query all vectors (in a real implementation, you'd want pagination)
    # For now, we'll fetch and aggregate by document_id
    # Note: Using include_vectors=False to save bandwidth
    # Cap at 512 to respect Endee's maximum top_k
    fetch_limit = min(limit * 10, 512)
    results = index.query(
        vector=[0.0] * config.VECTOR_DIMENSION,  # Dummy vector
        top_k=fetch_limit,
        include_vectors=False
    )
    
    # Aggregate by document_id
    docs_map = {}
    # Endee query method returns list of dicts directly
    for result in results:
        metadata = result.get("meta", {})
        doc_id = metadata.get("document_id")
        
        if doc_id and doc_id not in docs_map:
            docs_map[doc_id] = {
                "document_id": doc_id,
                "source": metadata.get("source"),
                "chunk_count": 0,
                "tags": metadata.get("tags", [])
            }
        
        if doc_id:
            docs_map[doc_id]["chunk_count"] += 1
    
    documents = list(docs_map.values())[:limit]
    
    return {
        "documents": documents,
        "total": len(documents)
    }


def delete_document(document_id: str) -> None:
    """
    Delete a document and all its chunks from Endee.
    
    Args:
        document_id: Document ID to delete
    """
    index = initialize_endee_index("rag_documents")
    
    # Delete all vectors where document_id matches
    # Use delete_with_filter which is more efficient
    try:
        index.delete_with_filter({"document_id": document_id})
    except Exception as e:
        # Fallback logic if filter delete is not supported or fails
        print(f"Delete with filter failed: {e}")
        # Try finding and deleting individually
        results = index.query(
            vector=[0.0] * config.VECTOR_DIMENSION,
            top_k=1000,
            filter={"document_id": document_id},
            include_vectors=False
        )
        
        for result in results:
            index.delete_vector(result["id"])


def query_rag(question: str, top_k: int = 5, include_sources: bool = True, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Perform RAG query: retrieve context and generate answer.
    
    Args:
        question: User question
        top_k: Number of context chunks to retrieve
        include_sources: Whether to include source citations
        filters: Optional filters (e.g., {"tags": ["ml"]})
        
    Returns:
        Dict with answer, sources, and timings
    """
    start_time = time.time()
    
    # Retrieve context
    retrieval_start = time.time()
    if filters:
        context_results = retrieve_with_filter(question, filters=filters, top_k=top_k)
    else:
        context_results = retrieve_context(question, top_k=top_k)
    retrieval_time = (time.time() - retrieval_start) * 1000
    
    # Generate answer
    llm_start = time.time()
    result = rag_generate_answer(question, top_k=top_k)
    llm_time = (time.time() - llm_start) * 1000
    
    total_time = (time.time() - start_time) * 1000
    
    # Format sources if requested
    sources = []
    if include_sources and "sources" in result:
        sources = [
            {
                "text": src.get("text", ""),
                "score": src.get("similarity", 0.0),
                "source": src.get("source", "unknown"),
                "tags": src.get("tags", [])
            }
            for src in result.get("sources", [])
        ]
    
    return {
        "answer": result.get("answer", ""),
        "sources": sources,
        "timings": {
            "total_request_ms": total_time,
            "retrieval_ms": retrieval_time,
            "llm_generation_ms": llm_time
        }
    }


def search_semantic(query: str, top_k: int = 10, threshold: float = 0.0, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Perform semantic search without LLM generation.
    
    Args:
        query: Search query
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        filters: Optional filters
        
    Returns:
        Dict with results and timings
    """
    start_time = time.time()
    
    # Retrieve context
    if filters:
        context_results = retrieve_with_filter(query, filters=filters, top_k=top_k)
    else:
        context_results = retrieve_context(query, top_k=top_k)
    
    # Filter by threshold
    results = [
        {
            "text": ctx.get("text", ""),
            "score": ctx.get("similarity", 0.0),
            "source": ctx.get("source", "unknown"),
            "tags": ctx.get("tags", [])
        }
        for ctx in context_results
        if ctx.get("similarity", 0.0) >= threshold
    ]
    
    total_time = (time.time() - start_time) * 1000
    
    return {
        "results": results,
        "total": len(results),
        "timings": {
            "total_request_ms": total_time
        }
    }


def summarize_topic(topic: str, top_k: int = 10, max_length: int = 500, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Generate AI summary for a topic based on stored knowledge.
    
    Args:
        topic: Topic to summarize
        top_k: Number of context chunks to use
        max_length: Maximum summary length in words
        filters: Optional filters
        
    Returns:
        Dict with summary, topic, chunk_count, and timings
    """
    start_time = time.time()
    
    # Retrieve context
    retrieval_start = time.time()
    if filters:
        context_results = retrieve_with_filter(topic, filters=filters, top_k=top_k)
    else:
        context_results = retrieve_context(topic, top_k=top_k)
    retrieval_time = (time.time() - retrieval_start) * 1000
    
    # Build prompt for summarization
    context_text = "\n\n".join([ctx.get("text", "") for ctx in context_results])
    
    prompt = f"""Based on the following information, provide a comprehensive summary about "{topic}". 
Maximum length: {max_length} words.

Context:
{context_text}

Summary:"""
    
    # Generate summary using LLM
    llm_start = time.time()
    from src.rag import call_llm
    summary = call_llm(prompt)
    llm_time = (time.time() - llm_start) * 1000
    
    total_time = (time.time() - start_time) * 1000
    
    return {
        "summary": summary,
        "topic": topic,
        "chunk_count": len(context_results),
        "timings": {
            "total_request_ms": total_time,
            "retrieval_ms": retrieval_time,
            "llm_generation_ms": llm_time
        }
    }


def chunk_text(text: str, max_chunk_size: int = 500) -> List[str]:
    """
    Simple text chunking by sentences.
    
    Args:
        text: Input text
        max_chunk_size: Maximum chunk size in characters
        
    Returns:
        List of text chunks
    """
    # Simple sentence-based chunking
    sentences = text.replace('\n', ' ').split('. ')
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]
