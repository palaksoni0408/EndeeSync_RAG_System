# RAG System Demo Script & Walkthrough

**Presentation Script for Technical Interviews & Demonstrations**

---

## Demo Overview (30 seconds)

**Opening Statement:**
> "I built a production-grade Retrieval-Augmented Generation system using Endee vector database. This system can ingest documents, generate semantic embeddings, perform similarity search, and generate contextual answers using GPT-3.5. Let me show you how it works end-to-end."

**Tech Stack Snapshot:**
- **Vector DB:** Endee (HNSW algorithm, cosine similarity)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **LLM:** OpenAI GPT-3.5-turbo
- **Pipeline:** Document Processing → Chunking → Embedding → Storage → Retrieval → Generation

---

## Demo Part 1: System Setup (2 minutes)

### Show the Project Structure

```bash
cd /Users/kunalkumargupta/Desktop/endee
tree -L 2 -I 'venv|__pycache__|.git'
```

**Talking Points:**
- "The project is modular with clear separation of concerns"
- "Each component has a dedicated module: ingestion, embedding, storage, retrieval, and generation"
- "Configuration is centralized in config.py for easy deployment"

### Show the Architecture

```bash
cat README.md | grep -A 20 "System Architecture"
```

**Explain:**
> "The ingestion pipeline loads documents, chunks them intelligently with overlap, generates 384-dimensional embeddings, and stores them in Endee with metadata. The query pipeline embeds the question, retrieves top-k similar chunks using HNSW search, constructs a prompt, and generates an answer with GPT-3.5."

---

## Demo Part 2: Document Ingestion (3 minutes)

### Show Sample Documents

```bash
echo "=== Sample Documents ==="
ls -lh data/raw_docs/
echo ""
echo "=== Preview of intro_to_rag.md ==="
head -20 data/raw_docs/intro_to_rag.md
```

**Talking Points:**
- "I've created sample documents covering RAG concepts, vector databases, and Endee basics"
- "The system supports .txt, .md, and .pdf formats"
- "Let me show you the ingestion process"

### Run Ingestion

```bash
echo "=== Activating Environment ==="
source venv/bin/activate

echo ""
echo "=== Starting Ingestion Pipeline ==="
python app.py --ingest
```

**What to Point Out During Execution:**
1. **Document Loading:** "Loading 3 documents from the raw_docs directory"
2. **Chunking:** "Split into 31 chunks with 512 character size and 50 character overlap"
3. **Embedding:** "Using all-MiniLM-L6-v2 model to generate 384-dimensional vectors"
4. **Storage:** "Upserting to Endee in batches of 1000 (respecting API limits)"

**Expected Output Highlights:**
```
✓ Loaded 3 documents
✓ Document 'endee_basics.txt' split into 11 chunks
✓ Document 'vector_databases.md' split into 13 chunks
✓ Document 'intro_to_rag.md' split into 7 chunks
✓ Processing complete: 31 total chunks
✓ Generated embeddings with shape: (31, 384)
✓ Upserted batch 1: 31 vectors
✓ Ingestion Complete!
```

### Verify Index

```bash
echo ""
echo "=== Verifying Endee Index ==="
python -c "
from src.store import get_endee_client
client = get_endee_client()
idx = client.get_index('rag_documents')
info = idx.describe()
print(f'Index: {info[\"name\"]}')
print(f'Vectors stored: {info[\"count\"]}')
print(f'Dimension: {info[\"dimension\"]}')
print(f'Space type: {info[\"space_type\"]}')
print(f'Precision: {info[\"precision\"]}')
"
```

**Talking Point:**
> "We now have 31 vectors stored in Endee with cosine similarity metric and INT8D precision for 8x compression."

---

## Demo Part 3: Query & Retrieval (5 minutes)

### Query 1: Simple Fact Retrieval

```bash
echo ""
echo "=== Query 1: What is semantic search? ==="
python app.py --query "What is semantic search?"
```

**Expected Behavior:**
1. Query gets embedded using same model
2. Endee performs similarity search
3. Top 5 chunks retrieved with similarity scores
4. GPT-3.5 synthesizes answer from context
5. Sources shown with excerpts

**Talking Points:**
- "Notice the similarity score of the top result (0.53+)"
- "The answer is grounded in the retrieved context"
- "Source attribution shows which documents contributed"

### Query 2: Conceptual Explanation

```bash
echo ""
echo "=== Query 2: How does HNSW algorithm work? ==="
python app.py --query "How does HNSW algorithm work?"
```

**Talking Points:**
- "This tests the system's ability to synthesize from multiple chunks"
- "HNSW (Hierarchical Navigable Small World) is mentioned in the vector_databases.md doc"
- "Watch how it combines information from different sources"

### Query 3: Comparison Query

```bash
echo ""
echo "=== Query 3: What are the benefits of RAG over fine-tuning? ==="
python app.py --query "What are the benefits of RAG over fine-tuning?"
```

**Talking Points:**
- "This requires understanding comparative information"
- "The system should retrieve chunks discussing both approaches"
- "Notice how the answer balances different perspectives"

### Query 4: Out-of-Context Test

```bash
echo ""
echo "=== Query 4: What is the weather today? ==="
python app.py --query "What is the weather today?"
```

**Expected Behavior:**
> "Based on the provided context, I don't have information about the weather."

**Talking Point:**
> "The system correctly identifies when it doesn't have relevant information and doesn't hallucinate."

---

## Demo Part 4: Interactive Mode (2 minutes)

```bash
echo ""
echo "=== Starting Interactive Mode ==="
python app.py --interactive
```

**Demo Script for Interactive:**
```
Query> What is a vector database?
[Wait for answer]

Query> Explain the difference between dense and hybrid indexes
[Wait for answer]

Query> What is Endee used for?
[Wait for answer]

Query> exit
```

**Talking Points:**
- "Interactive mode allows natural conversation flow"
- "Each query maintains context from the same document set"
- "Useful for exploratory research on document collections"

---

## Demo Part 5: Code Walkthrough (3 minutes)

### Show Core Components

**1. Configuration**
```bash
echo "=== Configuration Module ==="
head -50 src/config.py
```

**Talking Points:**
- "Centralized configuration with environment variable support"
- "Easy to adjust chunk size, top-k, embedding model"
- "Supports different deployment environments"

**2. Embedding Generation**
```bash
echo ""
echo "=== Embedding Module (Key Functions) ==="
grep -A 10 "def embed_texts" src/embed.py
```

**Talking Points:**
- "Singleton pattern for model loading (efficiency)"
- "Batch processing for performance"
- "Same model used for documents and queries (critical for similarity)"

**3. RAG Pipeline**
```bash
echo ""
echo "=== RAG Pipeline (Core Logic) ==="
grep -A 20 "def generate_answer" src/rag.py
```

**Talking Points:**
- "Orchestrates retrieval and generation"
- "Constructs prompt with retrieved context"
- "Handles both OpenAI and local LLM fallback"

---

## Demo Part 6: Testing with New Data (3 minutes)

### Add Custom Document

```bash
echo ""
echo "=== Creating Custom Test Document ==="
cat > data/raw_docs/ml_basics.txt << 'EOF'
Machine Learning (ML) is a subset of artificial intelligence that enables systems to learn from data.

Key ML Paradigms:
1. Supervised Learning: Training with labeled examples
2. Unsupervised Learning: Finding patterns without labels
3. Reinforcement Learning: Learning through trial and error

Deep Learning uses neural networks with multiple layers to learn hierarchical representations.
Popular frameworks include TensorFlow, PyTorch, and JAX.

Transfer learning allows models trained on one task to be adapted for another related task.
This is particularly useful when labeled data is scarce.
EOF

echo "Document created successfully!"
cat data/raw_docs/ml_basics.txt
```

### Re-ingest

```bash
echo ""
echo "=== Re-ingesting with New Document ==="
python app.py --ingest
```

**Talking Point:**
> "The system now adds the new document without losing existing data. Total chunks should increase."

### Test New Knowledge

```bash
echo ""
echo "=== Testing New Document ==="
python app.py --query "What are the main types of machine learning?"
python app.py --query "What is transfer learning?"
```

**Expected Behavior:**
- Retrieves chunks from the newly added document
- Synthesizes answer about ML paradigms
- Shows source attribution to ml_basics.txt

**Talking Points:**
- "Notice the new document appears in sources"
- "The system seamlessly integrates new knowledge"
- "Similarity search finds the most relevant chunks regardless of which document they're from"

---

## Demo Part 7: Performance & Metrics (2 minutes)

### Show Retrieval Quality

```bash
echo ""
echo "=== Analyzing Retrieval Quality ==="
python -c "
from src.retrieve import retrieve_context

# Test retrieval for various queries
queries = [
    'What is semantic search?',
    'Explain HNSW algorithm',
    'What is RAG?'
]

for q in queries:
    print(f'\nQuery: {q}')
    results = retrieve_context(q, top_k=3)
    for i, r in enumerate(results, 1):
        print(f'  [{i}] Similarity: {r[\"similarity\"]:.4f} - {r[\"source\"]}')
"
```

**Talking Points:**
- "Higher similarity scores indicate better matches"
- "Typical good match: 0.5-0.9 similarity"
- "Multiple sources suggests comprehensive coverage"

### Show System Metrics

```bash
echo ""
echo "=== System Performance Metrics ==="
echo "Index Statistics:"
python -c "
from src.store import get_endee_client
client = get_endee_client()
idx = client.get_index('rag_documents')
info = idx.describe()
print(f'  Total vectors: {info[\"count\"]}')
print(f'  Dimension: {info[\"dimension\"]}')
print(f'  HNSW M parameter: {info.get(\"M\", \"N/A\")}')
print(f'  Precision: {info[\"precision\"]}')
"

echo ""
echo "Model Statistics:"
python -c "
from src.embed import get_embedding_model
model = get_embedding_model()
print(f'  Model: {model._model_card[\"model_id\"]}')
print(f'  Embedding dimension: {model.get_sentence_embedding_dimension()}')
print(f'  Max sequence length: {model.max_seq_length}')
"
```

---

## Demo Part 8: Production Features (2 minutes)

### Show Error Handling

```bash
echo ""
echo "=== Testing Error Handling: Invalid Query ==="
# This will gracefully handle empty results
python app.py --query "xyzqwertyfakequery12345"
```

**Expected:** System returns answer saying no information available

### Show Logging

```bash
echo ""
echo "=== Viewing Application Logs ==="
tail -20 rag_system.log
```

**Talking Points:**
- "Comprehensive logging at INFO, WARNING, ERROR levels"
- "Helps debug issues in production"
- "Tracks performance metrics"

### Show Configuration Flexibility

```bash
echo ""
echo "=== Configuration Options ==="
python -c "
from src import config
print('Embedding Model:', config.EMBEDDING_MODEL_NAME)
print('Vector Dimension:', config.VECTOR_DIMENSION)
print('Chunk Size:', config.CHUNK_SIZE)
print('Chunk Overlap:', config.CHUNK_OVERLAP)
print('Default Top-K:', config.DEFAULT_TOP_K)
print('Space Type:', config.SPACE_TYPE)
print('Precision:', config.PRECISION)
"
```

**Talking Point:**
> "All parameters are configurable without code changes. Easy to tune for different use cases."

---

## Demo Part 9: Scalability Discussion (1 minute)

### Current Capabilities

```bash
echo ""
echo "=== Current System State ==="
echo "Documents processed: $(ls data/raw_docs/ | wc -l)"
echo "Total chunks: $(python -c 'from src.store import get_endee_client; print(get_endee_client().get_index(\"rag_documents\").describe()[\"count\"])')"
echo "Storage format: Endee (persistent on Docker volume)"
```

**Scalability Talking Points:**
- "Currently handling 4 documents, 35+ chunks"
- "Can scale to thousands of documents with same architecture"
- "Endee uses HNSW for sub-linear search time (log n complexity)"
- "Batch processing supports large document sets"
- "Docker deployment makes it portable and scalable"

---

## Demo Part 10: Closing & Q&A (2 minutes)

### Summary of What Was Demonstrated

**Checklist:**
✅ Document ingestion pipeline (PDF, MD, TXT)  
✅ Semantic embedding generation (384d vectors)  
✅ Vector storage in Endee (HNSW indexing)  
✅ Similarity-based retrieval (cosine similarity)  
✅ LLM-powered answer generation (GPT-3.5)  
✅ Source attribution and transparency  
✅ Error handling and logging  
✅ Easy integration of new documents  
✅ Production-ready architecture  

### Key Technical Achievements

**Architecture:**
- Modular design with 7 separate components
- Configuration-driven, environment-aware
- Comprehensive error handling and logging
- Virtual environment for dependency isolation

**Vector Database Integration:**
- Implemented Endee storage with proper batch handling
- Configured HNSW for optimal performance
- Used INT8D precision for 8x compression
- Handled API quirks (index creation, response formats)

**RAG Pipeline:**
- Intelligent text chunking with overlap
- Consistent embedding generation
- Context-aware prompt construction
- Fallback LLM support

**Production Quality:**
- Type hints throughout
- Comprehensive logging
- CLI and interactive modes
- Validation and error messages
- Documentation (README, guides, testing docs)

### Common Interview Questions & Answers

**Q: Why did you choose Endee over other vector databases?**
> "Endee was specified for this project, but it offers advantages like efficient HNSW implementation, flexible precision options, and simple API. In production, I'd evaluate based on scale, cost, and ecosystem support - options like Pinecone, Weaviate, or Qdrant."

**Q: How do you handle document updates?**
> "Currently additive - re-running ingestion adds new documents. For updates, I'd implement versioning with chunk IDs that include document hash, allowing deletion and re-insertion of modified documents."

**Q: What about prompt injection or hallucination?**
> "I include explicit instructions in the prompt to only use provided context. For production, I'd add output validation, confidence scoring, and potentially a second LLM to verify factuality."

**Q: How would you scale this to millions of documents?**
> "Three approaches: 1) Distributed Endee deployment with sharding, 2) Hierarchical retrieval (coarse filter then fine search), 3) Hybrid search combining keyword and semantic matching. Also implement caching for common queries."

**Q: What metrics would you use to evaluate quality?**
> "Retrieval metrics: Recall@k, precision, MRR. Generation metrics: ROUGE, BLEU for reference answers. Human evaluation for coherence and factuality. A/B testing for user satisfaction."

---

## Bonus: Advanced Features Demo (Optional, 3 minutes)

### Custom Top-K Parameter

```bash
echo "=== Comparing Different Top-K Values ==="
echo ""
echo "Top-K = 3:"
python app.py --query "What is semantic search?" --top-k 3 | grep "SOURCES"

echo ""
echo "Top-K = 10:"
python app.py --query "What is semantic search?" --top-k 10 | grep "SOURCES"
```

**Talking Point:**
> "Higher top-k provides more context but may include less relevant chunks. Trade-off between coverage and precision."

### Index Management

```bash
echo ""
echo "=== Index Management Demo ==="
echo "Current index:"
python -c "from src.store import get_endee_client; print(get_endee_client().list_indexes())"

echo ""
echo "Creating backup index:"
python -c "
from src.store import get_endee_client, get_precision_enum
from src import config
client = get_endee_client()
try:
    client.create_index(
        name='rag_documents_backup',
        dimension=384,
        space_type='cosine',
        precision=get_precision_enum('INT8D')
    )
    print('Backup index created!')
except:
    print('Backup already exists or other error')
"

echo ""
echo "All indexes:"
python -c "from src.store import get_endee_client; print(get_endee_client().list_indexes())"
```

---

## Script Timing Guide

**Total Demo Time: ~20-25 minutes**

- Introduction & Setup: 2 min
- Ingestion Pipeline: 3 min
- Query Demonstrations: 5 min
- Interactive Mode: 2 min
- Code Walkthrough: 3 min
- New Data Testing: 3 min
- Metrics & Performance: 2 min
- Production Features: 2 min
- Scalability Discussion: 1 min
- Closing & Q&A: 2 min
- Bonus (optional): 3 min

**For 10-Minute Version:**
- Skip: Code walkthrough, new data testing, bonus
- Focus: Ingestion → Queries → Results → Quick Q&A

**For 5-Minute Version:**
- Show: Pre-run ingestion → 2 queries → Source attribution → Key architecture slide

---

## Presentation Tips

### Before Demo
1. ✅ Test all commands work
2. ✅ Clear terminal for clean output
3. ✅ Have Endee running (`docker ps`)
4. ✅ Virtual environment ready
5. ✅ Browser tabs ready (README, code files)

### During Demo
1. **Speak while waiting** for commands to run
2. **Highlight key outputs** in real-time
3. **Explain "why"** not just "what"
4. **Show actual code** when discussing architecture
5. **Handle errors gracefully** if they occur

### After Demo
1. Offer to dive deeper into any component
2. Have README.md open for reference
3. Be ready to discuss trade-offs and alternatives
4. Connect to real-world use cases

---

## Emergency Backup Plan

If something fails during demo:

**Endee not running:**
```bash
docker compose up -d
# Wait 10 seconds
```

**Import error:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Query fails:**
```bash
# Show pre-run screenshot or logs
cat rag_system.log | grep "ANSWER"
```

**No time for live demo:**
```bash
# Show walkthrough.md instead
cat walkthrough.md
```

---

**Remember:** The goal is to demonstrate technical competence, architectural thinking, and production awareness. Focus on the "why" behind decisions, not just the "what" of implementation.

Good luck with your demo! 🚀
