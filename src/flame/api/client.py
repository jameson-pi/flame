"""Hack Club AI API wrapper for streaming and non-streaming responses."""

import os
import time
import random
from typing import Iterator, Optional, Any, Callable
from openrouter import OpenRouter
from rich.console import Console


class HackClubAIClient:
    """Wrapper around OpenRouter SDK for Hack Club AI."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        console: Optional[Console] = None,
    ):
        """Initialize the Hack Club AI client.
        
        Args:
            api_key: API key for Hack Club AI (defaults to HACK_CLUB_API_KEY env var)
            base_url: API base URL (defaults to HACK_CLUB_API_BASE_URL env var)
            model: Model name (defaults to HACK_CLUB_MODEL env var)
            console: Rich console for output (optional)
        """
        self.api_key = api_key or os.getenv("HACK_CLUB_API_KEY")
        self.base_url = base_url or os.getenv("HACK_CLUB_API_BASE_URL", "https://ai.hackclub.com/proxy/v1")
        self.model = model or os.getenv("HACK_CLUB_MODEL", "google/gemini-3-flash-preview")
        self.console = console or Console()

        if not self.api_key:
            raise ValueError(
                "HACK_CLUB_API_KEY not found. Please set it in .env or pass it as an argument."
            )

        self.client = OpenRouter(
            api_key=self.api_key,
            server_url=self.base_url,
        )

    def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: Optional[str] = None,
    ) -> Iterator[str]:
        """Stream chat response from Hack Club AI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            model: Model name to use (overrides default)
            
        Yields:
            Streamed response chunks as strings
        """
        def _attempt():
            response = self.client.chat.send(
                model=model or self.model,
                messages=messages,
                stream=True,
            )
            for chunk in response:
                if isinstance(chunk, dict):
                    if 'choices' in chunk and chunk['choices']:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield content
                elif hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    content = getattr(delta, "content", "")
                    if content:
                        yield content

        return self._with_retry(_attempt)

    def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: Optional[str] = None,
    ) -> str:
        """Get non-streaming chat response from Hack Club AI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            model: Model name to use (overrides default)
            
        Returns:
            Complete response text
        """
        def _attempt():
            response = self.client.chat.send(
                model=model or self.model,
                messages=messages,
                stream=False,
            )
            # Handle list response or single object
            if isinstance(response, list):
                if response and hasattr(response[0], 'choices'):
                    return response[0].choices[0].message.content
                return ""
            
            if hasattr(response, 'choices'):
                return response.choices[0].message.content
            
            return str(response)

        return self._with_retry(_attempt)

    def _with_retry(self, func: Callable, max_retries: int = 3, base_delay: float = 1.0) -> Any:
        """Retry a function with exponential backoff."""
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                # Only retry on certain errors (simplified here to retry on most unless it's a clear config error)
                if "Authentication" in str(e) or "401" in str(e):
                    raise
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                    if self.console:
                        self.console.print(f"[yellow]⚠️  API error: {e}. Retrying in {delay:.1f}s... (Attempt {attempt + 1}/{max_retries})[/yellow]")
                    time.sleep(delay)
                else:
                    if self.console:
                        self.console.print(f"[red]❌ Max retries reached. Last error: {e}[/red]")
                    raise last_exception

    def validate_connection(self) -> bool:
        """Test connection to Hack Club AI API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.chat_complete(
                messages=[{"role": "user", "content": "say 'ok'"}],
                max_tokens=10,
            )
            return bool(response)
        except Exception:
            return False

