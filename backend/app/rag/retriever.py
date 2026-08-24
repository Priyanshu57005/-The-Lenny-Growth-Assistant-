import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import TranscriptChunkModel
from app.schemas.schemas import SourceCitation
from app.rag.embedder import embedder
from app.config.settings import settings

logger = logging.getLogger("lenny_growth.rag.retriever")

class TranscriptRetriever:
    def __init__(self, top_k: int = None, threshold: float = None):
        self.top_k = top_k or settings.TOP_K_RETRIEVAL
        self.threshold = threshold or settings.SIMILARITY_THRESHOLD

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    async def retrieve(
        self,
        query: str,
        db_session: AsyncSession,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[SourceCitation]:
        k = top_k or self.top_k
        min_score = threshold or self.threshold

        # Fetch all transcript chunks from DB
        stmt = select(TranscriptChunkModel)
        result = await db_session.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            logger.info("No transcript chunks present in database.")
            return []

        query_vec = embedder.embed_text(query)
        scored_chunks = []

        query_keywords = set(query.lower().split())

        for chunk in chunks:
            chunk_vec = chunk.embedding
            vector_sim = self._cosine_similarity(query_vec, chunk_vec) if chunk_vec else 0.0
            
            # Keyword overlap boost
            content_lower = chunk.content.lower()
            guest_lower = chunk.guest.lower()
            title_lower = chunk.title.lower()
            
            keyword_hits = sum(1 for kw in query_keywords if len(kw) > 3 and (kw in content_lower or kw in guest_lower or kw in title_lower))
            keyword_score = min(1.0, keyword_hits * 0.15)

            # Combined hybrid score
            hybrid_score = (vector_sim * 0.7) + (keyword_score * 0.3)

            if hybrid_score >= min_score:
                snippet = chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content
                citation = SourceCitation(
                    chunk_id=chunk.id,
                    guest=chunk.guest,
                    title=chunk.title,
                    url=chunk.url,
                    date=chunk.date,
                    snippet=snippet,
                    score=round(hybrid_score, 4)
                )
                scored_chunks.append((hybrid_score, citation, chunk.content))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_citations = [item[1] for item in scored_chunks[:k]]

        logger.info(f"Retrieved {len(top_citations)} relevant chunks for query: '{query[:40]}...' (Top score: {top_citations[0].score if top_citations else 0.0})")
        return top_citations

retriever = TranscriptRetriever()
