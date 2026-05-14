# Memory Service

## Overview

The Memory Service provides persistent memory and knowledge storage for AI agents and systems. This is Layer 2 of the 5-layer system architecture.

## Components

### Vector Database (Qdrant)

Primary vector database for semantic search and embeddings storage.

**Features:**
- High-performance vector similarity search
- Hybrid search (vector + keyword)
- Real-time updates
- Scalable architecture
- Filtered search

### Memory Systems

**Episodic Memory**
- Events and experiences
- Agent interactions
- Market events
- Trading decisions
- System events

**Strategy Memory**
- Trading strategies
- Strategy outcomes
- Performance metrics
- Strategy parameters
- Backtest results

**Agent Communication Memory**
- Inter-agent messages
- Collaboration history
- Decision chains
- Agent learnings

**User Behavior Memory**
- User preferences
- Trading patterns
- Risk tolerance
- Interaction history

**Failure Patterns Memory**
- Error patterns
- Failure modes
- Recovery strategies
- Prevention measures

### Memory Types

**Short-Term Memory**
- Current market state
- Active positions
- Recent signals
- Session context

**Long-Term Memory**
- Historical strategies
- Performance metrics
- Market patterns
- Agent learnings

**Semantic Memory**
- Strategy embeddings
- Market embeddings
- Risk factor embeddings
- Knowledge base

## Architecture

```
Memory Service
├── Vector Database (Qdrant)
│   ├── Collections
│   │   ├── episodic_memory
│   │   ├── strategy_memory
│   │   ├── agent_communication
│   │   └── semantic_knowledge
│   └── Indexes
│       ├── HNSW (vector)
│       └── Payload (keyword)
├── Memory Manager
│   ├── Storage
│   ├── Retrieval
│   ├── Update
│   └── Deletion
└── Memory Interface
    ├── Store
    ├── Search
    ├── Update
    └── Delete
```

## API

### Store Memory

```typescript
interface Memory {
  type: 'episodic' | 'strategy' | 'agent_communication' | 'user_behavior' | 'failure_pattern'
  content: string
  embedding?: number[]
  metadata: Record<string, any>
  timestamp: Date
}

await memoryService.store(memory)
```

### Search Memory

```typescript
const results = await memoryService.search({
  query: 'trading strategy for volatile markets',
  type: 'strategy',
  limit: 10
})
```

### Update Memory

```typescript
await memoryService.update(memoryId, {
  metadata: { outcome: 'successful' }
})
```

### Delete Memory

```typescript
await memoryService.delete(memoryId)
```

## Configuration

```bash
# .env
QDRANT_HOST=http://localhost:6333
QDRANT_API_KEY=
MEMORY_RETENTION_DAYS=365
MEMORY_MAX_SIZE_GB=100
```

## Collections

### episodic_memory

Stores events and experiences with temporal context.

**Payload Schema:**
```json
{
  "event_type": "trade",
  "timestamp": "2024-01-01T12:00:00Z",
  "agent_id": "market_watcher",
  "outcome": "success",
  "context": {}
}
```

### strategy_memory

Stores trading strategies and their outcomes.

**Payload Schema:**
```json
{
  "strategy_name": "momentum",
  "parameters": {},
  "performance": {
    "returns": 0.15,
    "sharpe_ratio": 1.5
  },
  "backtest_date": "2024-01-01"
}
```

### agent_communication

Stores inter-agent communication history.

**Payload Schema:**
```json
{
  "from_agent": "market_watcher",
  "to_agent": "risk_analyzer",
  "message": "High volatility detected",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### semantic_knowledge

Stores general knowledge and embeddings.

**Payload Schema:**
```json
{
  "category": "financial_concept",
  "source": "internal",
  "confidence": 0.95
}
```

## Best Practices

1. **Embedding Strategy**: Use appropriate embedding models for different memory types
2. **Retention Policy**: Implement automatic cleanup based on age and relevance
3. **Indexing**: Create appropriate indexes for common query patterns
4. **Batch Operations**: Use batch operations for bulk storage and retrieval
5. **Caching**: Cache frequently accessed memories
6. **Validation**: Validate memory content before storage
7. **Versioning**: Track memory versions for audit trails

## Future Enhancements

- Hierarchical memory organization
- Memory compression
- Automatic summarization
- Memory importance scoring
- Cross-agent memory sharing
- Memory access controls
- Memory encryption
- Distributed memory
