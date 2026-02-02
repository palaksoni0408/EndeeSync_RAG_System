# RAG System Testing Guide

Quick guide to test the RAG system with your own documents.

---

## Step 1: Add Your Documents

Place your documents in the `data/raw_docs/` directory:

```bash
cd /Users/kunalkumargupta/Desktop/endee

# Option A: Copy your files
cp /path/to/your/document.pdf data/raw_docs/
cp /path/to/your/notes.txt data/raw_docs/
cp /path/to/your/report.md data/raw_docs/

# Option B: Create a new document directly
cat > data/raw_docs/my_custom_doc.txt << 'EOF'
Your content here...
Add as much text as you want.
The system will automatically chunk it.
EOF
```

**Supported formats:**
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents

---

## Step 2: Clear Old Data (Optional)

If you want to start fresh:

```bash
# Activate virtual environment
source venv/bin/activate

# Delete existing index
python app.py --delete-index

# Confirm deletion
# The system will ask for confirmation
```

---

## Step 3: Ingest New Documents

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Run ingestion
python app.py --ingest

# Expected output:
# ✓ Loaded X documents
# ✓ Created Y chunks
# ✓ Generated embeddings
# ✓ Stored in Endee
```

**What happens:**
1. System loads all documents from `data/raw_docs/`
2. Splits them into chunks (512 chars with 50 char overlap)
3. Generates 384-dimensional embeddings
4. Stores in Endee vector database

---

## Step 4: Test with Queries

### Single Query Mode

```bash
python app.py --query "Your question here"
```

**Example queries:**

```bash
# Query about your document content
python app.py --query "What are the main topics discussed?"

# Specific fact retrieval
python app.py --query "What is the definition of X?"

# Comparison query
python app.py --query "How does A compare to B?"
```

### Interactive Mode

```bash
python app.py --interactive
```

Then type your questions one by one:
```
Query> What is semantic search?
[Answer displayed with sources]

Query> Explain vector databases
[Answer displayed with sources]

Query> exit
[Exits interactive mode]
```

---

## Step 5: Verify Results

### Check Retrieved Chunks

The system shows which documents were used:

```
================================================================================
SOURCES (5 chunks retrieved)
================================================================================

[1] your_document.pdf (similarity: 0.8234)
    The main topic is about...

[2] your_notes.txt (similarity: 0.7654)
    Another relevant passage...
```

### Adjust Retrieval Parameters

If results aren't good enough:

```bash
# Retrieve more chunks (default: 5)
python app.py --query "Your question" --top-k 10

# Custom configuration in src/config.py
# Edit these values:
DEFAULT_TOP_K = 10      # Retrieve more chunks
DEFAULT_EF = 256        # Higher search quality (slower)
CHUNK_SIZE = 1024       # Larger chunks (more context)
```

---

## Step 6: Verify Index Contents

```bash
# Check what's in the index
source venv/bin/activate
python -c "
from src.store import get_endee_client
client = get_endee_client()
indexes = client.list_indexes()
print(f'Indexes: {indexes}')

# Get index details
index = client.get_index('rag_documents')
info = index.describe()
print(f'Index info: {info}')
print(f'Total vectors: {info[\"count\"]}')
"
```

---

## Common Testing Workflows

### Test Case 1: Add Single New Document

```bash
# 1. Create test document
echo "Machine learning is a subset of artificial intelligence..." > data/raw_docs/ml_basics.txt

# 2. Re-ingest (adds to existing index)
source venv/bin/activate
python app.py --ingest

# 3. Test query
python app.py --query "What is machine learning?"
```

### Test Case 2: Replace All Documents

```bash
# 1. Clear old data
source venv/bin/activate
python app.py --delete-index

# 2. Remove old documents
rm data/raw_docs/*.{txt,md,pdf}

# 3. Add new documents
cp ~/my_research_papers/*.pdf data/raw_docs/

# 4. Ingest fresh
python app.py --ingest

# 5. Test
python app.py --query "Summarize the research findings"
```

### Test Case 3: Domain-Specific Testing

```bash
# Example: Testing on technical documentation
cp ~/project_docs/api_reference.md data/raw_docs/
cp ~/project_docs/architecture.md data/raw_docs/
cp ~/project_docs/deployment.md data/raw_docs/

source venv/bin/activate
python app.py --delete-index
python app.py --ingest

# Test domain-specific queries
python app.py --query "How do I deploy the application?"
python app.py --query "What are the API endpoints?"
python app.py --query "Explain the system architecture"
```

---

## Troubleshooting

### Issue: "No documents found"

**Check:**
```bash
ls -la data/raw_docs/
# Make sure files have correct extensions: .txt, .md, .pdf
```

### Issue: "Empty chunks" or low count

**Cause:** Documents might be too small or empty

**Fix:**
- Ensure documents have actual content
- Check PDF extraction worked: `python -c "from pypdf import PdfReader; print(PdfReader('data/raw_docs/file.pdf').pages[0].extract_text())"`

### Issue: Poor quality answers

**Improvements:**
1. **Increase top-k:** Retrieve more chunks
2. **Adjust chunk size:** Larger chunks = more context
3. **Better documents:** Add more comprehensive source material
4. **Improve queries:** Be more specific in your questions

### Issue: Endee connection failed

**Fix:**
```bash
# Check if Endee is running
docker ps | grep endee

# If not running, start it
docker compose up -d

# Check logs
docker logs endee-server
```

---

## Performance Tips

### For Large Document Sets (100+ documents)

```bash
# Monitor progress during ingestion
python app.py --ingest 2>&1 | tee ingestion.log

# Check logs for any errors
grep ERROR ingestion.log
```

### For Better Search Quality

```python
# Edit src/config.py

# Increase search quality (slower but more accurate)
DEFAULT_EF = 256          # Default: 128

# Retrieve more candidates
DEFAULT_TOP_K = 10        # Default: 5

# Larger overlapping chunks
CHUNK_SIZE = 1024         # Default: 512
CHUNK_OVERLAP = 100       # Default: 50
```

---

## Example: Testing with Wikipedia Articles

```bash
# 1. Download Wikipedia articles
curl -o data/raw_docs/python_wiki.txt \
  "https://en.wikipedia.org/wiki/Python_(programming_language)?action=raw"

# 2. Ingest
source venv/bin/activate
python app.py --ingest

# 3. Test queries
python app.py --query "What is Python programming language?"
python app.py --query "Who created Python?"
python app.py --query "What are Python's key features?"
```

---

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Ingest all documents
python app.py --ingest

# Single query
python app.py --query "Your question here"

# Interactive mode
python app.py --interactive

# Delete index
python app.py --delete-index

# Custom top-k
python app.py --query "Question" --top-k 10

# Check what's indexed
ls -lh data/raw_docs/

# View logs
tail -f rag_system.log

# Check Endee status
curl http://localhost:8080/api/v1/index/list
```

---

## Next Steps

After testing:
1. ✅ Verify answers are accurate and relevant
2. ✅ Check source attribution makes sense
3. ✅ Experiment with different query styles
4. ✅ Adjust configuration for your use case
5. ✅ Add more diverse documents
6. ✅ Consider implementing evaluation metrics (see README.md)

**Ready to deploy?** See `README.md` for production deployment guidelines.
