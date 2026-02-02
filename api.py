#!/usr/bin/env python3
"""
FastAPI backend for EndeeSync RAG System.
Provides REST API endpoints and serves the frontend.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from src import config
from src.store import get_endee_client
from src.api_handlers import (
    ingest_document,
    list_documents,
    delete_document,
    query_rag,
    search_semantic,
    summarize_topic
)

# Set up logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EndeeSync API",
    description="RAG System with Semantic Memory Engine",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="frontend")

# ============================================================================
# Request/Response Models
# ============================================================================

class IngestRequest(BaseModel):
    text: str
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    include_sources: Optional[bool] = True
    filters: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    threshold: Optional[float] = 0.0
    filters: Optional[Dict[str, Any]] = None

class SummarizeRequest(BaseModel):
    topic: str
    top_k: Optional[int] = 10
    max_length: Optional[int] = 500
    filters: Optional[Dict[str, Any]] = None

# ============================================================================
# Frontend Routes
# ============================================================================

@app.get("/")
async def serve_frontend(request: Request):
    """Serve the frontend landing page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": "EndeeSync",
        "app_version": "1.0.0"
    })

@app.get("/video")
async def serve_video(request: Request):
    """Serve the demo video page."""
    return templates.TemplateResponse("video.html", {
        "request": request
    })

@app.get("/dashboard")
async def serve_dashboard(request: Request):
    """Serve the main application dashboard."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "app_name": "EndeeSync",
        "app_version": "1.0.0"
    })

@app.get("/documentation")
async def serve_documentation(request: Request):
    """Serve the projects documentation page."""
    return templates.TemplateResponse("docs.html", {
        "request": request
    })

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """System health check."""
    status = {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "endee": "unknown",
            "llm": "ready"
        }
    }
    
    try:
        client = get_endee_client()
        client.list_indexes()
        status["components"]["endee"] = "connected"
    except Exception as e:
        status["components"]["endee"] = f"error: {str(e)}"
        status["status"] = "degraded"
        
    return status

@app.post("/api/v1/ingest")
async def ingest(request: IngestRequest):
    """
    Ingest a document or note into the system.
    
    Request body:
    - text: Document content (required)
    - source: Source identifier (optional)
    - tags: List of tags (optional)
    - metadata: Additional metadata (optional)
    
    Returns:
    - document_id: Unique document identifier
    - chunk_count: Number of chunks created
    - message: Success message
    """
    try:
        result = ingest_document(
            text=request.text,
            source=request.source,
            tags=request.tags,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ingest")
async def list_docs(limit: int = 100):
    """
    List all ingested documents.
    
    Query params:
    - limit: Maximum number of documents to return (default: 100)
    
    Returns:
    - documents: List of document metadata
    - total: Total count
    """
    try:
        result = list_documents(limit=limit)
        return result
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/ingest/{document_id}")
async def delete_doc(document_id: str):
    """
    Delete a document and all its chunks.
    
    Path params:
    - document_id: Document ID to delete
    
    Returns:
    - 204 No Content on success
    """
    try:
        delete_document(document_id)
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/clear-all")
async def clear_all_data():
    """
    Clear all stored embeddings and reset the vector database.
    This will delete the entire index and recreate it empty.
    
    Returns:
    - message: Success message with count of deleted items
    """
    try:
        from src.store import delete_index, initialize_endee_index
        
        # Delete the index
        delete_index()
        logger.info("Deleted existing index")
        
        # Recreate empty index
        initialize_endee_index()
        logger.info("Recreated empty index")
        
        return {"message": "All data cleared successfully. Index has been reset."}
    except Exception as e:
        logger.error(f"Clear all failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query")
async def query(request: QueryRequest):
    """
    Perform RAG query: retrieve context and generate answer.
    
    Request body:
    - question: User question (required)
    - top_k: Number of context chunks (default: 5)
    - include_sources: Include source citations (default: true)
    - filters: Optional filters like {"tags": ["ml"]}
    
    Returns:
    - answer: Generated answer
    - sources: List of source chunks with scores
    - timings: Performance metrics
    """
    try:
        result = query_rag(
            question=request.question,
            top_k=request.top_k or 5,
            include_sources=request.include_sources if request.include_sources is not None else True,
            filters=request.filters
        )
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search")
async def search(request: SearchRequest):
    """
    Perform semantic search without LLM generation.
    
    Request body:
    - query: Search query (required)
    - top_k: Maximum results (default: 10)
    - threshold: Minimum similarity threshold (default: 0.0)
    - filters: Optional filters
    
    Returns:
    - results: List of matching chunks
    - total: Result count
    - timings: Performance metrics
    """
    try:
        result = search_semantic(
            query=request.query,
            top_k=request.top_k or 10,
            threshold=request.threshold or 0.0,
            filters=request.filters
        )
        return result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/summarize")
async def summarize(request: SummarizeRequest):
    """
    Generate AI-powered summary for a topic.
    
    Request body:
    - topic: Topic to summarize (required)
    - top_k: Number of context chunks (default: 10)
    - max_length: Maximum summary length in words (default: 500)
    - filters: Optional filters
    
    Returns:
    - summary: Generated summary
    - topic: Topic name
    - chunk_count: Number of chunks used
    - timings: Performance metrics
    """
    try:
        result = summarize_topic(
            topic=request.topic,
            top_k=request.top_k or 10,
            max_length=request.max_length or 500,
            filters=request.filters
        )
        return result
    except Exception as e:
        logger.error(f"Summarize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
