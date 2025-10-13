#!/usr/bin/env python3
"""
Test script to verify Gestify setup
"""

import sys

def test_imports():
    """Test if all required packages are installed"""
    print("🧪 Testing imports...")
    
    try:
        import cv2
        print("  ✅ OpenCV")
    except ImportError as e:
        print(f"  ❌ OpenCV: {e}")
        return False
    
    try:
        import mediapipe
        print("  ✅ MediaPipe")
    except ImportError as e:
        print(f"  ❌ MediaPipe: {e}")
        return False
    
    try:
        import numpy
        print("  ✅ NumPy")
    except ImportError as e:
        print(f"  ❌ NumPy: {e}")
        return False
    
    try:
        import pyautogui
        print("  ✅ PyAutoGUI")
    except ImportError as e:
        print(f"  ❌ PyAutoGUI: {e}")
        return False
    
    try:
        import requests
        print("  ✅ Requests")
    except ImportError as e:
        print(f"  ❌ Requests: {e}")
        return False
    
    return True


def test_camera():
    """Test camera availability"""
    print("\n📹 Testing camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("  ❌ Camera not accessible")
            print("     Make sure:")
            print("     - No other app is using the camera")
            print("     - Camera permissions are granted")
            return False
        
        # Try to read a frame
        ret, frame = cap.read()
        if not ret:
            print("  ❌ Cannot read from camera")
            cap.release()
            return False
        
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"  ✅ Camera: {int(width)}x{int(height)} @ {int(fps)}fps")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"  ❌ Camera test failed: {e}")
        return False


def test_mediapipe():
    """Test MediaPipe hand detection"""
    print("\n🖐️  Testing MediaPipe...")
    
    try:
        import mediapipe as mp
        
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        
        print("  ✅ MediaPipe Hands initialized")
        hands.close()
        return True
        
    except Exception as e:
        print(f"  ❌ MediaPipe test failed: {e}")
        return False


def test_pyautogui():
    """Test PyAutoGUI"""
    print("\n🖱️  Testing PyAutoGUI...")
    
    try:
        import pyautogui
        
        # Get screen size
        width, height = pyautogui.size()
        print(f"  ✅ Screen: {width}x{height}")
        
        # Test cursor position (doesn't move cursor)
        x, y = pyautogui.position()
        print(f"  ✅ Current cursor: ({x}, {y})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ PyAutoGUI test failed: {e}")
        print("     Note: You need Accessibility permissions for full functionality")
        print("     System Preferences → Security & Privacy → Privacy → Accessibility")
        return False


def test_ollama():
    """Test Ollama connection (optional)"""
    print("\n🤖 Testing Ollama (optional)...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            print(f"  ✅ Ollama running")
            
            if any("qwen2.5-vl" in name for name in model_names):
                print("  ✅ Qwen 2.5 VL model available")
            else:
                print("  ⚠️  Qwen 2.5 VL model not found")
                print("     Install with: ollama pull qwen2.5-vl:7b")
            
            return True
        else:
            print("  ⚠️  Ollama not responding")
            return False
            
    except Exception:
        print("  ⚠️  Ollama not running")
        print("     This is optional - Gestify works without it")
        print("     To enable: ollama serve")
        return False


def main():
    """Run all tests"""
    print("""
╔═══════════════════════════════════════╗
║      Gestify Setup Test               ║
╚═══════════════════════════════════════╝
""")
    
    results = {
        "imports": test_imports(),
        "camera": test_camera(),
        "mediapipe": test_mediapipe(),
        "pyautogui": test_pyautogui(),
        "ollama": test_ollama()
    }
    
    print("\n" + "="*40)
    print("📊 Test Results:")
    print("="*40)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        required = "(optional)" if test_name == "ollama" else "(required)"
        print(f"{status} - {test_name.capitalize()} {required}")
    
    required_tests = ["imports", "camera", "mediapipe", "pyautogui"]
    all_required_passed = all(results[test] for test in required_tests)
    
    print("="*40)
    
    if all_required_passed:
        print("✅ All required tests passed!")
        print("\n🚀 You're ready to run Gestify:")
        print("   python gestify.py")
    else:
        print("❌ Some required tests failed")
        print("\n📋 Next steps:")
        print("   1. Check error messages above")
        print("   2. Install missing packages: pip install -r requirements.txt")
        print("   3. Grant camera permissions if needed")
        print("   4. Run this test again")
    
    print()
    return 0 if all_required_passed else 1


if __name__ == "__main__":
    sys.exit(main())

