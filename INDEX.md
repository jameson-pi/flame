# 📚 Flame - Complete Documentation Index

Welcome to **Flame**, an AI-powered CLI coding assistant powered by Hack Club AI! Here's your navigation guide.

---

## 🚀 Start Here

### For First-Time Users
1. **[INSTALLATION.md](INSTALLATION.md)** - Step-by-step setup guide
2. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
3. **[README.md](README.md)** - Full feature overview

### For Developers
1. **[TECHNICAL.md](TECHNICAL.md)** - Architecture & implementation details
2. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What's been built
3. **Source Code** - See sections below

---

## 📁 Project Structure

```
flame/
├── 📄 Core Modules
│   ├── main.py                    # Entry point & CLI initialization
│   ├── api/client.py              # Hack Club AI API wrapper
│   ├── cli/repl.py                # Interactive REPL loop
│   ├── cli/executor.py            # File & command execution
│   └── utils/context.py           # System context collector
│
├── 📋 Documentation
│   ├── README.md                  # User guide & features
│   ├── QUICKSTART.md              # 5-minute setup
│   ├── TECHNICAL.md               # Architecture guide
│   ├── INSTALLATION.md            # Detailed setup instructions
│   ├── IMPLEMENTATION_SUMMARY.md   # What's implemented
│   └── INDEX.md                   # This file
│
├── ⚙️ Configuration
│   ├── pyproject.toml             # Project metadata
│   ├── requirements.txt           # Pip dependencies
│   ├── .env.example               # Environment template
│   ├── .gitignore                 # Git exclusions
│   ├── setup.bat                  # Windows setup script
│   └── setup.sh                   # macOS/Linux setup script
│
└── 🔧 Generated Files
    ├── .venv/                     # Virtual environment
    ├── __pycache__/               # Python cache
    ├── api/__pycache__/           # Module cache
    ├── cli/__pycache__/           # Module cache
    └── utils/__pycache__/         # Module cache
```

---

## 📖 Documentation Guide

### [INSTALLATION.md](INSTALLATION.md)
**Complete setup and troubleshooting guide**
- Automated setup scripts (Windows, macOS/Linux)
- Manual installation steps
- Configuration and environment variables
- Comprehensive troubleshooting section
- **Best for**: Getting Flame installed and running

### [QUICKSTART.md](QUICKSTART.md)
**5-minute quick start with examples**
- Installation summary
- Verification steps
- Usage examples
- Common tasks
- Keyboard shortcuts
- **Best for**: Learning basic usage quickly

### [README.md](README.md)
**Full feature overview and user guide**
- Feature list with emojis
- Complete setup instructions
- Usage examples with output
- Architecture diagram
- Security details
- Configuration options
- **Best for**: Understanding all features and capabilities

### [TECHNICAL.md](TECHNICAL.md)
**Deep dive into architecture and implementation**
- High-level architecture
- Module breakdown with code patterns
- Data flow diagrams
- Security model (5-layer defense)
- Design decisions explained
- Error handling strategy
- Extension points for customization
- **Best for**: Developers and contributors

### [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
**Summary of what's been built**
- Completed features checklist
- Architecture summary
- Project statistics
- Configuration options
- Design decisions
- Security highlights
- **Best for**: Project overview and status

---

## 🎯 Quick Navigation by Task

### "I want to install Flame"
→ Start with [INSTALLATION.md](INSTALLATION.md)

### "I want to use Flame right now"
→ Follow [QUICKSTART.md](QUICKSTART.md)

### "I want to understand the features"
→ Read [README.md](README.md)

### "I want to understand the code"
→ Study [TECHNICAL.md](TECHNICAL.md)

### "I want to contribute or extend Flame"
→ See [TECHNICAL.md](TECHNICAL.md) "Extension Points" section

### "I want to see what's been completed"
→ Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🔑 Key Features

### Core Capabilities
- **Interactive REPL** - Continuous chat with AI
- **System Awareness** - Project context injection
- **Real-time Streaming** - Live response output
- **File Operations** - Safe file creation/editing with approval
- **Command Execution** - Safe command running with safety checks
- **Message History** - Multi-turn context retention

### Security
- API key protection (`.env` file)
- Path validation (no directory traversal)
- User approval gates (all mutations require confirmation)
- Dangerous command detection (regex-based blocking)
- Runtime limits (30-second command timeout)

### User Experience
- Rich terminal formatting with colors and boxes
- Command history persistence
- Multi-line input support
- Helpful command system
- Clear error messages

---

## 💻 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **API** | Hack Club AI / OpenRouter SDK |
| **CLI Framework** | Rich (terminal styling) |
| **Input** | Prompt Toolkit (history, multiline) |
| **Config** | python-dotenv |
| **Execution** | subprocess (commands) |
| **Context** | subprocess (git), pathlib (files) |

---

## 📊 Module Reference

### `main.py` - Entry Point
**Purpose**: Initialize application, parse CLI arguments, start REPL

**Key Features**:
- Argument parsing (`--check`, `--dir`, `--model`, `--debug`)
- Environment variable loading
- API client initialization
- Connection validation
- Working directory override

**Usage**:
```bash
python main.py                    # Start interactive REPL
python main.py --check           # Test API connection
python main.py --dir /path       # Use specific directory
python main.py --debug           # Enable debug output
```

### `api/client.py` - API Wrapper
**Purpose**: Encapsulate Hack Club AI communication

**Key Classes**: `HackClubAIClient`

**Key Methods**:
- `chat_stream()` - Stream responses token-by-token
- `chat_complete()` - Get non-streaming response
- `validate_connection()` - Test API connectivity

**Design Pattern**: Wrapper with error handling

### `cli/repl.py` - Interactive Loop
**Purpose**: Main event loop and command routing

**Key Classes**: `REPL`

**Key Methods**:
- `run()` - Main event loop
- `stream_response()` - Display AI response
- `handle_command()` - Route special commands
- `add_system_message()` - Inject context

**Features**:
- Multi-turn conversation
- Command routing
- Signal handling (Ctrl+C)
- Streaming display

### `cli/executor.py` - Safe Execution
**Purpose**: File and command operations with safety

**Key Classes**:
- `FileExecutor` - Safe file creation/editing
- `CommandExecutor` - Safe command execution

**Key Methods**:
- `suggest_file_creation()` - Create file with approval
- `suggest_file_edit()` - Edit file with diff preview
- `suggest_command()` - Execute command with approval
- `is_dangerous()` - Detect dangerous patterns

**Safety Features**:
- Path validation
- User approval gates
- Dangerous pattern detection
- Timeout protection

### `utils/context.py` - System Context
**Purpose**: Gather environment data for AI awareness

**Key Classes**: `SystemContext`

**Key Methods**:
- `get_os_info()` - OS and Python version
- `get_git_status()` - Git repository status
- `get_project_structure()` - Directory tree
- `get_file_summary()` - File type counts
- `get_context_prompt()` - System message

**Features**:
- Multi-source information gathering
- Timeout protection
- Human-readable formatting

---

## 🔒 Security Architecture

### Defense Layers

```
Layer 1: API Key Security
  └─ Environment variable management (.env)

Layer 2: Path Validation
  └─ All file paths restricted to project directory

Layer 3: User Approval Gates
  └─ Diffs/previews shown before any modification

Layer 4: Dangerous Pattern Detection
  └─ Regex-based blocking of risky commands

Layer 5: Runtime Limits
  └─ 30-second timeout, process termination
```

### Blocked Command Patterns
- `rm -rf /` - Recursive root deletion
- `sudo` - Privilege escalation
- `dd` - Disk operations
- `mkfs` - Filesystem formatting
- `:(){ : | : & };:` - Fork bomb

---

## 📝 Configuration Reference

### Environment Variables (.env)

```env
# REQUIRED
HACK_CLUB_API_KEY=your_api_key_here

# OPTIONAL (pre-configured defaults)
HACK_CLUB_API_BASE_URL=https://ai.hackclub.com/proxy/v1
HACK_CLUB_MODEL=qwen/qwen3-32b

# OPTIONAL (CLI settings)
CLI_THEME=dark
DEBUG=false
```

### Command-Line Arguments

```
--version           Show version
--check             Test API connection
--dir DIR           Use different working directory
--model MODEL       Override AI model
--debug             Enable debug output
--help              Show help message
```

---

## 🚀 Getting Started Paths

### Path 1: Quick Start (5 minutes)
```
1. INSTALLATION.md → Follow setup.bat/setup.sh
2. Edit .env with API key
3. Run: python main.py --check
4. Run: python main.py
5. Try: "hello" or "help"
```

### Path 2: Deep Understanding (30 minutes)
```
1. QUICKSTART.md → Understand basics
2. README.md → Learn features
3. TECHNICAL.md → Study architecture
4. Explore source code
```

### Path 3: Developer Setup (1 hour)
```
1. INSTALLATION.md → Manual setup
2. Activate virtual environment
3. Study TECHNICAL.md
4. Review module code
5. Identify extension points
6. Plan modifications
```

---

## 🛠️ Common Tasks

### Run Flame
```bash
python main.py
```

### Test Setup
```bash
python main.py --check
```

### Use Different Model
```bash
python main.py --model llama2
```

### Analyze Different Project
```bash
python main.py --dir /path/to/other/project
```

### Debug Mode
```bash
python main.py --debug
```

### View Help in REPL
```
You: help
You: context
```

---

## 🧪 Testing Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] `.env` file created with API key
- [ ] Connection test passes (`python main.py --check`)
- [ ] REPL starts (`python main.py`)
- [ ] Basic chat works
- [ ] `/help` command shows options
- [ ] `context` command displays project info
- [ ] File/command execution with approval prompts work

---

## 📚 External Resources

### Hack Club AI
- **Website**: https://ai.hackclub.com
- **API Documentation**: https://ai.hackclub.com/docs
- **Dashboard**: https://ai.hackclub.com/dashboard

### Python & Libraries
- **Python Docs**: https://docs.python.org/3/
- **Rich Documentation**: https://rich.readthedocs.io/
- **Prompt Toolkit**: https://python-prompt-toolkit.readthedocs.io/
- **OpenRouter SDK**: https://github.com/openrouter/openrouter-py

---

## ❓ FAQ

**Q: How do I get my API key?**
A: Sign up at https://ai.hackclub.com and copy your key from the dashboard.

**Q: Can I use a different AI model?**
A: Yes! Set `HACK_CLUB_MODEL` in `.env` or use `--model` flag.

**Q: Is my API key safe?**
A: Yes! It's stored in `.env` which is gitignored. Never commit it.

**Q: Can I use Flame in different directories?**
A: Yes! Use `python main.py --dir /path/to/project`.

**Q: How do I clear my chat history?**
A: In REPL, type: `clear`

**Q: Why are some commands blocked?**
A: Dangerous patterns (like `rm -rf /`) are blocked for safety.

**Q: Can I modify the dangerous patterns list?**
A: Yes! Edit `DANGEROUS_PATTERNS` in `cli/executor.py`.

**Q: How do I update dependencies?**
A: Run `pip install --upgrade -r requirements.txt`

---

## 🤝 Contributing

Want to improve Flame? See [TECHNICAL.md](TECHNICAL.md) for:
- Extension points
- Design patterns used
- Testing recommendations
- Future enhancement ideas

---

## 📄 License

MIT License - See project for details

---

## 🎉 Next Steps

1. **Install**: Follow [INSTALLATION.md](INSTALLATION.md)
2. **Learn**: Read [QUICKSTART.md](QUICKSTART.md)
3. **Explore**: Use [README.md](README.md) for features
4. **Develop**: Study [TECHNICAL.md](TECHNICAL.md) for internals

---

**Happy coding with Flame! 🔥**

Last Updated: April 4, 2026
Status: ✅ Phase 1 Complete

