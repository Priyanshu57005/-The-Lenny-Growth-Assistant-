import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.db import get_db, SessionModel, MessageModel, ArtifactModel
from app.schemas.schemas import (
    SessionCreate, SessionResponse, SessionSummary,
    MessageCreate, MessageResponse,
    ArtifactResponse, ProviderInfo, ProviderSwitchRequest
)
from app.services.llm import llm_factory
from app.agents import agent_router
from app.services.security import sanitizer

logger = logging.getLogger("lenny_growth.api")

router = APIRouter(prefix="/api")

# --- System & Provider Endpoints ---

@router.get("/health", tags=["System"])
async def health_check():
    provider_status = await llm_factory.get_health_status()
    return {
        "status": "healthy",
        "active_provider": llm_factory.active_provider_name,
        "provider_health": provider_status
    }

@router.get("/providers", response_model=ProviderInfo, tags=["LLM Providers"])
async def get_providers():
    status_dict = await llm_factory.get_health_status()
    return ProviderInfo(
        active_provider=llm_factory.active_provider_name,
        available_providers=["ollama", "anthropic", "openai"],
        ollama_model=llm_factory.get_provider("ollama").model_name,
        anthropic_model=llm_factory.get_provider("anthropic").model_name,
        openai_model=llm_factory.get_provider("openai").model_name,
        status=status_dict
    )

@router.post("/providers/switch", tags=["LLM Providers"])
async def switch_provider(req: ProviderSwitchRequest):
    try:
        new_provider = llm_factory.set_active_provider(req.provider)
        return {"message": f"Active LLM provider switched to {new_provider}", "active_provider": new_provider}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Session Endpoints ---

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED, tags=["Sessions"])
async def create_session(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    title = session_in.title or "New Conversation"
    new_session = SessionModel(title=title)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return SessionResponse(
        id=new_session.id,
        title=new_session.title,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        messages=[]
    )

@router.get("/sessions", response_model=List[SessionSummary], tags=["Sessions"])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    stmt = select(SessionModel).options(selectinload(SessionModel.messages)).order_by(SessionModel.updated_at.desc())
    result = await db.execute(stmt)
    sessions = result.scalars().unique().all()
    
    summaries = []
    for s in sessions:
        summaries.append(SessionSummary(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(s.messages) if s.messages else 0
        ))
    return summaries

@router.get("/sessions/{session_id}", response_model=SessionResponse, tags=["Sessions"])
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(SessionModel).where(SessionModel.id == session_id).options(
        selectinload(SessionModel.messages).selectinload(MessageModel.artifact)
    )
    result = await db.execute(stmt)
    session_obj = result.scalars().unique().first()
    
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_obj

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Sessions"])
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    result = await db.execute(stmt)
    session_obj = result.scalar_one_or_none()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(session_obj)
    await db.commit()
    return None

# --- Messaging & Artifact Endpoints ---

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse, tags=["Messages"])
async def send_message(
    session_id: str,
    message_in: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SessionModel).where(SessionModel.id == session_id).options(
        selectinload(SessionModel.messages)
    )
    result = await db.execute(stmt)
    session_obj = result.scalars().unique().first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    user_msg = MessageModel(
        session_id=session_id,
        role="user",
        content=message_in.content
    )
    db.add(user_msg)
    await db.commit()

    history = []
    for msg in session_obj.messages:
        if msg.role in ["user", "assistant"]:
            history.append({"role": msg.role, "content": msg.content})

    if len(session_obj.messages) <= 1 and message_in.content:
        short_title = message_in.content[:40] + "..." if len(message_in.content) > 40 else message_in.content
        session_obj.title = short_title

    try:
        ans_text, route, citations, artifact_payload = await agent_router.process_user_message(
            user_message=message_in.content,
            db_session=db,
            conversation_history=history,
            provider_override=message_in.provider_override
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

    sources_data = [c.model_dump() for c in citations] if citations else None

    assistant_msg = MessageModel(
        session_id=session_id,
        role="assistant",
        content=ans_text,
        sources=sources_data,
        agent_route=route
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    artifact_resp = None
    if artifact_payload:
        clean_content = artifact_payload["content"]
        if artifact_payload["artifact_type"] == "html":
            clean_content = sanitizer.wrap_in_sandboxed_document(clean_content)

        artifact_obj = ArtifactModel(
            session_id=session_id,
            message_id=assistant_msg.id,
            artifact_type=artifact_payload["artifact_type"],
            title=artifact_payload["title"],
            content=clean_content
        )
        db.add(artifact_obj)
        await db.commit()
        await db.refresh(artifact_obj)
        
        artifact_resp = ArtifactResponse(
            id=artifact_obj.id,
            session_id=artifact_obj.session_id,
            message_id=artifact_obj.message_id,
            artifact_type=artifact_obj.artifact_type,
            title=artifact_obj.title,
            content=artifact_obj.content,
            created_at=artifact_obj.created_at
        )

    return MessageResponse(
        id=assistant_msg.id,
        session_id=assistant_msg.session_id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        sources=citations,
        agent_route=assistant_msg.agent_route,
        created_at=assistant_msg.created_at,
        artifact=artifact_resp
    )

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse, tags=["Artifacts"])
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ArtifactModel).where(ArtifactModel.id == artifact_id)
    result = await db.execute(stmt)
    art = result.scalar_one_or_none()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return art
