import pytest
from flame.api.client import APIClient

def test_client_init():
    # This will fail without an API key, so we mock or handle it
    import os
    os.environ["FLAME_API_KEY"] = "fake-key"
    client = APIClient()
    assert client.api_key == "fake-key"

---

### Suggested Next Steps
1. **Interactive UI**: Would you like me to help integrate `prompt-toolkit`'s bottom toolbar to show the current model or token usage?
2. **System Prompts**: We could add a `src/flame/utils/prompts.py` to manage specialized "coding mode" vs "debug mode" instructions.
3. **History**: Implement a local SQLite or JSON history manager so users can reference previous chats.

Which one sounds most useful for your workflow?