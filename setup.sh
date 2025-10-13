#!/bin/bash
# Setup script for Gestify on M1 MacBook Pro

echo "╔═══════════════════════════════════════╗"
echo "║    Gestify Setup for M1 MacBook       ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.9 or later."
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "✅ Virtual environment created"
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully"

# Check if Ollama is installed
echo ""
echo "🔍 Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
        
        # Check if qwen2.5-vl model is available
        if ollama list | grep -q "qwen2.5-vl"; then
            echo "✅ Qwen 2.5 VL model found"
        else
            echo "⚠️  Qwen 2.5 VL model not found"
            echo ""
            read -p "Would you like to download it now? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "📥 Downloading Qwen 2.5 VL 7B (this may take a while)..."
                ollama pull qwen2.5-vl:7b
            else
                echo "ℹ️  You can download it later with: ollama pull qwen2.5-vl:7b"
            fi
        fi
    else
        echo "⚠️  Ollama is not running"
        echo "ℹ️  Start it with: ollama serve"
        echo "ℹ️  Then pull model with: ollama pull qwen2.5-vl:7b"
    fi
else
    echo "⚠️  Ollama not found"
    echo "ℹ️  Install with: brew install ollama"
    echo "ℹ️  Or visit: https://ollama.ai"
    echo ""
    echo "Note: Ollama is optional - Gestify works with MediaPipe only"
fi

echo ""
echo "═══════════════════════════════════════"
echo "✅ Setup Complete!"
echo "═══════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Grant Accessibility Permissions:"
echo "   System Preferences → Security & Privacy → Privacy → Accessibility"
echo "   Add Terminal (or your Python IDE) and enable it"
echo ""
echo "2. Run Gestify:"
echo "   source venv/bin/activate"
echo "   python gestify.py"
echo ""
echo "3. Controls:"
echo "   Q - Quit"
echo "   A - Toggle AI assist (if Ollama installed)"
echo ""
echo "📖 For more info, see README.md"
echo ""

