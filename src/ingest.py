"""
Document ingestion module.
Loads documents from the data directory and chunks them for embedding.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
import hashlib

from pypdf import PdfReader

from . import config

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def load_text_file(file_path: Path) -> str:
    """
    Load content from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading text file {file_path}: {e}")
        return ""


def load_pdf_file(file_path: Path) -> str:
    """
    Load content from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error loading PDF file {file_path}: {e}")
        return ""


def load_documents(directory: Path) -> List[Dict[str, Any]]:
    """
    Load all supported documents from a directory.
    
    Args:
        directory: Path to the directory containing documents
        
    Returns:
        List of dictionaries with 'path', 'name', and 'content' keys
    """
    documents = []
    
    if not directory.exists():
        logger.warning(f"Directory {directory} does not exist")
        return documents
    
    # Recursively find all supported files
    for ext in config.SUPPORTED_EXTENSIONS:
        for file_path in directory.rglob(f"*{ext}"):
            logger.info(f"Loading document: {file_path.name}")
            
            # Load content based on file type
            if ext == ".pdf":
                content = load_pdf_file(file_path)
            else:
                content = load_text_file(file_path)
            
            if content.strip():  # Only add non-empty documents
                documents.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "content": content
                })
            else:
                logger.warning(f"Skipping empty document: {file_path.name}")
    
    logger.info(f"Loaded {len(documents)} documents")
    return documents


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum number of characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # If this isn't the last chunk, try to break at sentence/word boundary
        if end < text_length:
            # Look for sentence boundary (. ! ?)
            for boundary_char in ['. ', '! ', '? ', '\n\n']:
                boundary_idx = text.rfind(boundary_char, start + chunk_size // 2, end)
                if boundary_idx != -1:
                    end = boundary_idx + len(boundary_char)
                    break
            else:
                # No sentence boundary found, look for word boundary
                space_idx = text.rfind(' ', start, end)
                if space_idx != -1 and space_idx > start:
                    end = space_idx
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start <= chunks[-1][:overlap].__len__() if chunks else 0:
            start = end  # Prevent infinite loop on very small texts
    
    return chunks


def create_chunk_id(doc_name: str, chunk_index: int) -> str:
    """
    Create a unique ID for a chunk.
    
    Args:
        doc_name: Document name
        chunk_index: Index of the chunk within the document
        
    Returns:
        Unique chunk ID
    """
    # Create hash-based ID for uniqueness
    content = f"{doc_name}_{chunk_index}"
    hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{doc_name}_chunk{chunk_index}_{hash_suffix}"


def process_documents(directory: Path = None) -> List[Dict[str, Any]]:
    """
    Complete document processing pipeline.
    Loads documents and chunks them with metadata.
    
    Args:
        directory: Directory containing documents (defaults to config.RAW_DOCS_DIR)
        
    Returns:
        List of chunk dictionaries with id, text, and metadata
    """
    if directory is None:
        directory = config.RAW_DOCS_DIR
    
    logger.info(f"Starting document processing from {directory}")
    
    # Load documents
    documents = load_documents(directory)
    
    if not documents:
        logger.warning("No documents found to process")
        return []
    
    # Chunk all documents
    all_chunks = []
    total_chunks = 0
    
    for doc in documents:
        # Chunk the document
        chunks = chunk_text(
            doc["content"],
            config.CHUNK_SIZE,
            config.CHUNK_OVERLAP
        )
        
        logger.info(f"Document '{doc['name']}' split into {len(chunks)} chunks")
        
        # Create structured chunk objects
        for i, text_chunk in enumerate(chunks):
            chunk_obj = {
                "id": create_chunk_id(doc["name"], i),
                "text": text_chunk,
                "metadata": {
                    "source": doc["name"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source_path": doc["path"]
                }
            }
            all_chunks.append(chunk_obj)
            total_chunks += 1
    
    logger.info(f"Processing complete: {total_chunks} total chunks from {len(documents)} documents")
    return all_chunks


if __name__ == "__main__":
    # Test the ingestion pipeline
    chunks = process_documents()
    print(f"\nProcessed {len(chunks)} chunks")
    if chunks:
        print(f"\nExample chunk:")
        print(f"ID: {chunks[0]['id']}")
        print(f"Text preview: {chunks[0]['text'][:200]}...")
        print(f"Metadata: {chunks[0]['metadata']}")
