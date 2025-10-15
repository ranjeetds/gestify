#!/usr/bin/env python3
"""
Test script to verify Gestify v2.0 environment setup
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    required_packages = [
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'),
        ('numpy', 'numpy'),
        ('pyautogui', 'pyautogui'),
    ]
    
    failed = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError as e:
            print(f"   ❌ {package_name}: {e}")
            failed.append(package_name)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def test_gestify_library():
    """Test if Gestify library can be imported"""
    print("\n🔍 Testing Gestify library...")
    try:
        from gestify_lib import (
            GestifyController,
            GestifyConfig,
            HandDetector,
            FaceDetector,
            GestureRecognizer
        )
        print("   ✅ GestifyController")
        print("   ✅ GestifyConfig")
        print("   ✅ HandDetector")
        print("   ✅ FaceDetector")
        print("   ✅ GestureRecognizer")
        return True
    except ImportError as e:
        print(f"   ❌ Gestify library: {e}")
        print("   Run: pip install -e .")
        return False

def test_camera():
    """Test if camera is accessible"""
    print("\n🔍 Testing camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("   ⚠️  Camera not accessible")
            print("      This might be okay - check if other apps are using it")
            return True  # Don't fail setup
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"   ✅ Camera working ({frame.shape[1]}x{frame.shape[0]})")
            return True
        else:
            print("   ⚠️  Camera opened but couldn't read frame")
            return True  # Don't fail setup
    except Exception as e:
        print(f"   ⚠️  Camera test error: {e}")
        return True  # Don't fail setup

def test_mediapipe():
    """Test MediaPipe hand and face detection"""
    print("\n🔍 Testing MediaPipe models...")
    try:
        import mediapipe as mp
        
        # Test hands
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        hands.close()
        print("   ✅ MediaPipe Hands")
        
        # Test face mesh
        mp_face = mp.solutions.face_mesh
        face = mp_face.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        face.close()
        print("   ✅ MediaPipe Face Mesh")
        
        return True
    except Exception as e:
        print(f"   ❌ MediaPipe error: {e}")
        return False

def test_system_control():
    """Test PyAutoGUI for system control"""
    print("\n🔍 Testing system control...")
    try:
        import pyautogui
        
        # Get screen size
        width, height = pyautogui.size()
        print(f"   ✅ Screen size: {width}x{height}")
        
        # Test failsafe
        pyautogui.FAILSAFE = True
        print("   ✅ Failsafe enabled")
        
        return True
    except Exception as e:
        print(f"   ❌ System control error: {e}")
        return False

def test_config_modes():
    """Test configuration modes"""
    print("\n🔍 Testing configuration modes...")
    try:
        from gestify_lib import GestifyConfig
        
        # Test default
        config = GestifyConfig()
        print("   ✅ Default config")
        
        # Test fast mode
        fast = GestifyConfig.fast_mode()
        print("   ✅ Fast mode")
        
        # Test accurate mode
        accurate = GestifyConfig.accurate_mode()
        print("   ✅ Accurate mode")
        
        # Test two-hand mode
        two_hand = GestifyConfig.two_hand_mode()
        print("   ✅ Two-hand mode")
        
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False

def main():
    """Run all tests"""
    print("╔" + "═" * 48 + "╗")
    print("║  🧪 Gestify v2.0 Environment Test             ║")
    print("╚" + "═" * 48 + "╝\n")
    
    results = []
    results.append(("Core Imports", test_imports()))
    results.append(("Gestify Library", test_gestify_library()))
    results.append(("MediaPipe Models", test_mediapipe()))
    results.append(("Camera Access", test_camera()))
    results.append(("System Control", test_system_control()))
    results.append(("Config Modes", test_config_modes()))
    
    print("\n╔" + "═" * 48 + "╗")
    print("║  📊 Test Results                               ║")
    print("╚" + "═" * 48 + "╝")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name:.<30} {status}")
    
    all_critical_passed = all(result for name, result in results 
                              if name not in ["Camera Access"])
    
    print()
    if all_critical_passed:
        print("✅ All critical tests passed! You're ready to use Gestify.")
        print("\n💡 Quick start:")
        print("   gestify              # Run with default settings")
        print("   gestify --help       # Show all options")
        return 0
    else:
        print("❌ Some critical tests failed. Check the errors above.")
        print("   Try running: pip install -r requirements.txt")
        print("   Then: pip install -e .")
        return 1

if __name__ == '__main__':
    sys.exit(main())
