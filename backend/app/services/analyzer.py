import uuid
from datetime import datetime
from typing import List, Dict, Optional
from .provider_factory import get_provider
from ..schemas import AnalysisResponse, SkillsData
import time


class ResumeAnalyzer:
    """Core resume analysis service"""

    def __init__(self):
        # In-memory storage: {analysis_id: analysis_data}
        self.results_cache: Dict[str, dict] = {}

    def analyze_single(
        self, resume: str, job_description: str, provider: Optional[str] = None
    ) -> AnalysisResponse:
        """
        Analyze a single resume against a job description.

        Args:
            resume: Resume text
            job_description: Job description text
            provider: Optional provider name ("claude" or "groq"). If not provided, uses default.

        Returns:
            AnalysisResponse with analysis results
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())

        try:
            # Get the appropriate provider
            llm_provider = get_provider(provider)

            # Call provider API
            analysis_data = llm_provider.analyze_resume(resume, job_description)

            # Ensure all required fields are present
            analysis_data.setdefault("match_percentage", 0)
            analysis_data.setdefault("ats_score", 0)
            analysis_data.setdefault("weak_sections", [])
            analysis_data.setdefault("suggestions", [])
            analysis_data.setdefault("improved_summary", "")
            analysis_data.setdefault("skills", {"extracted": [], "matched": [], "missing": []})

            # Create response object
            processing_time = (time.time() - start_time) * 1000  # Convert to ms

            response = AnalysisResponse(
                analysis_id=analysis_id,
                match_percentage=int(analysis_data.get("match_percentage", 0)),
                ats_score=int(analysis_data.get("ats_score", 0)),
                skills=SkillsData(
                    extracted=analysis_data["skills"].get("extracted", []),
                    matched=analysis_data["skills"].get("matched", []),
                    missing=analysis_data["skills"].get("missing", []),
                ),
                weak_sections=analysis_data.get("weak_sections", []),
                suggestions=analysis_data.get("suggestions", []),
                improved_summary=analysis_data.get("improved_summary", ""),
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=processing_time,
            )

            # Cache the result
            self.results_cache[analysis_id] = response.dict()

            return response

        except Exception as e:
            raise RuntimeError(f"Analysis failed: {str(e)}")

    def analyze_batch(
        self, resumes: List[str], job_description: str, provider: Optional[str] = None
    ) -> Dict:
        """
        Analyze multiple resumes against a job description.

        Args:
            resumes: List of resume texts
            job_description: Job description text
            provider: Optional provider name ("claude" or "groq"). If not provided, uses default.

        Returns:
            Dictionary with batch analysis results
        """
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        analyses = []

        for resume in resumes:
            try:
                analysis = self.analyze_single(resume, job_description, provider)
                analyses.append(analysis.dict())
            except Exception as e:
                # Log error but continue with other resumes
                print(f"Error analyzing resume: {str(e)}")
                continue

        processing_time = (time.time() - start_time) * 1000

        return {
            "batch_id": batch_id,
            "total_resumes": len(resumes),
            "analyzed_count": len(analyses),
            "analyses": analyses,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": processing_time,
        }

    def get_result(self, analysis_id: str) -> dict:
        """Retrieve a cached analysis result"""
        if analysis_id not in self.results_cache:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        return self.results_cache[analysis_id]
