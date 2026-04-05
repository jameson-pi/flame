# 🔥 Flame - Technical Implementation Guide

## Overview

**Flame** is a comprehensive AI-powered CLI coding assistant built with Python, integrating the API for generative capabilities. This document provides technical details about the architecture, implementation patterns, and key design decisions.

---

## Architecture

### High-Level Design

```
┌──────────────────────────────────────────────────────────┐
│                    User Terminal                          │
│                 (Interactive REPL)                        │
└──────────────┬───────────────────────────────────────────┘
               │
        ┌──────▼────────┐
        │   main.py     │ Entry point with arg parsing
        │   (Config &   │ and environment setup
        │    Init)      │
        └──────┬────────┘
               │
        ┌──────▼──────────┐
        │  cli/repl.py    │ Interactive loop, message
        │  (REPL Core)    │ history, command routing
        └──────┬──────────┘
               │
        ┌──────┴──────────────────────┐
        │                             │
        ▼                             ▼
   ┌─────────────┐           ┌──────────────────┐
   │ api/client  │           │ cli/executor     │
   │ (API Wrapper)│          │ (File/Cmd Exec)  │
   │             │           │                  │
   │ • Stream    │           │ • File ops       │
   │ • Complete  │           │ • Command exec   │
   │ • Validate  │           │ • Safety checks  │
   └─────────────┘           └──────────────────┘
        │                             │
        ▼                             ▼
   ┌─────────────────────────────────────────┐
   │ API                        │
   │ (https://api.example.com/proxy/v1)      │
   │ Model: qwen/qwen3-32b                   │
   └─────────────────────────────────────────┘
        │
        └─────── System Context ────────┐
                                        ▼
                               ┌──────────────────┐
                               │utils/context.py  │
                               │(System Context)  │
                               │                  │
                               │• OS info         │
                               │• Git status      │
                               │• Project tree    │
                               │• File summary    │
                               └──────────────────┘
```

---

## Module Breakdown

### 1. **main.py** - Entry Point

**Responsibility**: CLI initialization, argument parsing, and dependency injection

**Key Functions**:
- `main()`: Parses CLI arguments, initializes API client, starts REPL
- Environment variable loading via `python-dotenv`
- Connection validation (`--check` flag)
- Debug mode support

**Design Pattern**: Dependency Injection
- REPL receives fully-configured client
- Config isolated from business logic

**Command-Line Arguments**:
```
--version       Show version
--check         Test API connection
--dir DIR       Override working directory
--model MODEL   Override AI model
--debug         Enable debug output
```

---

### 2. **api/client.py** - API Wrapper

**Responsibility**: Encapsulate API communication with streaming and error handling

**Key Classes**:

#### `APIClient`

**Methods**:
- `__init__()`: Initialize with API key, base URL, and model
  - Validates API key is present
  - Defaults to environment variables
  
- `chat_stream()`: Stream responses
  - Iterates over OpenRouter SDK chunks
  - Yields individual tokens for real-time display
  - Exception handling with console feedback
  
- `chat_complete()`: Non-streaming responses
  - Single request-response cycle
  - Used for validation and non-interactive queries
  
- `validate_connection()`: Test API connectivity
  - Sends minimal test message
  - Returns boolean success status

**Error Handling**:
- API key validation at initialization
- Try-catch on stream operations
- Detailed error messages to console

**Streaming Implementation**:
```python
for chunk in response:
    if hasattr(chunk, 'choices') and chunk.choices:
        delta = chunk.choices[0].delta
        if hasattr(delta, 'content') and delta.content:
            yield delta.content  # Token-by-token streaming
```

---

### 3. **utils/context.py** - System Context Collector

**Responsibility**: Gather environment data to inject as AI context

**Key Classes**:

#### `SystemContext`

**Methods**:
- `get_os_info()`: Returns OS and Python version
  - Format: "Windows 10 | Python 3.11.0"
  
- `get_git_status()`: Optional git repository info
  - Runs `git status --porcelain --branch`
  - Returns None if not in git repo
  - 2-second timeout to prevent hangs
  
- `get_project_structure()`: Directory tree
  - Recursive traversal up to 2 levels deep
  - Filters hidden files and common ignore patterns
  - Max 10 entries per directory to prevent spam
  
- `get_file_summary()`: File count by extension
  - Recursive walk of project
  - Top 5 extensions by frequency
  
- `get_full_context()`: Complete formatted context string
  - Combines all above methods
  - Human-readable formatting with emojis
  
- `get_context_prompt()`: System message for AI
  - Injects context as initial system role
  - Primes AI with project awareness

**Design Pattern**: Information Aggregation
- Multiple data sources (OS, git, filesystem)
- Single responsible interface
- Lazy evaluation (only called when needed)

---

### 4. **cli/executor.py** - File & Command Execution

**Responsibility**: Safe, user-approved execution of file ops and commands

**Key Classes**:

#### `FileExecutor`

**Methods**:
- `_is_path_safe()`: Validates path is within base_dir
  - Uses `Path.resolve().relative_to()` pattern
  - Prevents directory traversal attacks
  
- `suggest_file_creation()`:
  - Shows full file content preview (first 30 lines)
  - Requests user confirmation with `Confirm.ask()`
  - Creates parent directories if needed
  - Returns boolean success
  
- `suggest_file_edit()`:
  - Generates unified diff of changes
  - Highlights with syntax coloring (diff mode)
  - Requires explicit approval before writing
  - Overwrites with confirmation only

**Safety Features**:
- Path validation before any operation
- Diff preview prevents surprises
- Parent directory creation is idempotent

#### `CommandExecutor`

**Attributes**:
- `DANGEROUS_PATTERNS`: Regex list of blocked commands
  - `rm -rf /`: Recursive root deletion
  - `sudo`: Privilege escalation
  - `dd`: Disk operations
  - `mkfs`: Filesystem formatting
  - Fork bomb pattern: `:(){ : | : & };:`

**Methods**:
- `is_dangerous()`: Regex matching against patterns
  - Case-insensitive matching
  - Returns True if any pattern matches
  
- `suggest_command()`:
  - Shows command with description
  - Checks dangerous patterns
  - Requests user approval
  - Executes with 30-second timeout
  - Captures stdout + stderr
  - Returns tuple: (success, output)

**Timeout Protection**:
```python
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    timeout=30,  # Force kill after 30s
)
```

---

### 5. **cli/repl.py** - Interactive REPL

**Responsibility**: Main event loop, message management, and command routing

**Key Classes**:

#### `REPL`

**Initialization**:
```python
def __init__(self, api_client, working_dir, history_file):
    self.client = api_client              # API wrapper
    self.system_context = SystemContext() # Context collector
    self.file_executor = FileExecutor()   # File operations
    self.command_executor = CommandExecutor()  # Command execution
    self.messages = []                    # Chat history
    self.add_system_message()             # Inject context
```

**Message History Pattern**:
- `messages` list maintains full conversation
- System context added as first message
- User/assistant messages appended chronologically
- Enables multi-turn context retention

**Core Methods**:

- `add_system_message()`: Inject initial context
  - Uses `system_context.get_context_prompt()`
  - Sets role: "system", content: full context
  
- `print_welcome()`: ASCII art header and instructions
  
- `print_help()`: Show available commands
  
- `handle_command()`: Route special commands
  - `help`: Show help
  - `context`: Display system context
  - `clear`: Reset message history
  - `exit`: Clean shutdown
  - `/run`: Command execution
  - `/create`, `/edit`: File operations
  
- `stream_response()`: Core interaction loop
  - Append user message to history
  - Stream response chunks from API
  - Collect full response
  - Append to history for context
  
- `run()`: Main loop with signal handling
  - Prompt for user input (multiline capable)
  - Handle special commands
  - Stream responses
  - Graceful exit on Ctrl+C

**Prompt Toolkit Integration**:
```python
prompt_session = PromptSession(
    history=FileHistory("~/.flame_history")
)
user_input = prompt_session.prompt(
    "[cyan]You:[/cyan] ",
    multiline=True,  # Ctrl+Enter for newlines
)
```

**Signal Handling**:
- SIGINT (Ctrl+C) triggers graceful shutdown
- Exits event loop cleanly

---

## Data Flow

### Chat Message Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. User enters message in REPL                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2. Special command? (help, clear, exit, etc.)       │
│    Yes → Handle and return to prompt                │
│    No → Continue                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3. Append user message to history                   │
│    [{role: "system", content: context},             │
│     {role: "user", content: "..."},                 │
│     {role: "assistant", content: "..."},             │
│     {role: "user", content: new_message}]           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4. Send full history to API                         │
│    POST /chat.completions with stream=true          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5. Stream response chunks                           │
│    Display incrementally to terminal                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 6. Append complete response to history              │
│    [{..., {role: "assistant", content: full_resp}] │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 7. Return to prompt for next input                  │
└─────────────────────────────────────────────────────┘
```

---

## Security Model

### Defense-in-Depth Approach

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: API Key Security                            │
│ • Stored in .env (gitignored)                        │
│ • Environment variable support                       │
│ • Validation on startup                              │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Layer 2: Path Validation (Files)                     │
│ • All paths resolved and checked                     │
│ • Must be within project directory                   │
│ • Directory traversal prevention                     │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Layer 3: User Approval Gates                         │
│ • File creation requires explicit confirmation       │
│ • Command execution requires explicit confirmation   │
│ • Diff/preview before any modification               │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Layer 4: Dangerous Pattern Detection                 │
│ • Regex matching on commands                         │
│ • Blocks rm -rf, sudo, dd, mkfs, fork bombs          │
│ • Extensible pattern list                            │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Layer 5: Runtime Limits                              │
│ • 30-second command timeout                          │
│ • Stderr capture for error detection                 │
│ • Process termination on timeout                     │
└──────────────────────────────────────────────────────┘
```

### Approval Workflow

```
User Request (File/Command)
         │
         ▼
   Show Preview
   (Diff for files, full command for exec)
         │
         ▼
   Ask Confirmation [y/n]
   (Require explicit 'y')
         │
     ┌───┴───┐
     │       │
     ▼       ▼
    Yes      No
     │       │
     │       └─→ Return false
     │            (No action taken)
     ▼
   Execute with Safety Checks
   (Path validation, timeout, etc.)
     │
     ▼
   Report Result
```

---

## Key Design Decisions

### 1. **Streaming vs Non-Streaming**

**Decision**: Default to streaming with fallback

**Rationale**:
- Streaming provides real-time feedback
- Matches user expectations (like ChatGPT)
- Better UX for long responses
- Non-streaming available for simple operations

```python
# Streaming for interactive chat
for chunk in client.chat_stream(messages):
    console.print(chunk, end="")

# Non-streaming for validation
response = client.chat_complete(messages)
```

### 2. **Message History Storage**

**Decision**: In-memory list with optional file-based session history

**Rationale**:
- Simplicity: No database needed
- Context retention: Full conversation available
- CLI convenience: History survives shell restart
- Extensibility: Easy to add persistence

### 3. **Context Injection**

**Decision**: System context as first message in chat

**Rationale**:
- AI aware of environment without overhead
- No per-message context overhead
- Single source of truth for context
- Easily updated between sessions

### 4. **Safety via Approval**

**Decision**: User approval for all mutations

**Rationale**:
- Prevents accidental data loss
- Aligns with principle of least surprise
- User maintains control
- Enables auditability

### 5. **Dangerous Pattern Regex**

**Decision**: Regex blocklist (not whitelist)

**Rationale**:
- Flexibility: Allows most commands
- UX: Doesn't frustrate users
- Maintainability: Easy to add patterns
- Trade-off: Users can still shoot themselves

---

## Error Handling Strategy

### API Layer Errors

```python
try:
    for chunk in self.client.chat_stream(messages):
        yield chunk
except Exception as e:
    self.console.print(f"[red]Error streaming response: {e}[/red]")
    raise
```

### File Operation Errors

```python
if not self._is_path_safe(target_path):
    self.console.print("[red]❌ Security Error: Cannot create file...")
    return False

try:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content)
except Exception as e:
    self.console.print(f"[red]File error: {e}[/red]")
    return False
```

### Command Execution Errors

```python
try:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        output = result.stderr
except subprocess.TimeoutExpired:
    self.console.print("[red]❌ Command timed out after 30 seconds[/red]")
except Exception as e:
    self.console.print(f"[red]❌ Error executing command: {e}[/red]")
```

---

## Extension Points

### Adding New Dangerous Patterns

```python
# In cli/executor.py
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"your\s+new\s+pattern",  # Add here
]
```

### Adding New Commands

```python
# In cli/repl.py
def handle_command(self, user_input):
    if stripped.startswith("/newcommand "):
        # Your implementation
        return None
    return user_input
```

### Custom System Context

```python
# In utils/context.py
def get_custom_info(self):
    # Gather whatever context you need
    return info

def get_full_context(self):
    context_parts = [
        # ... existing ...
        self.get_custom_info(),  # Add new info
    ]
    return "\n".join(context_parts)
```

---

## Testing Strategy

### Suggested Test Coverage

1. **API Client Tests**
   - Connection validation
   - Streaming vs non-streaming
   - Error handling
   - Token injection

2. **Context Tests**
   - Project structure parsing
   - Git status detection
   - File counting

3. **Executor Tests**
   - Path safety validation
   - File creation/editing
   - Dangerous pattern detection
   - Command execution

4. **REPL Tests**
   - Command routing
   - Message history
   - Streaming integration

### Example Test

```python
def test_path_safety():
    executor = FileExecutor(base_dir="/project")
    
    # Safe: within project
    assert executor._is_path_safe(
        Path("/project/src/main.py")
    )
    
    # Unsafe: outside project
    assert not executor._is_path_safe(
        Path("/etc/passwd")
    )
```

---

## Performance Considerations

### Streaming Performance

- Chunks streamed immediately (no buffering)
- Console output happens per-token
- Network latency hidden by streaming

### Context Performance

- Git status: 2-second timeout prevents hangs
- Directory traversal: Limited to 10 entries/dir
- File regex: Runs async, doesn't block UI

### Memory Usage

- Message history: Keeps full conversation
- Limit conversation via `/clear` command
- Optional persistence layer for large histories

---

## Future Enhancements

### Phase 2 Features

1. **Multi-file Operations**
   - Batch file creation
   - Project scaffolding

2. **Conversation Management**
   - Save/load sessions
   - Conversation export (markdown/JSON)

3. **Custom Plugins**
   - User-defined commands
   - Custom context providers

4. **Advanced Security**
   - Command fingerprinting
   - Execution sandboxing
   - Activity logging

5. **Performance**
   - Database for history
   - Offline mode with caching
   - Streaming response optimization

---

## Debugging Tips

### Enable Debug Mode

```bash
python main.py --debug
```

### Check API Connection

```bash
python main.py --check
```

### Inspect Message History

Add to REPL:
```python
# In handle_command()
elif stripped == "history":
    import json
    self.console.print(json.dumps(self.messages, indent=2))
```

### Validate Dangerous Pattern

```python
from cli.executor import CommandExecutor
executor = CommandExecutor()
print(executor.is_dangerous("rm -rf /"))  # True
print(executor.is_dangerous("pip install"))  # False
```

---

## References

- **API Docs**: https://api.example.com
- **OpenRouter SDK**: https://github.com/openrouter/openrouter-py
- **Rich Library**: https://rich.readthedocs.io/
- **Prompt Toolkit**: https://python-prompt-toolkit.readthedocs.io/

---

**Last Updated**: April 4, 2026
**Implementation Status**: ✅ Complete Phase 1

