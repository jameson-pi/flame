#!/bin/bash
# Setup script for Flame CLI on macOS/Linux

echo ""
echo "======================================"
echo "🔥 Flame CLI Setup Script"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python found:"
python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

# Setup .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created - Please edit it with your API key"
else
    echo "✅ .env already exists"
fi

# Test setup
echo ""
echo "Testing setup..."
python main.py --version
if [ $? -ne 0 ]; then
    echo "❌ Setup test failed"
    exit 1
fi
echo "✅ Setup test passed"

# Final instructions
echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your HACK_CLUB_API_KEY"
echo "2. Run: python main.py --check"
echo "3. Run: python main.py"
echo ""
echo "For more help, see README.md or QUICKSTART.md"
echo ""

