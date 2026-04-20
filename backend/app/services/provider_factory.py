import os
from typing import Optional
from .llm_provider import LLMProvider
from .claude_client import ClaudeProvider
from .groq_provider import GroqProvider


def get_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Get an LLM provider instance.

    Provider selection order:
    1. Explicit provider_name parameter (if provided)
    2. LLM_PROVIDER environment variable
    3. Default: "claude"

    Args:
        provider_name: Optional provider name ("claude" or "groq")

    Returns:
        An instance of the selected LLM provider

    Raises:
        ValueError: If provider name is invalid or required API key is not set
    """
    # Determine which provider to use
    selected_provider = provider_name or os.getenv("LLM_PROVIDER", "claude")
    selected_provider = selected_provider.lower().strip()

    # Validate provider
    valid_providers = {"claude", "groq"}
    if selected_provider not in valid_providers:
        raise ValueError(
            f"Invalid provider: {selected_provider}. "
            f"Must be one of: {', '.join(valid_providers)}"
        )

    # Create and return provider instance
    try:
        if selected_provider == "claude":
            return ClaudeProvider()
        elif selected_provider == "groq":
            return GroqProvider()
    except ValueError as e:
        # Re-raise ValueError (missing API key)
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {selected_provider} provider: {str(e)}")
