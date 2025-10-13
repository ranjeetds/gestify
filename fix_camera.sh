#!/bin/bash
# Fix camera access issues for Gestify

echo "╔═══════════════════════════════════════╗"
echo "║    Gestify Camera Troubleshooter      ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if any apps are using camera
echo "🔍 Checking for apps using camera..."
lsof 2>/dev/null | grep -i "VDC\|camera\|AppleCamera" | head -5

if [ $? -eq 0 ]; then
    echo ""
    echo "⚠️  Found apps using camera. Please close them:"
    echo "   - Zoom"
    echo "   - FaceTime"
    echo "   - Photo Booth"
    echo "   - Teams"
    echo "   - Any other video apps"
    echo ""
else
    echo "✅ No other apps using camera"
    echo ""
fi

# Check camera permissions
echo "🔐 Checking camera permissions..."
echo ""
echo "To grant camera access to Terminal:"
echo "1. Open System Preferences"
echo "2. Go to Security & Privacy → Privacy → Camera"
echo "3. Look for Terminal in the list"
echo "4. If present, ensure checkbox is ✅ enabled"
echo "5. If not present, it will be added when you run Gestify"
echo ""

# Offer to reset camera permissions
read -p "Would you like to reset camera permissions? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Resetting camera permissions..."
    tccutil reset Camera
    echo "✅ Camera permissions reset"
    echo "   Gestify will request permission again when you run it"
    echo ""
fi

# Test camera availability
echo "📹 Testing camera..."
python3 << 'EOF'
import cv2
import sys

try:
    # Try camera 0
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ Camera 0 working!")
            print(f"   Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        else:
            print("⚠️  Camera 0 opens but cannot read frames")
        cap.release()
    else:
        print("❌ Camera 0 not available")
        
        # Try camera 1
        print("   Trying camera 1...")
        cap = cv2.VideoCapture(1)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("   ✅ Camera 1 working!")
                print("   Note: Update gestify.py to use VideoCapture(1)")
            else:
                print("   ⚠️  Camera 1 opens but cannot read frames")
            cap.release()
        else:
            print("   ❌ Camera 1 not available either")
            print("")
            print("   Possible issues:")
            print("   - Camera is being used by another app")
            print("   - Camera permissions not granted")
            print("   - Camera is disabled or not connected")
            
except ImportError:
    print("❌ OpenCV not installed")
    print("   Run: pip install opencv-python")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error testing camera: {e}")
    sys.exit(1)
EOF

echo ""
echo "═══════════════════════════════════════"
echo "✅ Troubleshooting complete!"
echo "═══════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Close all apps using camera"
echo "2. Grant camera permissions to Terminal if needed"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python gestify.py"
echo ""

