from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
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
import html
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
    job_description: str = Form(""),
    provider: Optional[str] = Form(None),
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


@router.post("/resume-download")
async def download_resume_html(
    name: str = Form("Your Name"),
    title: str = Form("Professional Title"),
    email: str = Form(""),
    phone: str = Form(""),
    location: str = Form(""),
    summary: str = Form(""),
    skills: str = Form(""),
    experience: str = Form(""),
    education: str = Form(""),
):
    """Return a simple HTML resume as a downloadable attachment."""

    def split_lines(value: str) -> List[str]:
        return [line.strip() for line in value.splitlines() if line.strip()]

    def list_items(lines: List[str]) -> str:
        return "".join(f"<li>{html.escape(line)}</li>" for line in lines)

    safe_name = name.strip() or "resume"
    filename = "-".join(part for part in safe_name.lower().split() if part) or "resume"
    filename = "".join(ch for ch in filename if ch.isalnum() or ch == "-") or "resume"

    contact = " | ".join(
        html.escape(value)
        for value in [email.strip(), phone.strip(), location.strip()]
        if value.strip()
    )

    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{html.escape(safe_name)} - Resume</title>
  <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 44px; color: #111827; line-height: 1.6; background: #ffffff; }}
        .resume {{ max-width: 760px; margin: 0 auto; }}
        h1 {{ margin: 0; font-size: 42px; letter-spacing: 0.04em; text-align: center; }}
        .headline {{ color: #404040; font-weight: 700; font-size: 1.1rem; text-align: center; margin-top: 4px; margin-bottom: 12px; }}
        .contact {{ color: #404040; margin-bottom: 18px; text-align: center; padding-bottom: 12px; border-bottom: 1px solid #d1d5db; }}
        h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 0.14em; color: #111827; margin-top: 22px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #d1d5db; }}
        .entry {{ margin-bottom: 14px; }}
        .meta {{ color: #6b7280; font-size: 0.95rem; }}
        .role {{ color: #111827; font-size: 1.02rem; font-weight: 700; margin-top: 2px; }}
        .desc {{ color: #111827; }}
        ul {{ margin: 0; padding-left: 18px; }}
        .skills {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px 22px; padding-left: 18px; }}
        p {{ margin: 0; }}
  </style>
</head>
<body>
    <div class="resume">
        <h1>{html.escape(safe_name).upper()}</h1>
        <div class="headline">{html.escape(title.strip() or 'Professional Title')}</div>
        <div class="contact">{contact}</div>
        <h2>About Me</h2>
        <p>{html.escape(summary.strip())}</p>
        <h2>Education</h2>
        {''.join(
                f'<div class="entry"><div class="meta">{html.escape(parts[0])} | {html.escape(parts[1])}</div><div class="role">{html.escape(parts[2])}</div><div class="desc">{html.escape(parts[3])}</div></div>'
                if (parts := [part.strip() for part in item.split('|') if part.strip()]) and len(parts) >= 4
                else f'<div class="entry"><div class="desc">{html.escape(item)}</div></div>'
                for item in split_lines(education)
        )}
        <h2>Work Experience</h2>
        {''.join(
                f'<div class="entry"><div class="meta">{html.escape(parts[0])} | {html.escape(parts[1])}</div><div class="role">{html.escape(parts[2])}</div><div class="desc">{html.escape(parts[3])}</div></div>'
                if (parts := [part.strip() for part in item.split('|') if part.strip()]) and len(parts) >= 4
                else f'<div class="entry"><div class="desc">{html.escape(item)}</div></div>'
                for item in split_lines(experience)
        )}
        <h2>Skills</h2>
        <ul class="skills">{''.join(f'<li>{html.escape(skill)}</li>' for skill in split_lines(skills) or [skills])}</ul>
    </div>
</body>
</html>"""

    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}.html"'},
    )


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
