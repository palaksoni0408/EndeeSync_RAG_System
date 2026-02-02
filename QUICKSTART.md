# RAG System with Endee - Quick Start

## Virtual Environment Setup (✅ Completed)

The virtual environment has been created and all dependencies are installed!

## How to Use

### Option 1: Using the Helper Script

```bash
# Ingest documents
./run.sh python app.py --ingest

# Query the system
./run.sh python app.py --query "What is semantic search?"

# Interactive mode
./run.sh python app.py --interactive
```

### Option 2: Manual Activation

```bash
# Activate virtual environment
source venv/bin/activate

# Now you can run commands directly
python app.py --ingest
python app.py --query "What is semantic search?"

# When done, deactivate
deactivate
```

## Before Running

**Important:** Make sure to add your OpenAI API key to the `.env` file:

```bash
# Edit .env file
nano .env

# Add your API key:
OPENAI_API_KEY=sk-your-key-here
```

## Quick Test

1. **First, ingest the sample documents:**
   ```bash
   ./run.sh python app.py --ingest
   ```

2. **Then query the system:**
   ```bash
   ./run.sh python app.py --query "What is RAG?"
   ```

## Next Steps

See the main [README.md](README.md) for complete documentation.
