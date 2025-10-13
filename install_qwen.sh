#!/bin/bash
# Install Qwen 2.5 VL support for Enhanced Gestify

echo "╔═══════════════════════════════════════╗"
echo "║  Install Qwen 2.5 VL for Gestify      ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Activating venv..."
    source venv/bin/activate
fi

echo "📦 Installing Qwen 2.5 VL dependencies..."
echo "   This will download ~4-5GB of models on first run"
echo ""

# Install dependencies
echo "1️⃣  Installing PyTorch for Apple Silicon..."
pip install torch torchvision torchaudio

echo ""
echo "2️⃣  Installing Transformers..."
pip install transformers>=4.44.0

echo ""
echo "3️⃣  Installing Accelerate..."
pip install accelerate

echo ""
echo "4️⃣  Installing Qwen VL utils..."
pip install qwen-vl-utils

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "═══════════════════════════════════════"
echo "📥 Model Download (First Run Only)"
echo "═══════════════════════════════════════"
echo ""
echo "The Qwen 2.5 VL 2B model will be downloaded automatically"
echo "on first use. This is ~4-5GB and may take 10-15 minutes."
echo ""
echo "Model: Qwen/Qwen2-VL-2B-Instruct"
echo "Size: ~4.5GB"
echo "Location: ~/.cache/huggingface/hub/"
echo ""

read -p "Would you like to pre-download the model now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Downloading Qwen 2.5 VL 2B model..."
    python3 << 'EOF'
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import torch

print("Downloading Qwen2-VL-2B-Instruct...")
print("This may take 10-15 minutes depending on your internet speed...")

try:
    model_name = "Qwen/Qwen2-VL-2B-Instruct"
    processor = AutoProcessor.from_pretrained(model_name)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    print("\n✅ Model downloaded successfully!")
    print(f"   Cached at: ~/.cache/huggingface/hub/")
except Exception as e:
    print(f"\n❌ Error downloading model: {e}")
    print("   You can try again later or download will happen on first run")
EOF
else
    echo "⏭️  Skipping pre-download"
    echo "   Model will download automatically when you run with --qwen flag"
fi

echo ""
echo "═══════════════════════════════════════"
echo "✅ Installation Complete!"
echo "═══════════════════════════════════════"
echo ""
echo "📝 Usage:"
echo "   Basic (MediaPipe only):"
echo "     python gestify_enhanced.py"
echo ""
echo "   With Ollama AI (if available):"
echo "     python gestify_enhanced.py --ai"
echo ""
echo "   With Qwen 2.5 VL (Hugging Face):"
echo "     python gestify_enhanced.py --qwen --ai"
echo ""
echo "   Toggle AI during runtime with 'A' key"
echo "   Switch to Qwen during runtime with 'H' key"
echo ""
echo "💡 Tips:"
echo "   - First run with --qwen will be slow (model loading)"
echo "   - Subsequent runs are faster (model cached)"
echo "   - Qwen provides best AI gesture recognition"
echo "   - M1 Pro: Expect 20-30 FPS with Qwen"
echo ""

