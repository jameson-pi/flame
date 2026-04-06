# 🔥 Flame - AI-Powered CLI Coding Assistant

An intelligent command-line interface (CLI) application that functions as an AI coding assistant directly in your terminal, powered by **API**.

## ✨ Features

- **Interactive REPL**: Continuous chat loop with full conversation context
- **System Awareness**: Automatically gathers context about your environment (OS, project structure, git status)
- **Real-time Streaming**: Responses stream into the terminal as they're generated
- **Safe File Operations**: Create and edit files with intelligent diff preview and approval prompts
- **Command Execution**: Suggest and safely execute terminal commands with user approval
- **Dangerous Command Detection**: Blocks potentially harmful commands while allowing safe ones
- **Multi-turn Conversations**: Maintains full chat history across sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A API key
- pip or poetry for dependency management

### Installation

1. **Install via pip** (recommended to use a virtual environment):
   ```bash
   pip install flamecli
   ```

2. **Setup configuration**:
   ```bash
   # Interactively securely configure your API key and preferences
   flame --setup
   ```

### Test Connection

Before running the REPL, verify your setup:

```bash
flame --check
```

Expected output:
```
🔍 Testing connection to API...
✅ Connection successful!
```

### Start the CLI

```bash
flame
```

You'll see:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔥 Flame - AI Coding Assistant      ┃
┃ Powered by API              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Type 'help' for commands, 'exit' to quit

You: _
```

## 💬 Usage Examples

### Basic Chat

```
You: What does this code do?
[paste code]

🤖 Flame: This code does...
```

### Get Project Context

```
You: help

Available Commands:

  help          - Show this help message
  context       - Show current system context
  clear         - Clear conversation history
  exit          - Exit the program
  /run <cmd>    - Suggest running a command (AI-aware)
  /edit <file>  - Suggest editing a file
  /create <file> - Suggest creating a file
```

### View System Context

```
You: context

📍 System Context:

📍 Working Directory: /path/to/project
🖥️  System: Linux 6.1.0 | Python 3.11.0
🌿 Git Status: On branch main
📂 Project Structure:
  project-name/
  ├── main.py
  ├── utils/
  └── ...
📊 File Summary:
  Total files: 24
  .py: 12
  .md: 3
  ...
```

### AI-Suggested File Creation

```
You: Create a requirements.txt with common Python packages

🤖 Flame: I'll create a requirements.txt with popular packages...

📝 Create File: requirements.txt
   Suggested by AI assistant

Preview:
requests>=2.28.0
python-dotenv>=0.20.0
rich>=13.0.0
...

✅ Create this file? [y/n]: y
✅ File created: requirements.txt
```

### AI-Suggested Command Execution

```
You: How do I install the dependencies?

🤖 Flame: You can run pip install...

🔧 Run Command:
   Suggested by AI assistant

Command:
   pip install -r requirements.txt

✅ Execute this command? [y/n]: y
✅ Command executed successfully

Output:
Collecting requests...
...
```

### Clear History

```
You: clear
✅ Conversation history cleared
```

## 🏗️ Architecture

### Directory Structure

```
flame/
├── api/
│   ├── __init__.py
│   └── client.py          # API wrapper
├── cli/
│   ├── __init__.py
│   ├── repl.py            # Interactive REPL loop
│   └── executor.py        # File and command execution
├── utils/
│   ├── __init__.py
│   └── context.py         # System context collector
├── main.py                # Entry point
├── pyproject.toml         # Project configuration
├── .env.example           # Environment template
└── .env                   # Your configuration (gitignored)
```

### Component Interaction

```
┌─────────────────────────────────────────┐
│         main.py (Entry Point)           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    REPL (cli/repl.py)                  │
│  ├─ Interactive loop                   │
│  ├─ Message history                    │
│  └─ Command handling                   │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┬────────────┐
        ▼             ▼            ▼
   ┌────────┐   ┌──────────┐  ┌─────────┐
   │HackClubAI API    │   │FileExecutor │ │CommandExecutor
   │(api/client.py)   │   │(executor.py)│ │(executor.py)
   │                  │   │             │ │
   │• Streaming       │   │• Safe file  │ │• Command checks
   │• Non-streaming   │   │  ops        │ │• Approval prompts
   │• Error handling  │   │• Diffs      │ │• History
   └────────┬────────┘   └──────────────┘ └─────────────┘
            │
      SystemContext
      (utils/context.py)
      ├─ OS info
      ├─ Git status
      ├─ Project structure
      └─ File summary
```

## 🔒 Security Features

### File Operations Security

1. **Path Validation**: All file paths are validated to stay within the project directory
2. **Diff Preview**: Before writing, users see exactly what changes will be made
3. **User Approval**: Every file creation/edit requires explicit user confirmation
4. **Safe by Default**: Operations are blocked if path escapes project root

### Command Execution Security

1. **Dangerous Pattern Detection**: Blocks commands matching risky patterns:
   - `rm -rf /` (recursive root deletion)
   - `sudo` (privilege escalation)
   - `dd` (disk operations)
   - `mkfs` (filesystem formatting)
   - Fork bombs

2. **User Approval**: Every command execution requires explicit confirmation
3. **Timeout Protection**: Commands are forcibly terminated after 30 seconds
4. **Error Reporting**: Command failures are clearly reported

### API Key Security

- Store in `.env` file (add to `.gitignore` automatically)
- Never commit `.env` to version control
- Use environment variables in production
- Supports `.env.example` for template sharing

## 📋 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# Required: Your API key
FLAME_API_KEY=hf_xxxxxxxxxxxxx

# Optional: API endpoint (usually pre-configured)
FLAME_API_BASE_URL=https://api.example.com/proxy/v1

# Optional: AI model to use
FLAME_MODEL=qwen/qwen3-32b

# Optional: CLI settings
CLI_THEME=dark
DEBUG=false
```

## 🎮 CLI Options

```bash
python main.py --help

usage: main.py [-h] [--version] [--check] [--dir DIR] [--model MODEL] [--debug]

Flame - AI Coding Assistant powered by API

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --check               Test connection to API
  --setup               Interactive setup to configure your API key and settings
  --dir DIR             Working directory (defaults to current directory)
  --model MODEL         AI model to use (overrides FLAME_MODEL env var)
  --debug               Enable debug mode
```

## 🐛 Troubleshooting

### Connection Failed

**Error**: `Connection failed. Check your API key and network.`

**Solutions**:
1. Verify API key is correct in `.env`
2. Check internet connection
3. Verify API base URL is correct
4. Test with: `python main.py --check --debug`

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'api'`

**Solutions**:
1. Ensure you're in the project root directory
2. Virtual environment is activated
3. Dependencies are installed: `pip install -e .`

### Command Won't Execute

**Error**: `Dangerous Command Detected`

**Solutions**:
1. Command matches safety patterns (by design)
2. Use `--debug` to see pattern matching
3. Use safer alternative commands
4. File path must be within project directory

## 📚 Advanced Usage

### Using with Different Models

```bash
# Override model at runtime
python main.py --model llama2

# Or set in .env:
FLAME_MODEL=llama2
```

### Using Different Working Directory

```bash
# Analyze a different project
python main.py --dir /path/to/other/project
```

### Debug Mode

```bash
# See detailed error messages
python main.py --debug
```

## 🔧 Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black api/ cli/ utils/ main.py

# Lint
flake8 api/ cli/ utils/ main.py
```

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 🙋 Support

Need help? Try:

1. Check `.env` configuration
2. Run `python main.py --check` to verify setup
3. Use `--debug` flag for detailed error messages
4. Review this README for common issues

---

**Made with 🔥 by API Community**

