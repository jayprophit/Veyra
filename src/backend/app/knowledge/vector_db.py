"""Vector Database for Knowledge Management."""
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeDoc:
    id: str
    title: str
    content: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None

class VectorDB:
    """Semantic search with vector embeddings."""
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.docs: Dict[str, KnowledgeDoc] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.model = None
    
    async def add(self, title: str, content: str, metadata: dict = None) -> str:
        await self._load_model()
        doc_id = f"doc_{len(self.docs)}"
        doc = KnowledgeDoc(id=doc_id, title=title, content=content, metadata=metadata)
        doc.embedding = await self._embed(content)
        self.docs[doc_id] = doc
        self.embeddings[doc_id] = doc.embedding
        return doc_id
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.docs:
            return []
        query_emb = await self._embed(query)
        scores = []
        for doc_id, emb in self.embeddings.items():
            sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
            scores.append((self.docs[doc_id], float(sim)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [{'doc': s[0].to_dict() if hasattr(s[0], 'to_dict') else str(s[0]), 'score': s[1]} for s in scores[:top_k]]
    
    async def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                pass
    
    async def _embed(self, text: str) -> np.ndarray:
        if self.model:
            return self.model.encode(text)
        return np.random.randn(self.dim)

vector_db = VectorDB()
