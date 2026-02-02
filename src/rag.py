"""
RAG (Retrieval-Augmented Generation) module.
Combines retrieval with LLM generation for grounded answers.
"""

import logging
from typing import List, Dict, Any, Optional
import os

from . import config
from .retrieve import retrieve_context

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Lazy import LLM dependencies
_openai_client = None
_groq_client = None
_local_llm = None


def get_openai_client():
    """Get or initialize OpenAI client."""
    global _openai_client
    
    if _openai_client is None:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            raise
    
    return _openai_client


def get_local_llm():
    """Get or initialize local LLM model."""
    global _local_llm
    
    if _local_llm is None:
        try:
            from transformers import pipeline
            logger.info(f"Loading local LLM: {config.LOCAL_LLM_MODEL}")
            _local_llm = pipeline(
                "text-generation",
                model=config.LOCAL_LLM_MODEL,
                max_length=config.LLM_MAX_TOKENS,
                device=-1  # CPU
            )
            logger.info("Local LLM initialized")
        except Exception as e:
            logger.error(f"Error initializing local LLM: {e}")
            raise
    
    return _local_llm


def get_groq_client():
    """Get or initialize Groq client."""
    global _groq_client
    
    if _groq_client is None:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=config.GROQ_API_KEY)
            logger.info("Groq client initialized")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            raise
    
    return _groq_client


def construct_prompt(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Construct RAG prompt with retrieved context.
    
    Args:
        query: User query
        context_chunks: List of retrieved context chunks
        
    Returns:
        Formatted prompt string
    """
    # Format context
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get("source", "unknown")
        text = chunk.get("text", "")
        context_parts.append(f"[{i}] From {source}:\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    # Use template from config
    prompt = config.RAG_PROMPT_TEMPLATE.format(
        context=context_str,
        query=query
    )
    
    return prompt


def call_openai_llm(prompt: str) -> str:
    """
    Call OpenAI API for generation.
    
    Args:
        prompt: Formatted prompt
        
    Returns:
        Generated answer
    """
    client = get_openai_client()
    
    logger.info("Calling OpenAI API for generation")
    
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS
        )
        
        answer = response.choices[0].message.content
        logger.info("OpenAI generation complete")
        
        return answer
    
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        raise


def call_local_llm(prompt: str) -> str:
    """
    Call local LLM for generation.
    
    Args:
        prompt: Formatted prompt
        
    Returns:
        Generated answer
    """
    llm = get_local_llm()
    
    logger.info("Calling local LLM for generation")
    
    try:
        result = llm(prompt, max_length=config.LLM_MAX_TOKENS, do_sample=True, temperature=config.LLM_TEMPERATURE)
        answer = result[0]["generated_text"]
        logger.info("Local LLM generation complete")
        
        return answer
    
    except Exception as e:
        logger.error(f"Error calling local LLM: {e}")
        raise


def call_groq_llm(prompt: str) -> str:
    """
    Call Groq API for generation.
    
    Args:
        prompt: Formatted prompt
        
    Returns:
        Generated answer
    """
    client = get_groq_client()
    
    logger.info("Calling Groq API for generation")
    
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS
        )
        
        answer = response.choices[0].message.content
        logger.info("Groq generation complete")
        
        return answer
    
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        raise



def call_llm(prompt: str) -> str:
    """
    Call LLM with fallback chain: OpenAI -> Groq -> Local LLM.
    
    Args:
        prompt: Formatted prompt
        
    Returns:
        Generated answer
    """
    # Try OpenAI first (if available)
    if config.USE_OPENAI:
        try:
            logger.info("Attempting OpenAI LLM (primary)")
            return call_openai_llm(prompt)
        except Exception as e:
            logger.warning(f"OpenAI failed: {e}, falling back to Groq")
    
    # Try Groq second (if available)
    if config.USE_GROQ:
        try:
            logger.info("Attempting Groq LLM (fallback 1)")
            return call_groq_llm(prompt)
        except Exception as e:
            logger.warning(f"Groq failed: {e}, falling back to local LLM")
    
    # Fall back to local LLM (always available)
    logger.info("Using local LLM (fallback 2)")
    return call_local_llm(prompt)


def generate_answer(
    query: str,
    top_k: int = None,
    ef: int = None,
    index_name: str = None,
    include_sources: bool = True
) -> Dict[str, Any]:
    """
    Complete RAG pipeline: retrieve context and generate answer.
    
    Args:
        query: User query
        top_k: Number of context chunks to retrieve
        ef: Search quality parameter
        index_name: Name of the index to query
        include_sources: Whether to include source information in response
        
    Returns:
        Dictionary with answer, sources, and metadata
    """
    logger.info(f"Starting RAG pipeline for query: '{query[:100]}...'")
    
    if top_k is None:
        top_k = config.DEFAULT_TOP_K
    
    try:
        # Step 1: Retrieve relevant context
        logger.info("Step 1: Retrieving context")
        context_chunks = retrieve_context(query, top_k=top_k, ef=ef, index_name=index_name)
        
        if not context_chunks:
            logger.warning("No context retrieved")
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": [],
                "num_chunks": 0
            }
        
        logger.info(f"Retrieved {len(context_chunks)} context chunks")
        
        # Step 2: Construct prompt
        logger.info("Step 2: Constructing prompt")
        prompt = construct_prompt(query, context_chunks)
        
        # Step 3: Generate answer
        logger.info("Step 3: Generating answer with LLM")
        answer = call_llm(prompt)
        
        # Step 4: Prepare response
        response = {
            "answer": answer,
            "num_chunks": len(context_chunks)
        }
        
        if include_sources:
            sources = [
                {
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "similarity": chunk["similarity"],
                    "excerpt": chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]
                }
                for chunk in context_chunks
            ]
            response["sources"] = sources
        
        logger.info("RAG pipeline complete")
        
        return response
    
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        raise


if __name__ == "__main__":
    # Test RAG pipeline
    test_query = "What is semantic search and how does it work?"
    
    print(f"Testing RAG pipeline with query: '{test_query}'")
    print("-" * 80)
    
    try:
        result = generate_answer(test_query, top_k=3)
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nBased on {result['num_chunks']} retrieved chunks")
        
        if "sources" in result:
            print(f"\nSources:")
            for i, source in enumerate(result["sources"], 1):
                print(f"\n{i}. {source['source']} (similarity: {source['similarity']:.4f})")
                print(f"   {source['excerpt']}")
    
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. Endee server is running")
        print("2. Documents have been ingested")
        print("3. OpenAI API key is set (or use local LLM)")
