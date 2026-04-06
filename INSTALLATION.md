# 🔥 Flame - Complete Setup & Installation Guide

## Prerequisites

- **Python**: 3.10 or higher
- **pip**: Package manager (comes with Python)
- **API Account**: Get your API key from openrouter or your preferred provider

## Installation

The easiest and recommended way to install Flame is via `pip`:

```bash
pip install flamecli
```

### Virtual Environment (Recommended)

It's best practice to install Flame in a virtual environment:

**Windows**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install flamecli
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install flamecli
```

---

## First Run

### 1. Configure your API key

Flame requires an API key to function. The easiest way is to set it interactively via the built-in setup command:

```bash
flame --setup
```

This command will ask for your API key and AI model preference, and automatically create a `.env` file in your directory to securely store them.

Verify it works by running:

```bash
flame --check
```

Expected output:
```
🔍 Testing connection to API...
✅ Connection successful!
```

**If it fails:**
- Check your `.env` file exists
- Verify `FLAME_API_KEY` is correctly set
- Check internet connection
- Try with `--debug` flag for details

### 2. Start Chatting

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

Try typing:
```
You: hello
```

---

## Troubleshooting

### Issue: "flame: command not found"

**Solution**: This happens when your Python Scripts directory is not in your system's PATH.
- On Windows: Make sure you checked "Add Python to PATH" during Python installation. Alternatively, use `python -m flame.main`.
- On macOS/Linux: Make sure `~/.local/bin` is in your `$PATH`.

### Issue: "Connection failed. Check your API key"

**Checklist**:
1. ✅ `.env` file exists
2. ✅ `FLAME_API_KEY` is set (not empty)
3. ✅ Internet connection working
4. ✅ Firewall not blocking HTTPS

**Debug**:
```bash
flame --check --debug
```

### Issue: Virtual Environment Not Activating

**Windows PowerShell**:
```powershell
# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### Issue: "Python version too old"

```bash
# Check version
python --version

# Need Python 3.10+
# Download from https://www.python.org/downloads/
```

---

## Updating

As Flame is available on PyPI, you can update it to the latest version by running:

```bash
pip install --upgrade flamecli
```

