import os
from groq import Groq
from typing import List, Dict
from .llm_provider import LLMProvider


class GroqProvider(LLMProvider):
    """Groq API implementation of LLMProvider"""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)

    def analyze_resume(self, resume: str, job_description: str) -> dict:
        """
        Analyze a resume against a job description using Groq.

        Args:
            resume: The resume text
            job_description: The job description text

        Returns:
            Parsed JSON response with analysis results
        """
        prompt = self._build_prompt(resume, job_description)

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Latest available Llama 3.3 model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for more consistent JSON output
                max_tokens=1500,
            )

            # Extract the text content
            response_text = response.choices[0].message.content.strip()

            # Parse JSON
            analysis_data = self._parse_json_response(response_text)
            return analysis_data

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Send messages to Groq for multi-turn conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            Assistant's response text
        """
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")
