#!/usr/bin/env python3
"""
Gestify - Hand Gesture Control for macOS
Using MediaPipe for hand detection and Ollama Qwen 2.5 VL for gesture recognition
Optimized for M1 MacBook Pro
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import requests
import json
import sys
from collections import deque
from typing import Optional, Tuple, List, Dict
import base64
from io import BytesIO
from PIL import Image

# Configure PyAutoGUI for macOS
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01  # Minimal pause for M1 performance


class GestureController:
    """Main controller for gesture recognition and system control"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """Initialize the gesture controller
        
        Args:
            ollama_host: Ollama API endpoint
        """
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=0  # Lightweight model for M1
        )
        
        # Camera setup with proper error handling
        self.cap = None
        try:
            # Try default camera
            self.cap = cv2.VideoCapture(0)
            
            # Give camera time to initialize
            time.sleep(0.5)
            
            if not self.cap.isOpened():
                print("⚠️  Default camera not available, trying camera index 1...")
                self.cap.release()
                self.cap = cv2.VideoCapture(1)
                time.sleep(0.5)
            
            if not self.cap.isOpened():
                raise Exception("No camera found")
            
            # Configure camera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Verify we can read frames
            ret, _ = self.cap.read()
            if not ret:
                raise Exception("Cannot read from camera")
                
        except Exception as e:
            print(f"❌ Camera error: {e}")
            print("   Make sure:")
            print("   1. No other app is using the camera (Zoom, FaceTime, etc.)")
            print("   2. Camera permissions are granted")
            print("   3. Camera is properly connected")
            if self.cap:
                self.cap.release()
            self.cap = None
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Smoothing buffers
        self.cursor_history = deque(maxlen=5)
        self.gesture_history = deque(maxlen=10)
        
        # State tracking
        self.current_gesture = "None"
        self.last_action_time = 0
        self.action_cooldown = 0.3  # 300ms between actions
        self.is_dragging = False
        
        # Gesture thresholds (optimized for natural hand movements)
        self.pinch_threshold = 0.05
        self.swipe_threshold = 0.15
        self.confidence_threshold = 0.6
        
        # Ollama configuration
        self.ollama_host = ollama_host
        self.model = "llama3.2-vision:latest"  # Using Meta's Llama 3.2 Vision
        self.use_ai_assist = False  # Disable by default for performance
        self.last_ai_query = 0
        self.ai_cooldown = 2.0  # Only query AI every 2 seconds
        
        # FPS tracking
        self.fps_history = deque(maxlen=30)
        self.last_fps_time = time.time()
        
        print("✅ Gestify initialized")
        if self.cap and self.cap.isOpened():
            print(f"📹 Camera: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ {int(self.cap.get(cv2.CAP_PROP_FPS))}fps")
        else:
            print("📹 Camera: Not available")
        print(f"🖥️  Screen: {self.screen_width}x{self.screen_height}")
        self.check_ollama_connection()
    
    def check_ollama_connection(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check for exact match or similar vision models
                has_model = any(self.model in name for name in model_names)
                
                # Find available vision models
                vision_models = [name for name in model_names if "vision" in name.lower() or "llava" in name.lower()]
                
                if has_model:
                    print(f"✅ Ollama connected - {self.model} available")
                    print("💡 Press 'A' to toggle AI-assisted gesture recognition")
                elif vision_models:
                    # Use first available vision model
                    self.model = vision_models[0]
                    print(f"✅ Ollama connected - Using {self.model}")
                    print("💡 Press 'A' to toggle AI-assisted gesture recognition")
                else:
                    print(f"⚠️  Ollama connected but no vision models found")
                    print(f"   Available models: {', '.join(model_names[:3])}")
                    print(f"   Install a vision model: ollama pull llava:13b")
                    print("   (AI-assisted gestures disabled, using MediaPipe only)")
            else:
                print("⚠️  Ollama not responding")
        except requests.exceptions.RequestException:
            print("⚠️  Ollama not running. Start with: ollama serve")
            print("   (AI-assisted gestures disabled, using MediaPipe only)")
    
    def query_ollama_gesture(self, frame: np.ndarray, landmarks: Dict) -> Optional[str]:
        """Query Ollama to identify gesture from frame (optional, for complex gestures)
        
        Args:
            frame: Current video frame
            landmarks: Hand landmarks data
            
        Returns:
            Gesture name or None
        """
        current_time = time.time()
        if current_time - self.last_ai_query < self.ai_cooldown:
            return None
        
        try:
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Query Ollama
            prompt = """Identify the hand gesture in this image. Choose only one from:
- pointing (index finger extended)
- fist (all fingers closed)
- palm (all fingers open)
- peace (index and middle fingers extended)
- thumbs_up
- thumbs_down
- pinch (thumb and index touching)

Respond with ONLY the gesture name, nothing else."""

            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=1.5
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().lower()
                self.last_ai_query = current_time
                return result
        except Exception as e:
            print(f"AI query error: {e}")
        
        return None
    
    def calculate_distance(self, point1: Tuple, point2: Tuple) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def is_finger_extended(self, landmarks, finger_tip_idx: int, finger_pip_idx: int) -> bool:
        """Check if a finger is extended
        
        Args:
            landmarks: Hand landmarks
            finger_tip_idx: Index of finger tip
            finger_pip_idx: Index of finger PIP joint
            
        Returns:
            True if finger is extended
        """
        wrist = landmarks[0]
        tip = landmarks[finger_tip_idx]
        pip = landmarks[finger_pip_idx]
        
        tip_to_wrist = self.calculate_distance((tip.x, tip.y), (wrist.x, wrist.y))
        pip_to_wrist = self.calculate_distance((pip.x, pip.y), (wrist.x, wrist.y))
        
        return tip_to_wrist > pip_to_wrist * 1.1
    
    def detect_gesture(self, landmarks) -> str:
        """Detect gesture from hand landmarks using MediaPipe
        
        Args:
            landmarks: Hand landmarks from MediaPipe
            
        Returns:
            Gesture name
        """
        # Extract key points
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Check finger extensions
        index_extended = self.is_finger_extended(landmarks, 8, 6)
        middle_extended = self.is_finger_extended(landmarks, 12, 10)
        ring_extended = self.is_finger_extended(landmarks, 16, 14)
        pinky_extended = self.is_finger_extended(landmarks, 20, 18)
        
        # Pinch detection (thumb + index close)
        pinch_distance = self.calculate_distance(
            (thumb_tip.x, thumb_tip.y),
            (index_tip.x, index_tip.y)
        )
        
        if pinch_distance < self.pinch_threshold:
            return "pinch"
        
        # Fist (all fingers closed)
        if not any([index_extended, middle_extended, ring_extended, pinky_extended]):
            return "fist"
        
        # Open palm (all fingers extended)
        if all([index_extended, middle_extended, ring_extended, pinky_extended]):
            return "palm"
        
        # Pointing (only index extended)
        if index_extended and not middle_extended and not ring_extended:
            return "pointing"
        
        # Peace / Two fingers
        if index_extended and middle_extended and not ring_extended and not pinky_extended:
            return "peace"
        
        # Thumbs up/down
        thumb_tip_y = thumb_tip.y
        wrist_y = landmarks[0].y
        
        if not index_extended and not middle_extended:
            if thumb_tip_y < wrist_y - 0.1:
                return "thumbs_up"
            elif thumb_tip_y > wrist_y + 0.1:
                return "thumbs_down"
        
        return "unknown"
    
    def execute_gesture_action(self, gesture: str, landmarks):
        """Execute system action based on detected gesture
        
        Args:
            gesture: Detected gesture name
            landmarks: Hand landmarks for position tracking
        """
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_action_time < self.action_cooldown:
            return
        
        # Get index finger position for cursor control
        index_tip = landmarks[8]
        cursor_x = int(index_tip.x * self.screen_width)
        cursor_y = int(index_tip.y * self.screen_height)
        
        # Smooth cursor movement
        self.cursor_history.append((cursor_x, cursor_y))
        if len(self.cursor_history) >= 3:
            smooth_x = int(np.mean([p[0] for p in self.cursor_history]))
            smooth_y = int(np.mean([p[1] for p in self.cursor_history]))
        else:
            smooth_x, smooth_y = cursor_x, cursor_y
        
        # Execute actions based on gesture
        if gesture == "pointing":
            # Move cursor with index finger
            pyautogui.moveTo(smooth_x, smooth_y, duration=0)
            
        elif gesture == "pinch":
            # Left click
            if not self.is_dragging:
                pyautogui.click()
                self.last_action_time = current_time
                print("🖱️  Click")
            
        elif gesture == "fist":
            # Start/continue drag
            if not self.is_dragging:
                pyautogui.mouseDown()
                self.is_dragging = True
                print("🖱️  Drag started")
            else:
                pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                
        elif gesture == "palm":
            # Release drag or trigger spacebar
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False
                print("🖱️  Drag released")
            else:
                pyautogui.press('space')
                self.last_action_time = current_time
                print("⌨️  Space")
                
        elif gesture == "peace":
            # Scroll gesture - use hand height
            wrist = landmarks[0]
            middle_tip = landmarks[12]
            vertical_movement = middle_tip.y - wrist.y
            
            if abs(vertical_movement) > 0.1:
                scroll_amount = int(vertical_movement * 200)
                pyautogui.scroll(scroll_amount)
                self.last_action_time = current_time
                
        elif gesture == "thumbs_up":
            # Enter key
            pyautogui.press('enter')
            self.last_action_time = current_time
            print("⌨️  Enter")
            
        elif gesture == "thumbs_down":
            # Escape key
            pyautogui.press('escape')
            self.last_action_time = current_time
            print("⌨️  Escape")
    
    def draw_ui(self, frame: np.ndarray, hand_landmarks, fps: float):
        """Draw UI overlay on frame
        
        Args:
            frame: Video frame
            hand_landmarks: Detected hand landmarks
            fps: Current FPS
        """
        height, width, _ = frame.shape
        
        # Draw hand landmarks
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Status overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 150), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Text info
        cv2.putText(frame, "Gestify - Hand Control", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Gesture: {self.current_gesture}", (20, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        status = "Dragging" if self.is_dragging else "Ready"
        cv2.putText(frame, f"Status: {status}", (20, 115),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        ai_status = "ON" if self.use_ai_assist else "OFF"
        ai_color = (0, 255, 0) if self.use_ai_assist else (128, 128, 128)
        cv2.putText(frame, f"AI: {ai_status}", (20, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, ai_color, 1)
        
        # Controls hint
        cv2.putText(frame, "Q: Quit | A: Toggle AI", (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Gesture guide
        guide_x = width - 250
        cv2.rectangle(frame, (guide_x - 10, 10), (width - 10, 280), (0, 0, 0), -1)
        cv2.putText(frame, "Gesture Guide:", (guide_x, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        gestures = [
            ("☝️  Point", "Move cursor"),
            ("🤏 Pinch", "Click"),
            ("✊ Fist", "Drag"),
            ("🖐 Palm", "Release/Space"),
            ("✌️  Peace", "Scroll"),
            ("👍 Thumbs Up", "Enter"),
            ("👎 Thumbs Down", "Escape")
        ]
        
        for i, (emoji, desc) in enumerate(gestures):
            y = 55 + i * 30
            cv2.putText(frame, emoji, (guide_x, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            cv2.putText(frame, desc, (guide_x + 60, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Main loop for gesture control"""
        
        # Check if camera was initialized
        if self.cap is None or not self.cap.isOpened():
            print("❌ Cannot start - camera not available")
            print("\n📋 Troubleshooting steps:")
            print("1. Close other apps using camera (Zoom, FaceTime, Photo Booth)")
            print("2. Grant camera permissions to Terminal:")
            print("   System Preferences → Security & Privacy → Privacy → Camera")
            print("3. Try running: tccutil reset Camera")
            print("4. Restart Terminal and try again")
            return
        
        print("\n🚀 Starting Gestify...")
        print("👋 Show your hand to the camera")
        print("Press 'Q' to quit, 'A' to toggle AI assist\n")
        
        frame_count = 0
        
        try:
            while True:
                # Capture frame
                success, frame = self.cap.read()
                if not success:
                    print("❌ Failed to capture frame")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process hand detection
                results = self.hands.process(rgb_frame)
                
                hand_landmarks = None
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    landmarks = hand_landmarks.landmark
                    
                    # Detect gesture with MediaPipe
                    gesture = self.detect_gesture(landmarks)
                    
                    # Optionally enhance with AI (if enabled and not too frequent)
                    if self.use_ai_assist and frame_count % 30 == 0:  # Every 30 frames
                        ai_gesture = self.query_ollama_gesture(frame, landmarks)
                        if ai_gesture and ai_gesture in ["pointing", "fist", "palm", "peace", 
                                                         "thumbs_up", "thumbs_down", "pinch"]:
                            gesture = ai_gesture
                    
                    self.current_gesture = gesture
                    self.gesture_history.append(gesture)
                    
                    # Execute action
                    self.execute_gesture_action(gesture, landmarks)
                else:
                    self.current_gesture = "None"
                    # Release drag if hand lost
                    if self.is_dragging:
                        pyautogui.mouseUp()
                        self.is_dragging = False
                
                # Calculate FPS
                current_time = time.time()
                fps_delta = current_time - self.last_fps_time
                if fps_delta > 0:
                    fps = 1.0 / fps_delta
                    self.fps_history.append(fps)
                self.last_fps_time = current_time
                avg_fps = np.mean(self.fps_history) if self.fps_history else 0
                
                # Draw UI
                frame = self.draw_ui(frame, hand_landmarks, avg_fps)
                
                # Display frame
                cv2.imshow('Gestify - Hand Control', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n👋 Quitting...")
                    break
                elif key == ord('a') or key == ord('A'):
                    self.use_ai_assist = not self.use_ai_assist
                    status = "enabled" if self.use_ai_assist else "disabled"
                    print(f"🤖 AI assist {status}")
                
                frame_count += 1
                
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        if self.is_dragging:
            pyautogui.mouseUp()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("✅ Cleanup complete")


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════╗
║         Gestify - Hand Control         ║
║   Powered by MediaPipe + Ollama       ║
║      Optimized for M1 MacBook         ║
╚═══════════════════════════════════════╝
    """)
    
    try:
        controller = GestureController()
        controller.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

