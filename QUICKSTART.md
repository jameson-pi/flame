# 🚀 Quick Start Guide - Flame CLI

Get up and running with Flame in 5 minutes!

## Step 1: Install Flame

### 1. **Install via pip** (recommended to use a virtual environment):

```bash
# Optional: Setup virtual environment
python -m venv venv
venv\Scripts\activate # Windows
# source venv/bin/activate # macOS/Linux

# Install Flame
pip install flamecli
```

## Step 2: Configure API Key

Run the built-in setup command:

```bash
flame --setup
```

It will ask you to enter:
1. `FLAME_API_KEY`: Your API key.
2. `FLAME_MODEL`: Defaults to the recommended `qwen/qwen3-32b` if you skip it.

**Where to get your API key?**
- Get your API key from openrouter or your preferred provider
- Copy your API key from your dashboard

## Step 3: Verify Setup

```bash
flame --check
```

Expected output:
```
🔍 Testing connection to API...
✅ Connection successful!
```

If this fails:
1. Check your `.env` file is configured correctly
2. Verify internet connection
3. Run with `--debug` for details

## Step 4: Start Chatting!

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
... 
```

