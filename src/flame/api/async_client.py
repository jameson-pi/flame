import os
import httpx
from typing import AsyncIterator, Optional
from rich.console import Console

class AsyncHackClubAIClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("HACK_CLUB_API_KEY")
        self.base_url = base_url or os.getenv("HACK_CLUB_API_BASE_URL", "https://ai.hackclub.com/proxy/v1")
        self.model = model or os.getenv("HACK_CLUB_MODEL", "qwen/qwen3-32b")
        
        if not self.api_key:
            raise ValueError("HACK_CLUB_API_KEY not found.")

    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        # Simple SSE parsing
                        content = line[6:]
                        if content == "[DONE]":
                            break
                        # In a real app, use json.loads(content) here
                        yield content

### Step 4: Update the Test
Now that we changed the structure, we need to update the test I created earlier.