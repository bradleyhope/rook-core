# Research Findings: Time-Weighted Vector Retrieval

**Sources:** 
- LangChain Time-Weighted Retriever
- Various vector database research papers
- Recency bias in information retrieval

---

## Time-Weighted Retrieval Algorithm

### Scoring Formula:
```
score = (1 - decay_rate)^hours_passed + semantic_similarity
```

### Components:
1. **Semantic Similarity**: Cosine similarity between query and memory vectors
2. **Temporal Decay**: Exponential decay based on time since last access/creation
3. **Combined Score**: Weighted sum of both factors

### Parameters:
- `decay_rate`: How quickly memories fade (e.g., 0.01 = 1% decay per hour)
- `k`: Number of memories to retrieve
- `fetch_k`: Number of candidates to consider before re-ranking

---

## Recency Bias in AI Systems

### Problem:
- Pure semantic search ignores temporal context
- Old but semantically similar memories may be irrelevant
- Recent experiences should have higher priority

### Solutions:

1. **Time Decay Weighting**
   - Recent memories score higher
   - Exponential decay function
   - Configurable decay rate

2. **Access-Based Decay**
   - Memories decay based on last access time
   - Frequently accessed memories stay fresh
   - Mimics human memory strengthening through recall

3. **Hybrid Approaches**
   - Combine creation time and access time
   - Weight by both recency and frequency
   - Add importance/significance scores

---

## Relevant Vector Database Features

### Metadata Filtering:
- Store timestamp, importance, emotional valence as metadata
- Filter before semantic search
- Combine filters with vector similarity

### Multi-Vector Retrieval:
- Store multiple embeddings per experience
- Different aspects (what, when, who, why, how)
- Retrieve based on different query types

### Weighted Scoring:
```
final_score = α * semantic_similarity + 
              β * recency_score + 
              γ * importance_score +
              δ * emotional_valence
```

Where α + β + γ + δ = 1

---

## Application to ROOK

### Memory Schema:
```json
{
  "id": "investigation_001",
  "type": "investigation",
  "content": "Discovered shell company network in Panama",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "timestamp": "2024-03-15T10:30:00Z",
    "importance": 0.9,
    "emotional_valence": "breakthrough",
    "tags": ["shell_companies", "panama", "money_laundering"],
    "related_investigations": ["investigation_002", "investigation_015"],
    "outcome": "successful_prosecution"
  }
}
```

### Retrieval Strategy:

1. **For Investigations (High Stakes)**
   - High weight on importance (γ = 0.4)
   - Moderate weight on recency (β = 0.3)
   - Semantic similarity (α = 0.3)
   - Emotional valence (δ = 0.0)

2. **For Casual Queries**
   - High weight on semantic similarity (α = 0.6)
   - Moderate weight on recency (β = 0.3)
   - Low weight on importance (γ = 0.1)
   - Emotional valence (δ = 0.0)

3. **For Self-Reflection ("Tell me about yourself")**
   - High weight on importance (γ = 0.5)
   - High weight on emotional valence (δ = 0.3)
   - Low weight on recency (β = 0.1)
   - Semantic similarity (α = 0.1)

---

## Advanced Techniques

### 1. Consolidation Process
- Background job that runs periodically
- Identifies related memories
- Creates "summary memories" that link them
- Strengthens important connections

### 2. Forgetting Mechanism
- Memories below threshold importance decay faster
- Rarely accessed memories fade
- But can be "revived" if accessed again

### 3. Episodic Clustering
- Group related experiences together
- Create hierarchical memory structure
- Retrieve clusters instead of individual memories

---

## Technical Implementation

### Vector Database: Pinecone
- Supports metadata filtering
- Fast approximate nearest neighbor search
- Can store multiple vectors per item

### Retrieval Pipeline:
```
1. Query → Generate embedding
2. Filter by metadata (time range, type, importance > threshold)
3. Vector similarity search (get top 100 candidates)
4. Re-rank by weighted score (semantic + temporal + importance + valence)
5. Return top k results
6. Update "last accessed" timestamp for retrieved memories
```

### Decay Function:
```python
def calculate_recency_score(timestamp, current_time, decay_rate=0.01):
    hours_passed = (current_time - timestamp).total_seconds() / 3600
    return (1 - decay_rate) ** hours_passed
```

### Importance Score:
- Manual tagging (0.0 to 1.0)
- OR derived from outcome (successful investigation = 0.9, dead end = 0.3)
- OR learned from user feedback

---

## Key Insight for ROOK

**Personality emerges from the weighted combination of:**
1. **What** he remembers (content)
2. **When** he remembers it (recency)
3. **How important** it was (significance)
4. **How he felt** about it (emotional valence)

This creates a **dynamic, experience-based personality** that evolves over time without hardcoded traits.

