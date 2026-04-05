# 🚀 Quick Start Guide - Flame CLI

Get up and running with Flame in 5 minutes!

## Step 1: Install Dependencies

```bash
# Navigate to the project
cd flame

# Activate virtual environment (if not already activated)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Key

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API key
# Open .env in your editor and update:
# FLAME_API_KEY=your_api_key_here
```

**Where to get your API key?**
- Sign up at https://api.example.com
- Copy your API key from your dashboard
- Paste it into `.env`

## Step 3: Verify Setup

```bash
python main.py --check
```

Expected output:
```
🔍 Testing connection to API...
✅ Connection successful!
```

If this fails:
1. Check your `.env` file is configured
2. Verify internet connection
3. Confirm API key is correct
4. Run with `--debug` for details

## Step 4: Start Chatting!

```bash
python main.py
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

Try these prompts:

```
You: What's in my current directory?
You: help
You: Create a Python script that prints hello world
You: How do I install a Python package?
```

## Step 5: Explore Features

### View System Context

```
You: context

📍 System Context:
📍 Working Directory: C:\Users\pisci\PycharmProjects\flame
🖥️  System: Windows 10 | Python 3.11.0
📂 Project Structure:
  flame/
  ├── main.py
  ├── api/
  ...
```

### Ask for File Creation

```
You: Create a requirements-dev.txt with pytest and black

🤖 Flame: I'll create a requirements-dev.txt file...

📝 Create File: requirements-dev.txt
Preview:
pytest>=7.0.0
black>=23.0.0
...

✅ Create this file? [y/n]: y
✅ File created: requirements-dev.txt
```

### Clear History

```
You: clear
✅ Conversation history cleared
```

### Exit

```
You: exit
👋 Goodbye!
```

## Common Tasks

### Ask for Code Help

```
You: I have this Python code that's broken. Can you help?
[paste your code]

🤖 Flame: I see the issue...
```

### Get Project Analysis

```
You: Analyze my project structure and suggest improvements

🤖 Flame: Your project has...
```

### Learn Something

```
You: Explain how Python decorators work with examples

🤖 Flame: Decorators are...
```

### Get Command Help

```
You: How do I create a git commit message that follows best practices?

🤖 Flame: Here's a well-written commit message...
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | New line in multi-line input |
| Ctrl+C | Exit program |
| Up/Down | Navigate command history |
| Ctrl+L | Clear screen |
| Ctrl+R | Search history (in some shells) |

## Troubleshooting

### "Connection failed"

```bash
# Check configuration
cat .env

# Make sure FLAME_API_KEY is set
# Test with verbose output
python main.py --check --debug
```

### "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or using pyproject.toml
pip install -e .
```

### "Command won't execute"

Commands matching these patterns are blocked (for safety):
- `rm -rf /` (recursive deletion)
- `sudo` (privilege escalation)
- `dd` (disk operations)
- `mkfs` (format filesystem)

This is intentional! Use safer alternatives.

### "File creation rejected"

Make sure:
1. File path is within the project directory
2. Parent directories exist (or will be created)
3. You have write permissions
4. You confirmed with `[y/n]` prompt

## Next Steps

### Learn More

- Read [README.md](README.md) for full feature list
- Check [TECHNICAL.md](TECHNICAL.md) for architecture details
- Review security features in README

### Customize

Edit configurations in `.env`:
```bash
FLAME_MODEL=llama2          # Change AI model
CLI_THEME=light                 # Change theme
DEBUG=true                       # Enable debug mode
```

### Use Different Directory

```bash
# Analyze another project
python main.py --dir /path/to/other/project
```

## Tips for Best Results

1. **Be Specific**: "Create a Flask app with SQLAlchemy" vs "Create an app"
2. **Use Context**: Say "in my Python project" if relevant
3. **Review Changes**: Always check diffs before approving file edits
4. **Ask Clarifying**: If output seems off, ask follow-up questions
5. **Use `context` Command**: AI performs better with recent context refresh

## Getting Help

If stuck:
1. Try `help` command in Flame
2. Check this Quick Start again
3. Review README.md for examples
4. Run with `--debug` flag for detailed errors
5. Check your `.env` configuration

## Example Session

```
PS C:\flame> python main.py

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔥 Flame - AI Coding Assistant      ┃
┃ Powered by API              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Type 'help' for commands, 'exit' to quit

You: Show me a Python function to calculate fibonacci

🤖 Flame: Here's a recursive Fibonacci implementation:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

You: Make it iterative for better performance

🤖 Flame: Great idea! Here's an iterative approach:

def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

You: Create a test file for this

📝 Create File: test_fibonacci.py
Preview:
def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55

✅ Create this file? [y/n]: y
✅ File created: test_fibonacci.py

You: exit
👋 Goodbye!
```

---

**Happy coding with Flame! 🔥**

