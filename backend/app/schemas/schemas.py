from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict

# Source Citation Schema
class SourceCitation(BaseModel):
    chunk_id: str
    guest: str
    title: str
    url: Optional[str] = None
    date: Optional[str] = None
    snippet: str
    score: float = 0.0

# Artifact Schema
class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    message_id: Optional[str] = None
    artifact_type: str  # 'markdown' | 'html'
    title: str
    content: str
    created_at: datetime

# Message Schemas
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Message text from user")
    provider_override: Optional[str] = Field(None, description="Optional temporary provider override: 'ollama', 'anthropic', 'openai'")

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    sources: Optional[List[SourceCitation]] = None
    agent_route: Optional[str] = None
    created_at: datetime
    artifact: Optional[ArtifactResponse] = None

# Session Schemas
class SessionCreate(BaseModel):
    title: Optional[str] = Field(default="New Conversation")

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

class SessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

# Provider Schemas
class ProviderInfo(BaseModel):
    active_provider: str
    available_providers: List[str]
    ollama_model: str
    anthropic_model: str
    openai_model: str
    status: Dict[str, bool]

class ProviderSwitchRequest(BaseModel):
    provider: str
