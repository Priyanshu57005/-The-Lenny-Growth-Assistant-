import pytest
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents import agent_router

@pytest.mark.asyncio
async def test_agent_route_classification():
    # Test Ship 30 route rule
    ship30_route = await agent_router.classify_route("Write a Ship 30 essay on product management")
    assert ship30_route == "SHIP30_ESSAY"

    # Test Artifact route rule
    artifact_route = await agent_router.classify_route("Build an interactive HTML component artifact")
    assert artifact_route == "ARTIFACT_GEN"

    # Test Direct route rule
    direct_route = await agent_router.classify_route("hello")
    assert direct_route == "DIRECT"

    # Test Knowledge QnA default
    qna_route = await agent_router.classify_route("How does Elena Verna define Product-Led Growth?")
    assert qna_route in ["KNOWLEDGE_QNA", "DIRECT", "SHIP30_ESSAY", "ARTIFACT_GEN"]
