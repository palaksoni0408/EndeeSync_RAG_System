# Alternative Setup: Run Without Docker

Since Docker is not installed, you have two options:

## Option A: Install Docker (Recommended)

1. Download Docker Desktop for Mac (Apple Silicon):
   https://www.docker.com/products/docker-desktop/

2. Install and start Docker Desktop

3. Run Endee:
   ```bash
   docker compose up -d
   ```

## Option B: Mock Endee Server (For Demo Purposes Only)

For **demonstration purposes only**, I can create a mock Endee server that simulates the vector database locally using in-memory storage. This won't be production-ready but will let you test the RAG pipeline.

**Note:** This is NOT the real Endee and won't have the same performance characteristics.

Would you like me to create a mock Endee server for testing, or do you prefer to install Docker?

## Option C: Try the Code Without Full Integration

You can test individual components without Endee:

```bash
# Test document ingestion (no Endee needed)
python -c "from src.ingest import process_documents; chunks = process_documents(); print(f'Processed {len(chunks)} chunks')"

# Test embedding generation (no Endee needed)
python -c "from src.embed import embed_query; emb = embed_query('test query'); print(f'Embedding shape: {emb.shape}')"
```

These tests will verify that the document processing and embedding generation work correctly.
