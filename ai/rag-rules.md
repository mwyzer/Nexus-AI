# RAG Rules

## Retrieval-Augmented Generation Guidelines

### 1. Query Formulation

- Use the user's exact question as the primary search query
- Generate 1-3 variant queries to improve recall
- Remove filler words and focus on key concepts
- Include relevant keywords from conversation context

### 2. Retrieval Strategy

- **Default**: Hybrid search (semantic + keyword, 0.7 weight on semantic)
- **Precision-critical**: Pure semantic with higher threshold
- **Broad exploration**: Lower threshold, higher top_k
- **Time-sensitive**: Apply recency boost to newer documents

### 3. Context Processing

- Retrieve top_k=5 by default, up to 20 for complex queries
- Filter by relevance score threshold (> 0.3)
- De-duplicate near-identical chunks
- Sort by relevance, then by recency as tiebreaker
- Trim context to fit model's context window

### 4. Answer Generation

- Only use information present in the retrieved context
- Cite specific sources using `[document_name]` or `[chunk_id]` format
- If context is insufficient, say: "I couldn't find enough information to answer this question."
- Structure answers with bullet points for multi-part questions
- Include direct quotes when appropriate, marked with `>`

### 5. Quality Checks

- Verify answer is grounded in retrieved context (faithfulness)
- Ensure answer directly addresses the question (relevance)
- Check for contradictions with other retrieved chunks
- Flag low-confidence answers: "I'm not entirely confident, but..."

## Chunking Best Practices

| Document Type | Strategy   | Chunk Size | Overlap |
|---------------|------------|------------|---------|
| Articles      | Recursive  | 1000       | 200     |
| Code          | Recursive  | 1500       | 100     |
| Documentation | Markdown   | 800        | 150     |
| Chat logs     | Fixed      | 500        | 100     |
| Legal/Contract | Semantic  | 2000       | 300     |

## Embedding Guidelines

- Use the same embedding model for indexing and querying
- Re-index when changing embedding models
- Normalize embeddings for cosine similarity
- Batch embedding requests for efficiency

## Response Template

```
[Answer based on context]

**Sources:**
1. [Document Name] — [relevant snippet]
2. [Document Name] — [relevant snippet]

**Confidence**: High/Medium/Low
```
