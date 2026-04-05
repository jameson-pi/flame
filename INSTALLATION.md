# 🔥 Flame - Complete Setup & Installation Guide

## Prerequisites

- **Python**: 3.10 or higher
- **pip**: Package manager (comes with Python)
- **Git** (optional, for version control)
- **API Account**: Get your API key from https://api.example.com

## Installation Methods

### Method 1: Automated Setup (Recommended)

#### Windows
```batch
# Double-click or run in PowerShell
setup.bat
```

#### macOS/Linux
```bash
# Make executable
chmod +x setup.sh

# Run setup
./setup.sh
```

This will:
1. Create virtual environment
2. Install all dependencies
3. Create .env file from template
4. Validate setup

---

### Method 2: Manual Setup

#### Step 1: Create Virtual Environment

**Windows (PowerShell)**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**:
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Or using pyproject.toml:
```bash
pip install -e .
```

#### Step 3: Configure API Key

```bash
# Copy the template
cp .env.example .env
# On Windows:
copy .env.example .env

# Edit .env and add your API key
# FLAME_API_KEY=your_api_key_here
```

#### Step 4: Validate Setup

```bash
python main.py --version
python main.py --check
```

---

## First Run

### 1. Verify API Connection

```bash
python main.py --check
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

Try typing:
```
You: hello
```

---

## Configuration

### Environment Variables (.env)

```env
# ============================================
# REQUIRED
# ============================================

# Your API Key
# Get it from https://api.example.com/dashboard
FLAME_API_KEY=your_api_key_here

# ============================================
# OPTIONAL (Usually Pre-configured)
# ============================================

# API endpoint
FLAME_API_BASE_URL=https://api.example.com/proxy/v1

# AI model to use
# Options: qwen/qwen3-32b (default), llama2, etc.
FLAME_MODEL=qwen/qwen3-32b

# ============================================
# OPTIONAL (CLI Settings)
# ============================================

# Terminal theme: dark or light
CLI_THEME=dark

# Enable debug output
DEBUG=false
```

### Command-Line Options

```bash
# Show help
python main.py --help

# Show version
python main.py --version

# Test API connection
python main.py --check

# Use different directory
python main.py --dir /path/to/project

# Override model
python main.py --model llama2

# Enable debug mode
python main.py --debug
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openrouter'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

Or in virtual environment:
```bash
# Make sure virtual environment is activated
python -m pip install -r requirements.txt
```

### Issue: "Connection failed. Check your API key"

**Checklist**:
1. ✅ `.env` file exists
2. ✅ `FLAME_API_KEY` is set (not empty)
3. ✅ API key is valid (check at https://api.example.com)
4. ✅ Internet connection working
5. ✅ Firewall not blocking HTTPS

**Debug**:
```bash
python main.py --check --debug
```

### Issue: "FLAME_API_KEY not found"

**Solution**: Create and configure `.env`
```bash
cp .env.example .env
# Then edit .env with your API key
```

Verify with:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('FLAME_API_KEY'))"
```

### Issue: Virtual Environment Not Activating

**Windows PowerShell**:
```powershell
# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
# Make sure you're in the project directory
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python  # Should show path in venv/
```

### Issue: pip Install Fails

**Solutions**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with --user flag
pip install --user -r requirements.txt

# Or force upgrade existing packages
pip install --force-reinstall -r requirements.txt
```

### Issue: "Python version too old"

```bash
# Check version
python --version

# Need Python 3.10+
# Download from https://www.python.org/downloads/

# After installing new version:
python3.11 -m venv venv
```

### Issue: Working Directory / Path Issues

```bash
# Make sure you're in the flame directory
cd path/to/flame

# Verify location
pwd  # or 'cd' on Windows to see current directory

# Try absolute path if needed
python main.py --dir /absolute/path/to/project
```

---

## Verification Checklist

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Virtual environment created (`venv/` directory exists)
- [ ] Virtual environment activated (prompt shows `(venv)`)
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] `.env` file created with API key
- [ ] Connection test passes (`python main.py --check`)
- [ ] REPL starts successfully (`python main.py`)

---

## Post-Installation

### Next Steps

1. **Read Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for usage examples
2. **Explore Features**: Run through the example commands
3. **Try Commands**: Use `/help` in REPL for available commands
4. **Read Documentation**: Check [README.md](README.md) for full features

### Pro Tips

```bash
# Keep virtual environment activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\Activate.ps1  # Windows PowerShell

# Check what packages are installed
pip list

# See package details
pip show openrouter

# Save updated requirements
pip freeze > requirements-lock.txt

# Use in a specific directory
python main.py --dir ~/projects/my-project
```

### Updating

```bash
# Activate virtual environment
source venv/bin/activate

# Upgrade packages
pip install --upgrade -r requirements.txt
```

---

## Getting Help

### Commands in REPL

```
You: help          # Show available commands
You: context       # Show system context
You: clear         # Clear conversation history
```

### Debug Mode

```bash
python main.py --debug
```

Shows detailed error messages and stack traces.

### Check Logs

Command history saved in: `~/.flame_history`

### Common Commands

```bash
# Verify Python
python --version

# Check pip
pip --version

# List packages
pip list

# Test import
python -c "from api.client import APIClient; print('OK')"

# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('FLAME_API_KEY', 'NOT SET'))"
```

---

## Advanced Setup

### Using Different Python Version

```bash
# Create venv with specific Python version
/usr/bin/python3.11 -m venv venv

# Or on Windows
py -3.11 -m venv venv
```

### Adding to PATH (macOS/Linux)

```bash
# Make flame executable from anywhere
echo 'alias flame="python /path/to/flame/main.py"' >> ~/.bashrc
source ~/.bashrc

# Then just run:
flame
```

### VS Code Integration

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

### PyCharm Integration

1. Open project in PyCharm
2. File → Project Settings → Python Interpreter
3. Click ⚙️ → Add...
4. Select "Existing Environment"
5. Browse to `venv/bin/python` (or `venv\Scripts\python.exe` on Windows)

---

## Security Notes

- **Never commit `.env` file**: It's in `.gitignore` for a reason
- **Never share API keys**: Keep `FLAME_API_KEY` private
- **Review diffs**: Always check file changes before approval
- **Know your commands**: Dangerous patterns are blocked, but user is responsible

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11+ |
| RAM | 256MB | 1GB+ |
| Disk | 500MB | 1GB |
| Network | Broadband | High-speed |
| OS | Windows/macOS/Linux | Any with Python |

---

## Support Resources

- **Official Documentation**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Technical Details**: [TECHNICAL.md](TECHNICAL.md)
- **API Docs**: https://api.example.com/docs
- **Python Docs**: https://docs.python.org/3/

---

**You're all set! Start with: `python main.py` 🔥**

