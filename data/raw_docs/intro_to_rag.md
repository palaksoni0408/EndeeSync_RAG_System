# What is Retrieval-Augmented Generation (RAG)?

Retrieval-Augmented Generation (RAG) is a powerful technique that enhances Large Language Models (LLMs) by providing them with relevant external knowledge during generation. Instead of relying solely on the model's training data, RAG systems retrieve relevant documents or passages from a knowledge base and use them as context for generating answers.

## How RAG Works

The RAG process consists of two main phases:

### 1. Retrieval Phase
- Convert user query into a vector embedding
- Search a vector database for semantically similar documents
- Retrieve the top-k most relevant passages

### 2. Generation Phase
- Inject retrieved passages as context into the LLM prompt
- Generate a grounded answer based on the provided context
- Return answer with source citations

## Why Use RAG?

### Advantages over Fine-tuning

1. **Up-to-date Information**: Add new documents without retraining
2. **Lower Cost**: No expensive model retraining required
3. **Source Attribution**: Can cite specific sources for verification
4. **Domain Flexibility**: Easy to switch domains by changing document corpus
5. **Reduced Hallucination**: Grounded in actual documents

### Advantages over Pure LLMs

1. **Factual Accuracy**: Uses authoritative sources
2. **Transparency**: Shows which documents influenced the answer
3. **Customization**: Works with proprietary/private knowledge bases
4. **Efficiency**: Smaller models can perform well with good context

## Vector Databases in RAG

Vector databases are essential for RAG systems because they enable semantic similarity search at scale. Traditional keyword search cannot capture meaning, while vector search finds conceptually related content even without exact word matches.

### Why Endee?

- **Fast**: HNSW algorithm for efficient approximate nearest neighbor search
- **Flexible**: Supports dense and hybrid (dense + sparse) indexes
- **Lightweight**: Easy to deploy locally or in production
- **Scalable**: Handles millions of vectors efficiently

## Common Use Cases

- **Customer Support**: Answer questions from documentation
- **Research Assistance**: Find relevant papers and summarize findings
- **Enterprise Search**: Query internal knowledge bases
- **Content Recommendation**: Suggest related articles or products
- **Code Documentation**: Answer questions about codebases

## Limitations

1. **Context Window**: Limited by LLM's maximum context length
2. **Retrieval Quality**: Results depend on embedding model quality
3. **Latency**: Multiple steps (embed → search → generate) add delay
4. **Cost**: API calls for embeddings and generation
