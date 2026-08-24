import pytest
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db import AsyncSessionLocal, init_db, TranscriptChunkModel
from app.rag import retriever, embedder
from sqlalchemy import delete

@pytest.mark.asyncio
async def test_retrieval_with_grounded_chunks():
    await init_db()
    async with AsyncSessionLocal() as db:
        text_content = "Shreyas Doshi discusses the LNO framework for PM task prioritization: Leverage, Neutral, and Overhead."
        chunk = TranscriptChunkModel(
            guest="Shreyas Doshi",
            title="LNO Framework Episode",
            url="https://example.com",
            date="2023-01-01",
            chunk_index=0,
            content=text_content,
            embedding=embedder.embed_text(text_content)
        )
        db.add(chunk)
        await db.commit()

        # Query retriever with matching terms
        citations = await retriever.retrieve("Shreyas Doshi LNO framework prioritization", db, threshold=0.1)
        assert len(citations) > 0
        assert citations[0].guest == "Shreyas Doshi"
        assert "LNO" in citations[0].snippet

        # Clean up
        await db.execute(delete(TranscriptChunkModel).where(TranscriptChunkModel.guest == "Shreyas Doshi"))
        await db.commit()

@pytest.mark.asyncio
async def test_empty_retrieval_handling():
    await init_db()
    async with AsyncSessionLocal() as db:
        citations = await retriever.retrieve("NonExistentUnrelatedKeywordXYZ12345", db, threshold=0.95)
        assert isinstance(citations, list)
        assert len(citations) == 0
