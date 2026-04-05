"""Hack Club AI API wrapper for streaming and non-streaming responses."""

import os
from typing import Iterator, Optional
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
        self.model = model or os.getenv("HACK_CLUB_MODEL", "qwen/qwen3-32b")
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
    ) -> Iterator[str]:
        """Stream chat response from Hack Club AI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            
        Yields:
            Streamed response chunks as strings
        """
        try:
            response = self.client.chat.send(
                model=self.model,
                messages=messages,
                stream=True,
            )

            for chunk in response:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    content = getattr(delta, "content", "")
                    if content:
                        yield content
        except Exception as e:
            self.console.print(f"[red]Error streaming response: {e}[/red]")
            raise

    def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Get non-streaming chat response from Hack Club AI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            
        Returns:
            Complete response text
        """
        try:
            response = self.client.chat.send(
                model=self.model,
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
        except Exception as e:
            self.console.print(f"[red]Error getting response: {e}[/red]")
            raise

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

