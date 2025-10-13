#!/usr/bin/env python3
"""
Gestify Enhanced - Advanced Hand Gesture Control for macOS
With Qwen 2.5 VL support via Hugging Face Transformers
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
import os
from collections import deque
from typing import Optional, Tuple, List, Dict
import base64
from io import BytesIO
from PIL import Image

# Configure PyAutoGUI for macOS
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


class EnhancedGestureController:
    """Enhanced controller with more gestures and Qwen 2.5 VL support"""
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize the enhanced gesture controller
        
        Args:
            use_huggingface: Use Hugging Face Qwen instead of Ollama
        """
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=0
        )
        
        # Camera setup with error handling
        self.cap = None
        try:
            self.cap = cv2.VideoCapture(0)
            time.sleep(0.5)
            
            if not self.cap.isOpened():
                print("⚠️  Trying camera index 1...")
                self.cap.release()
                self.cap = cv2.VideoCapture(1)
                time.sleep(0.5)
            
            if not self.cap.isOpened():
                raise Exception("No camera found")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            ret, _ = self.cap.read()
            if not ret:
                raise Exception("Cannot read from camera")
                
        except Exception as e:
            print(f"❌ Camera error: {e}")
            if self.cap:
                self.cap.release()
            self.cap = None
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Enhanced smoothing buffers
        self.cursor_history = deque(maxlen=5)
        self.gesture_history = deque(maxlen=15)
        self.landmark_history = deque(maxlen=5)
        
        # State tracking for all gestures
        self.current_gesture = "None"
        self.last_action_time = 0
        self.action_cooldown = 0.2
        self.is_dragging = False
        
        # Pinch zoom state
        self.last_pinch_distance = 0
        self.pinch_gesture_start = 0
        
        # Swipe detection
        self.swipe_start_x = 0
        self.swipe_start_time = 0
        
        # Wave detection (for back/forward)
        self.wave_history = deque(maxlen=10)
        self.wave_direction_changes = 0
        self.last_wave_time = 0
        
        # Two-finger twist detection
        self.last_rotation_angle = 0
        self.rotation_history = deque(maxlen=5)
        
        # Click detection
        self.click_count = 0
        self.last_click_time = 0
        
        # Thresholds
        self.pinch_threshold = 0.04
        self.swipe_threshold = 150  # pixels
        self.wave_threshold = 40  # pixels oscillation
        self.rotation_threshold = 15  # degrees
        
        # AI Model setup
        self.use_huggingface = use_huggingface
        self.use_ai_assist = False
        self.last_ai_query = 0
        self.ai_cooldown = 3.0
        
        # Hugging Face model (lazy load)
        self.hf_model = None
        self.hf_processor = None
        
        # Ollama config
        self.ollama_host = "http://localhost:11434"
        self.ollama_model = "llama3.2-vision:latest"
        
        # FPS tracking
        self.fps_history = deque(maxlen=30)
        self.last_fps_time = time.time()
        
        print("✅ Enhanced Gestify initialized")
        if self.cap and self.cap.isOpened():
            print(f"📹 Camera: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        else:
            print("📹 Camera: Not available")
        print(f"🖥️  Screen: {self.screen_width}x{self.screen_height}")
        
        if use_huggingface:
            print("🤖 AI Mode: Hugging Face Transformers (Qwen 2.5 VL)")
            print("   Model will load on first AI query")
        else:
            self.check_ollama_connection()
    
    def load_huggingface_model(self):
        """Lazy load Hugging Face Qwen model"""
        if self.hf_model is not None:
            return True
        
        try:
            print("📥 Loading Qwen 2.5 VL from Hugging Face...")
            print("   This may take a few minutes on first run...")
            
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            
            # Use smaller model for M1 performance
            model_name = "Qwen/Qwen2-VL-2B-Instruct"  # 2B for speed
            
            print(f"   Loading {model_name}...")
            self.hf_processor = AutoProcessor.from_pretrained(model_name)
            self.hf_model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            
            print("✅ Qwen 2.5 VL loaded successfully!")
            return True
            
        except ImportError:
            print("❌ Hugging Face Transformers not installed")
            print("   Install with: pip install transformers torch accelerate")
            return False
        except Exception as e:
            print(f"❌ Failed to load Qwen model: {e}")
            print("   Falling back to MediaPipe only")
            return False
    
    def check_ollama_connection(self):
        """Check Ollama connection"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                vision_models = [n for n in model_names if "vision" in n.lower() or "llava" in n.lower()]
                
                if vision_models:
                    self.ollama_model = vision_models[0]
                    print(f"✅ Ollama connected - {self.ollama_model}")
                    print("💡 Press 'A' to toggle AI assistance")
                    print("💡 Press 'H' to switch to Hugging Face Qwen")
                else:
                    print("⚠️  Ollama running but no vision models found")
        except:
            print("⚠️  Ollama not running (optional)")
    
    def query_ai_gesture(self, frame: np.ndarray) -> Optional[str]:
        """Query AI model for gesture recognition"""
        current_time = time.time()
        if current_time - self.last_ai_query < self.ai_cooldown:
            return None
        
        try:
            if self.use_huggingface:
                return self.query_huggingface(frame)
            else:
                return self.query_ollama(frame)
        except Exception as e:
            print(f"AI query error: {e}")
            return None
    
    def query_huggingface(self, frame: np.ndarray) -> Optional[str]:
        """Query Hugging Face Qwen model"""
        if not self.load_huggingface_model():
            return None
        
        try:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            prompt = """Identify the hand gesture in this image. Choose ONLY ONE from this list:
- pointing (index finger extended, others closed)
- fist (all fingers closed)
- palm (all fingers open)
- peace (index and middle extended, V sign)
- thumbs_up (thumb up, others closed)
- thumbs_down (thumb down, others closed)
- pinch (thumb and index touching)
- wave (hand moving side to side)
- ok_sign (thumb and index forming circle)

Respond with ONLY the gesture name, nothing else."""

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": pil_image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            text = self.hf_processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            inputs = self.hf_processor(
                text=[text],
                images=[pil_image],
                padding=True,
                return_tensors="pt"
            )
            
            # Generate
            output_ids = self.hf_model.generate(**inputs, max_new_tokens=20)
            generated_text = self.hf_processor.batch_decode(
                output_ids, skip_special_tokens=True
            )[0]
            
            # Extract gesture name
            result = generated_text.split("assistant")[-1].strip().lower()
            self.last_ai_query = time.time()
            return result
            
        except Exception as e:
            print(f"Hugging Face query error: {e}")
            return None
    
    def query_ollama(self, frame: np.ndarray) -> Optional[str]:
        """Query Ollama for gesture recognition"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            prompt = """Identify the hand gesture. Choose ONE:
pointing, fist, palm, peace, thumbs_up, thumbs_down, pinch, wave, ok_sign
Reply with ONLY the gesture name."""

            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=2.0
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().lower()
                self.last_ai_query = time.time()
                return result
        except Exception as e:
            return None
        
        return None
    
    def calculate_distance(self, p1: Tuple, p2: Tuple) -> float:
        """Calculate Euclidean distance"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def calculate_angle(self, p1: Tuple, p2: Tuple, center: Tuple) -> float:
        """Calculate angle between two points relative to center"""
        angle1 = np.arctan2(p1[1] - center[1], p1[0] - center[0])
        angle2 = np.arctan2(p2[1] - center[1], p2[0] - center[0])
        return np.degrees(angle2 - angle1)
    
    def is_finger_extended(self, landmarks, tip_idx: int, pip_idx: int) -> bool:
        """Check if finger is extended"""
        wrist = landmarks[0]
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        
        tip_dist = self.calculate_distance((tip.x, tip.y), (wrist.x, wrist.y))
        pip_dist = self.calculate_distance((pip.x, pip.y), (wrist.x, wrist.y))
        
        return tip_dist > pip_dist * 1.1
    
    def detect_gesture_enhanced(self, landmarks) -> str:
        """Enhanced gesture detection with all gestures"""
        # Extract key landmarks
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        
        # Check finger extensions
        index_ext = self.is_finger_extended(landmarks, 8, 6)
        middle_ext = self.is_finger_extended(landmarks, 12, 10)
        ring_ext = self.is_finger_extended(landmarks, 16, 14)
        pinky_ext = self.is_finger_extended(landmarks, 20, 18)
        
        # Convert to pixel coordinates for accurate measurements
        index_px = (int(index_tip.x * 640), int(index_tip.y * 480))
        thumb_px = (int(thumb_tip.x * 640), int(thumb_tip.y * 480))
        middle_px = (int(middle_tip.x * 640), int(middle_tip.y * 480))
        wrist_px = (int(wrist.x * 640), int(wrist.y * 480))
        
        # 1. PINCH DETECTION (for zoom and click)
        pinch_dist = self.calculate_distance(thumb_px, index_px)
        
        if pinch_dist < 25:  # Very close = pinch
            if self.last_pinch_distance > 0:
                delta = pinch_dist - self.last_pinch_distance
                
                # Pinch zoom (sustained pinch with movement)
                if abs(delta) > 3 and time.time() - self.pinch_gesture_start < 0.5:
                    self.last_pinch_distance = pinch_dist
                    if delta < 0:
                        return "pinch_in"  # Zoom in
                    else:
                        return "pinch_out"  # Zoom out
                
                # Quick pinch = click
                if time.time() - self.last_click_time < 0.4:
                    self.click_count += 1
                    if self.click_count >= 2:
                        self.click_count = 0
                        return "double_click"
                else:
                    self.click_count = 1
                    self.last_click_time = time.time()
                    return "single_click"
            
            self.last_pinch_distance = pinch_dist
            self.pinch_gesture_start = time.time()
            return "pinch"
        else:
            self.last_pinch_distance = pinch_dist
        
        # 2. FIST DETECTION
        if not any([index_ext, middle_ext, ring_ext, pinky_ext]):
            return "fist"
        
        # 3. OPEN PALM
        if all([index_ext, middle_ext, ring_ext, pinky_ext]):
            return "palm"
        
        # 4. POINTING
        if index_ext and not middle_ext and not ring_ext:
            return "pointing"
        
        # 5. PEACE SIGN / TWO FINGERS
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            # Check for rotation gesture
            angle = self.calculate_angle(index_px, middle_px, wrist_px)
            self.rotation_history.append(angle)
            
            if len(self.rotation_history) >= 5:
                angle_change = abs(self.rotation_history[-1] - self.rotation_history[0])
                if angle_change > self.rotation_threshold:
                    return "rotate"
            
            return "peace"
        
        # 6. THUMBS UP/DOWN
        thumb_y = thumb_tip.y
        wrist_y = wrist.y
        
        if not index_ext and not middle_ext:
            if thumb_y < wrist_y - 0.12:
                return "thumbs_up"
            elif thumb_y > wrist_y + 0.12:
                return "thumbs_down"
        
        # 7. WAVE DETECTION (lateral movement)
        self.wave_history.append(wrist_px[0])
        if len(self.wave_history) >= 10:
            # Detect oscillations
            direction_changes = 0
            for i in range(1, len(self.wave_history) - 1):
                if (self.wave_history[i] > self.wave_history[i-1] and 
                    self.wave_history[i] > self.wave_history[i+1]):
                    direction_changes += 1
                elif (self.wave_history[i] < self.wave_history[i-1] and 
                      self.wave_history[i] < self.wave_history[i+1]):
                    direction_changes += 1
            
            movement_range = max(self.wave_history) - min(self.wave_history)
            
            if direction_changes >= 2 and movement_range > self.wave_threshold:
                return "wave"
        
        # 8. SWIPE DETECTION
        current_time = time.time()
        if self.swipe_start_time == 0 or current_time - self.swipe_start_time > 1.0:
            self.swipe_start_x = wrist_px[0]
            self.swipe_start_time = current_time
        else:
            x_delta = wrist_px[0] - self.swipe_start_x
            if abs(x_delta) > self.swipe_threshold:
                self.swipe_start_time = 0
                if x_delta < 0:
                    return "swipe_left"
                else:
                    return "swipe_right"
        
        # 9. OK SIGN (thumb + index circle)
        thumb_index_dist = self.calculate_distance(thumb_px, index_px)
        if 20 < thumb_index_dist < 35 and middle_ext:
            return "ok_sign"
        
        return "unknown"
    
    def execute_enhanced_action(self, gesture: str, landmarks):
        """Execute actions for all gestures"""
        current_time = time.time()
        
        # Rate limiting (except for continuous gestures)
        continuous_gestures = ["pointing", "fist", "peace", "pinch"]
        if gesture not in continuous_gestures:
            if current_time - self.last_action_time < self.action_cooldown:
                return
        
        # Get cursor position from index finger
        index_tip = landmarks[8]
        cursor_x = int(index_tip.x * self.screen_width)
        cursor_y = int(index_tip.y * self.screen_height)
        
        # Smooth cursor
        self.cursor_history.append((cursor_x, cursor_y))
        if len(self.cursor_history) >= 3:
            smooth_x = int(np.mean([p[0] for p in self.cursor_history]))
            smooth_y = int(np.mean([p[1] for p in self.cursor_history]))
        else:
            smooth_x, smooth_y = cursor_x, cursor_y
        
        # Execute gesture actions
        if gesture == "pointing":
            pyautogui.moveTo(smooth_x, smooth_y, duration=0)
            
        elif gesture == "pinch" or gesture == "single_click":
            pyautogui.click()
            self.last_action_time = current_time
            print("🖱️  Click")
            
        elif gesture == "double_click":
            pyautogui.doubleClick()
            self.last_action_time = current_time
            print("🖱️  Double Click")
            
        elif gesture == "pinch_in":
            pyautogui.hotkey('command', '=')  # Zoom in
            self.last_action_time = current_time
            print("🔍 Zoom In")
            
        elif gesture == "pinch_out":
            pyautogui.hotkey('command', '-')  # Zoom out
            self.last_action_time = current_time
            print("🔍 Zoom Out")
            
        elif gesture == "fist":
            if not self.is_dragging:
                pyautogui.mouseDown()
                self.is_dragging = True
                print("🖱️  Drag started")
            else:
                pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                
        elif gesture == "palm":
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False
                print("🖱️  Drag released")
            else:
                pyautogui.press('space')
                self.last_action_time = current_time
                print("⌨️  Space")
                
        elif gesture == "peace":
            # Scroll with hand height
            wrist = landmarks[0]
            middle = landmarks[12]
            vertical_delta = middle.y - wrist.y
            
            if abs(vertical_delta) > 0.08:
                scroll_amount = int(vertical_delta * 300)
                pyautogui.scroll(scroll_amount)
                
        elif gesture == "rotate":
            # Simulate trackpad rotation
            pyautogui.hotkey('command', 'r')  # Example: rotate in Preview
            self.last_action_time = current_time
            print("🔄 Rotate")
            
        elif gesture == "thumbs_up":
            pyautogui.press('enter')
            self.last_action_time = current_time
            print("⌨️  Enter")
            
        elif gesture == "thumbs_down":
            pyautogui.press('escape')
            self.last_action_time = current_time
            print("⌨️  Escape")
            
        elif gesture == "wave":
            pyautogui.hotkey('command', '[')  # Back navigation
            self.last_action_time = current_time
            self.wave_history.clear()
            print("⬅️  Back")
            
        elif gesture == "swipe_left":
            pyautogui.hotkey('ctrl', 'left')  # Desktop left
            self.last_action_time = current_time
            print("⬅️  Swipe Left")
            
        elif gesture == "swipe_right":
            pyautogui.hotkey('ctrl', 'right')  # Desktop right
            self.last_action_time = current_time
            print("➡️  Swipe Right")
            
        elif gesture == "ok_sign":
            pyautogui.hotkey('command', 'w')  # Close window
            self.last_action_time = current_time
            print("❌ Close Window")
    
    def draw_enhanced_ui(self, frame: np.ndarray, hand_landmarks, fps: float):
        """Draw enhanced UI with all gestures"""
        height, width, _ = frame.shape
        
        # Draw hand landmarks
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Status overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 180), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Status info
        cv2.putText(frame, "Gestify Enhanced - AI Powered", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Gesture: {self.current_gesture}", (20, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        status = "Dragging" if self.is_dragging else "Ready"
        cv2.putText(frame, f"Status: {status}", (20, 115),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        ai_mode = "Qwen(HF)" if self.use_huggingface else "Ollama"
        ai_status = f"{ai_mode}:ON" if self.use_ai_assist else "MediaPipe"
        ai_color = (0, 255, 0) if self.use_ai_assist else (128, 128, 128)
        cv2.putText(frame, f"AI: {ai_status}", (20, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, ai_color, 1)
        
        cv2.putText(frame, f"Gestures: 15+", (20, 165),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Controls
        cv2.putText(frame, "Q:Quit A:AI H:Qwen M:More", (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Gesture guide (compact)
        guide_x = width - 260
        cv2.rectangle(frame, (guide_x - 10, 10), (width - 10, 350), (0, 0, 0), -1)
        cv2.putText(frame, "15+ Gestures:", (guide_x, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        gestures = [
            ("☝️  Point", "Move cursor"),
            ("🤏 Pinch", "Click/Zoom"),
            ("✊ Fist", "Drag"),
            ("🖐 Palm", "Release/Space"),
            ("✌️  Peace", "Scroll/Rotate"),
            ("👍 Up", "Enter"),
            ("👎 Down", "Escape"),
            ("👋 Wave", "Back"),
            ("⬅️  Swipe L", "Desktop Left"),
            ("➡️  Swipe R", "Desktop Right"),
            ("👌 OK", "Close Window"),
            ("🔍 Pinch In", "Zoom In"),
            ("🔍 Pinch Out", "Zoom Out"),
            ("🔄 Twist", "Rotate"),
            ("🖱️  2x Pinch", "Double Click")
        ]
        
        for i, (emoji, desc) in enumerate(gestures):
            y = 55 + i * 19
            cv2.putText(frame, emoji, (guide_x, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
            cv2.putText(frame, desc, (guide_x + 65, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Enhanced main loop"""
        if self.cap is None or not self.cap.isOpened():
            print("❌ Camera not available")
            return
        
        print("\n🚀 Starting Enhanced Gestify...")
        print("👋 Show your hand - 15+ gestures available!")
        print("Press: Q=Quit | A=Toggle AI | H=Use Qwen | M=Show all gestures\n")
        
        frame_count = 0
        
        try:
            while True:
                success, frame = self.cap.read()
                if not success:
                    break
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                results = self.hands.process(rgb_frame)
                
                hand_landmarks = None
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    landmarks = hand_landmarks.landmark
                    
                    # Detect with MediaPipe
                    gesture = self.detect_gesture_enhanced(landmarks)
                    
                    # Optionally enhance with AI
                    if self.use_ai_assist and frame_count % 45 == 0:
                        ai_gesture = self.query_ai_gesture(frame)
                        if ai_gesture:
                            gesture = ai_gesture
                    
                    self.current_gesture = gesture
                    self.gesture_history.append(gesture)
                    
                    # Execute action
                    self.execute_enhanced_action(gesture, landmarks)
                else:
                    self.current_gesture = "None"
                    if self.is_dragging:
                        pyautogui.mouseUp()
                        self.is_dragging = False
                
                # FPS
                current_time = time.time()
                fps_delta = current_time - self.last_fps_time
                if fps_delta > 0:
                    fps = 1.0 / fps_delta
                    self.fps_history.append(fps)
                self.last_fps_time = current_time
                avg_fps = np.mean(self.fps_history) if self.fps_history else 0
                
                # Draw UI
                frame = self.draw_enhanced_ui(frame, hand_landmarks, avg_fps)
                cv2.imshow('Gestify Enhanced - AI Powered', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('a') or key == ord('A'):
                    self.use_ai_assist = not self.use_ai_assist
                    status = "enabled" if self.use_ai_assist else "disabled"
                    print(f"🤖 AI assist {status}")
                elif key == ord('h') or key == ord('H'):
                    self.use_huggingface = True
                    self.use_ai_assist = True
                    print("🤖 Switched to Hugging Face Qwen 2.5 VL")
                elif key == ord('m') or key == ord('M'):
                    self.print_gesture_guide()
                
                frame_count += 1
                
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted")
        finally:
            self.cleanup()
    
    def print_gesture_guide(self):
        """Print complete gesture guide"""
        print("\n" + "="*60)
        print("📋 COMPLETE GESTURE GUIDE (15+ Gestures)")
        print("="*60)
        gestures = [
            ("☝️  Pointing", "Index only", "Move cursor"),
            ("🤏 Pinch", "Thumb+Index", "Click"),
            ("🤏🤏 Double Pinch", "2x quick", "Double click"),
            ("🤏⬆️  Pinch Close", "Fingers closer", "Zoom In (Cmd++)"),
            ("🤏⬇️  Pinch Apart", "Fingers apart", "Zoom Out (Cmd+-)"),
            ("✊ Fist", "All closed", "Start/Continue drag"),
            ("🖐 Open Palm", "All open", "Release drag or Space"),
            ("✌️  Peace/Two Fingers", "Index+Middle", "Scroll (up/down)"),
            ("🔄 Two-Finger Twist", "Rotate hand", "Rotate gesture"),
            ("👍 Thumbs Up", "Thumb up", "Enter key"),
            ("👎 Thumbs Down", "Thumb down", "Escape key"),
            ("👋 Wave", "Side to side", "Back (Cmd+[)"),
            ("⬅️  Swipe Left", "Fast left", "Desktop/Tab Left"),
            ("➡️  Swipe Right", "Fast right", "Desktop/Tab Right"),
            ("👌 OK Sign", "Thumb+Index circle", "Close Window (Cmd+W)"),
        ]
        
        for emoji, how, action in gestures:
            print(f"{emoji:12} | {how:15} | {action}")
        
        print("="*60)
        print("💡 Tips:")
        print("  - Good lighting helps accuracy")
        print("  - Keep hand 1-2 feet from camera")
        print("  - Show full hand including wrist")
        print("  - Move smoothly for best results")
        print("  - Toggle AI (A) for complex gestures")
        print("  - Use Qwen (H) for best AI recognition")
        print("="*60 + "\n")
    
    def cleanup(self):
        """Cleanup"""
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
    import argparse
    
    print("""
╔═══════════════════════════════════════╗
║    Gestify Enhanced - AI Powered      ║
║    15+ Gestures | Qwen 2.5 VL        ║
║    Optimized for M1 MacBook Pro      ║
╚═══════════════════════════════════════╝
    """)
    
    parser = argparse.ArgumentParser(description="Enhanced Gestify with AI")
    parser.add_argument('--qwen', action='store_true', 
                       help='Use Hugging Face Qwen 2.5 VL (slow first load)')
    parser.add_argument('--ai', action='store_true',
                       help='Enable AI assistance from start')
    args = parser.parse_args()
    
    try:
        controller = EnhancedGestureController(use_huggingface=args.qwen)
        if args.ai:
            controller.use_ai_assist = True
        controller.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

