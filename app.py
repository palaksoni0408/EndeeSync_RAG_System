#!/usr/bin/env python3
"""
Main application entry point for RAG system.
Provides CLI interface for ingestion and querying.
"""

import argparse
import logging
import sys
from pathlib import Path

from src import config
from src.ingest import process_documents
from src.embed import embed_chunks
from src.store import store_embeddings, delete_index
from src.rag import generate_answer

# Set up logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("rag_system.log")
    ]
)
logger = logging.getLogger(__name__)


def run_ingestion(data_dir: Path = None):
    """
    Run the complete ingestion pipeline.
    
    Args:
        data_dir: Directory containing documents (defaults to config.RAW_DOCS_DIR)
    """
    logger.info("=" * 80)
    logger.info("Starting Document Ingestion Pipeline")
    logger.info("=" * 80)
    
    try:
        # Step 1: Process documents
        logger.info("\nStep 1/3: Loading and chunking documents")
        chunks = process_documents(data_dir)
        
        if not chunks:
            logger.error("No documents found or processed. Please add documents to data/raw_docs/")
            return
        
        logger.info(f"Processed {len(chunks)} chunks")
        
        # Step 2: Generate embeddings
        logger.info("\nStep 2/3: Generating embeddings")
        chunks_with_embeddings = embed_chunks(chunks)
        logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
        
        # Step 3: Store in Endee
        logger.info("\nStep 3/3: Storing in Endee vector database")
        store_embeddings(chunks_with_embeddings)
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ Ingestion Complete!")
        logger.info(f"✓ Indexed {len(chunks)} chunks from documents")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n✗ Ingestion failed: {e}")
        raise


def run_query(query: str, top_k: int = 5):
    """
    Run a query against the RAG system.
    
    Args:
        query: User query string
        top_k: Number of context chunks to retrieve
    """
    logger.info("=" * 80)
    logger.info("Processing Query")
    logger.info("=" * 80)
    
    try:
        result = generate_answer(query, top_k=top_k)
        
        # Display results
        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(result["answer"])
        
        if "sources" in result:
            print("\n" + "=" * 80)
            print(f"SOURCES ({result['num_chunks']} chunks retrieved)")
            print("=" * 80)
            for i, source in enumerate(result["sources"], 1):
                print(f"\n[{i}] {source['source']} (similarity: {source['similarity']:.4f})")
                print(f"    {source['excerpt']}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"\n✗ Query failed: {e}")
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Endee server is running")
        print("2. Documents have been ingested (run with --ingest first)")
        print("3. OpenAI API key is set in .env file")


def run_interactive():
    """Run interactive query mode."""
    print("\n" + "=" * 80)
    print("RAG System - Interactive Mode")
    print("=" * 80)
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            run_query(query)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"\nError: {e}")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="RAG System with Endee Vector Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest documents
  python app.py --ingest
  
  # Query the system
  python app.py --query "What is semantic search?"
  
  # Interactive mode
  python app.py --interactive
  
  # Delete index and start fresh
  python app.py --delete-index
        """
    )
    
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Run document ingestion pipeline"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Query the RAG system"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive query mode"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of context chunks to retrieve (default: 5)"
    )
    
    parser.add_argument(
        "--delete-index",
        action="store_true",
        help="Delete the Endee index"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Custom directory for documents (default: data/raw_docs)"
    )
    
    args = parser.parse_args()
    
    # Handle commands
    if args.delete_index:
        confirm = input(f"Are you sure you want to delete index '{config.ENDEE_INDEX_NAME}'? (yes/no): ")
        if confirm.lower() == 'yes':
            delete_index()
            print("Index deleted successfully")
        else:
            print("Deletion cancelled")
        return
    
    if args.ingest:
        data_dir = Path(args.data_dir) if args.data_dir else None
        run_ingestion(data_dir)
        return
    
    if args.query:
        run_query(args.query, top_k=args.top_k)
        return
    
    if args.interactive:
        run_interactive()
        return
    
    # No arguments provided
    parser.print_help()


if __name__ == "__main__":
    main()
