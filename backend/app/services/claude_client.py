import os
from anthropic import Anthropic
from typing import List, Dict
from .llm_provider import LLMProvider


class ClaudeProvider(LLMProvider):
    """Claude API implementation of LLMProvider"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic()

    def analyze_resume(self, resume: str, job_description: str) -> dict:
        """
        Analyze a resume against a job description using Claude.

        Args:
            resume: The resume text
            job_description: The job description text

        Returns:
            Parsed JSON response with analysis results
        """
        prompt = self._build_prompt(resume, job_description)

        try:
            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract the text content
            response_text = response.content[0].text.strip()

            # Parse JSON
            analysis_data = self._parse_json_response(response_text)
            return analysis_data

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Send messages to Claude for multi-turn conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            Assistant's response text
        """
        try:
            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")


# Backwards compatibility alias
ClaudeAnalyzer = ClaudeProvider
