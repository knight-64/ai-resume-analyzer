from fastapi import APIRouter, HTTPException, UploadFile, File
from ..services.analyzer import ResumeAnalyzer
from ..services.pdf_extractor import extract_text_from_pdf
from ..services.conversation import ConversationManager
from ..services.provider_factory import get_provider
from ..schemas import (
    AnalysisRequest,
    AnalysisBatchRequest,
    AnalysisResponse,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatSessionResponse,
)
from typing import Dict, List, Optional
import time

router = APIRouter(prefix="/api", tags=["analysis"])

# Lazy initialization of analyzer
_analyzer: Optional[ResumeAnalyzer] = None

# Lazy initialization of conversation manager
_conversation_manager: Optional[ConversationManager] = None


def get_analyzer() -> ResumeAnalyzer:
    """Get or create the analyzer instance (lazy loading)"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ResumeAnalyzer()
    return _analyzer


def get_conversation_manager() -> ConversationManager:
    """Get or create the conversation manager instance (lazy loading)"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest):
    """
    Analyze a single resume against a job description.

    Returns detailed analysis with match percentage, skills, suggestions, etc.

    Query Parameters:
        - provider (optional): LLM provider to use - "claude" or "groq".
                              If not provided, uses default from environment.
    """
    try:
        if not request.resume.strip():
            raise HTTPException(status_code=400, detail="Resume cannot be empty")
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty")

        analyzer = get_analyzer()
        result = analyzer.analyze_single(
            request.resume, request.job_description, provider=request.provider
        )
        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-batch")
async def analyze_batch(request: AnalysisBatchRequest) -> Dict:
    """
    Analyze multiple resumes against a job description (batch mode).

    Returns array of analysis results with batch metadata.

    Query Parameters:
        - provider (optional): LLM provider to use - "claude" or "groq".
                              If not provided, uses default from environment.
    """
    try:
        if not request.resumes:
            raise HTTPException(status_code=400, detail="Resumes list cannot be empty")
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty")

        # Validate resumes
        for i, resume in enumerate(request.resumes):
            if not resume.strip():
                raise HTTPException(
                    status_code=400, detail=f"Resume at index {i} is empty"
                )

        analyzer = get_analyzer()
        result = analyzer.analyze_batch(
            request.resumes, request.job_description, provider=request.provider
        )
        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/results/{analysis_id}")
async def get_result(analysis_id: str) -> Dict:
    """
    Retrieve a previously cached analysis result by ID.
    """
    try:
        analyzer = get_analyzer()
        result = analyzer.get_result(analysis_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-resume-analyzer"}


@router.post("/upload-resume")
async def upload_resume_pdf(
    file: UploadFile = File(...),
    job_description: str = "",
    provider: Optional[str] = None,
):
    """
    Upload a resume PDF and optionally analyze it.

    Args:
        file: PDF file to upload
        job_description: Optional job description for immediate analysis
        provider: Optional LLM provider ("claude" or "groq")

    Returns:
        Extracted text from PDF, and analysis results if job_description provided
    """
    try:
        # Validate file
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Extract text from PDF
        try:
            resume_text = extract_text_from_pdf(content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # If job description provided, analyze immediately
        if job_description.strip():
            analyzer = get_analyzer()
            analysis = analyzer.analyze_single(
                resume_text, job_description, provider=provider
            )
            return {
                "extracted_text": resume_text,
                "analysis": analysis.dict(),
            }

        # Return just the extracted text
        return {"extracted_text": resume_text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# Chat endpoints

@router.post("/chat/start", response_model=ChatSessionResponse)
async def start_chat_session():
    """
    Start a new chat session.

    Returns:
        Dictionary with session_id for use in subsequent messages
    """
    try:
        manager = get_conversation_manager()
        session_id = manager.create_session()
        return ChatSessionResponse(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    Send a message in a chat session and get AI response.

    Args:
        request: ChatRequest with session_id, message, and optional provider

    Returns:
        ChatResponse with assistant's reply and metadata
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        manager = get_conversation_manager()
        start_time = time.time()

        # Get conversation history
        messages = manager.get_messages(request.session_id)

        # Add user message
        manager.add_message(request.session_id, "user", request.message)
        messages.append({"role": "user", "content": request.message})

        # Get LLM response
        try:
            provider = get_provider(request.provider)
            response_text = provider.chat(messages)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Add assistant response to history
        manager.add_message(request.session_id, "assistant", response_text)

        processing_time_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            session_id=request.session_id,
            message=response_text,
            timestamp=__import__("datetime").datetime.utcnow().isoformat(),
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/chat/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(session_id: str):
    """
    Get full conversation history for a session.

    Args:
        session_id: The session ID

    Returns:
        List of ChatMessage objects
    """
    try:
        manager = get_conversation_manager()
        messages = manager.get_messages(session_id)
        return [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session.

    Args:
        session_id: The session ID to delete

    Returns:
        Success message
    """
    try:
        manager = get_conversation_manager()
        manager.delete_session(session_id)
        return {"message": "Session deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
