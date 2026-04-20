from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for single resume analysis"""
    resume: str
    job_description: str
    provider: Optional[str] = Field(
        default=None,
        description='LLM provider to use: "claude" or "groq". If not provided, uses default.'
    )


class AnalysisBatchRequest(BaseModel):
    """Request model for batch resume analysis"""
    resumes: List[str]
    job_description: str
    provider: Optional[str] = Field(
        default=None,
        description='LLM provider to use: "claude" or "groq". If not provided, uses default.'
    )


class SkillsData(BaseModel):
    """Skills breakdown in analysis"""
    extracted: List[str]
    matched: List[str]
    missing: List[str]


class AnalysisResponse(BaseModel):
    """Response model for resume analysis"""
    analysis_id: str
    match_percentage: int
    ats_score: int
    skills: SkillsData
    weak_sections: List[str]
    suggestions: List[str]
    improved_summary: str
    timestamp: str
    processing_time_ms: float


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis"""
    batch_id: str
    total_resumes: int
    analyses: List[AnalysisResponse]
    timestamp: str
    processing_time_ms: float


class ChatMessage(BaseModel):
    """A single message in a conversation"""
    role: str = Field(..., description='Message role: "user", "assistant", or "system"')
    content: str = Field(..., description="Message content text")


class ChatRequest(BaseModel):
    """Request model for sending a chat message"""
    session_id: str = Field(..., description="Conversation session ID")
    message: str = Field(..., description="User message text")
    provider: Optional[str] = Field(
        default=None,
        description='LLM provider to use: "claude" or "groq". If not provided, uses default.'
    )


class ChatResponse(BaseModel):
    """Response model for a chat message"""
    session_id: str = Field(..., description="Conversation session ID")
    message: str = Field(..., description="Assistant response text")
    timestamp: str = Field(..., description="Response timestamp in ISO format")
    processing_time_ms: float = Field(..., description="API processing time in milliseconds")


class ChatSessionResponse(BaseModel):
    """Response model for creating a chat session"""
    session_id: str = Field(..., description="Newly created session ID")
