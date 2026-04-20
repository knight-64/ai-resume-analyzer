from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from dotenv import load_dotenv
import os

from .api.routes import router

# Load environment variables regardless of entrypoint (run.py, uvicorn, tests)
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Resume Analyzer",
    description="Analyze resumes against job descriptions using AI",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load HTML content
def get_html_content() -> str:
    """Load the HTML UI"""
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent  # app -> backend
    project_root = backend_dir.parent            # backend -> project root
    ui_candidates = [
        project_root / "index_backup.html",  # full UI
        project_root / "index.html",         # fallback UI
        project_root / "index_simple.html",  # minimal fallback
    ]

    for index_path in ui_candidates:
        if index_path.exists():
            with open(str(index_path), "r", encoding="utf-8") as f:
                return f"<!-- served:{index_path.name} -->\n" + f.read()

    return "<h1>UI not found in project root</h1>"


# Serve the HTML UI at root - MUST be before router
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the web UI"""
    return get_html_content()


# Include API routes
app.include_router(router)
