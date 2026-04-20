from abc import ABC, abstractmethod
import json
from typing import List, Dict


class LLMProvider(ABC):
    """Abstract base class for LLM providers (Claude, Groq, etc.)"""

    # Shared prompt template used by all providers
    ANALYSIS_PROMPT_TEMPLATE = """You are an advanced Applicant Tracking System (ATS) and professional resume reviewer.

Analyze the following resume against the job description and provide structured output.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:

1. Extract all relevant skills from the resume (technical + soft skills).
2. Extract required skills from the job description.
3. Compare both and calculate a match percentage (0–100).
4. Identify matched skills and missing skills.
5. Evaluate the resume quality like an ATS system (score 0-100).
6. Identify weak sections (e.g., skills, projects, experience, summary).
7. Provide clear and practical improvement suggestions:
   - skills to add
   - project ideas to include
   - how to improve experience descriptions
   - use of strong action verbs
8. Generate a short improved professional summary (3–4 lines).

Return ONLY valid JSON with this exact structure (no markdown, no code blocks, no explanations):

{{
    "match_percentage": <number 0-100>,
    "ats_score": <number 0-100>,
    "skills": {{
        "extracted": [<array of skills found in resume>],
        "matched": [<array of skills that match job description>],
        "missing": [<array of required skills not in resume>]
    }},
    "weak_sections": [<array of weak sections like "summary", "projects", etc>],
    "suggestions": [<array of specific, actionable suggestions>],
    "improved_summary": "<3-4 line professional summary>"
}}"""

    @abstractmethod
    def analyze_resume(self, resume: str, job_description: str) -> dict:
        """
        Analyze a resume against a job description.

        Args:
            resume: The resume text
            job_description: The job description text

        Returns:
            Dictionary with analysis results (match_percentage, ats_score, skills, etc.)

        Raises:
            ValueError: If API key is not set or response is invalid
            RuntimeError: If API call fails
        """
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Send messages to the LLM for multi-turn conversation.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response text

        Raises:
            ValueError: If API key is not set
            RuntimeError: If API call fails
        """
        pass

    @staticmethod
    def _build_prompt(resume: str, job_description: str) -> str:
        """Build the analysis prompt"""
        return LLMProvider.ANALYSIS_PROMPT_TEMPLATE.format(
            resume=resume, job_description=job_description
        )

    @staticmethod
    def _parse_json_response(response_text: str) -> dict:
        """
        Parse JSON response, handling markdown code blocks.

        Args:
            response_text: Raw text response from LLM

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {text}")
