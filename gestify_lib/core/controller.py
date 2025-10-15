"""
Main Gestify controller - orchestrates all components
"""

import cv2
import time
import numpy as np
from typing import Optional

from .config import GestifyConfig
from ..detectors.hand_detector import HandDetector
from ..detectors.face_detector import FaceDetector, AttentionTracker
from ..detectors.gesture_recognizer import GestureRecognizer, Gesture
from ..utils.action_executor import ActionExecutor
from ..utils.ui_renderer import UIRenderer


class GestifyController:
    """Main controller for Gestify gesture control"""
    
    def __init__(self, config: Optional[GestifyConfig] = None):
        """Initialize Gestify controller
        
        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or GestifyConfig()
        
        # Initialize camera
        self.cap = None
        self._init_camera()
        
        # Initialize detectors
        self.hand_detector = HandDetector(
            max_hands=self.config.max_hands,
            min_detection_confidence=self.config.hand_confidence,
            min_tracking_confidence=self.config.hand_tracking_confidence,
            model_complexity=self.config.hand_model_complexity
        )
        
        self.face_detector = None
        self.attention_tracker = None
        if self.config.enable_face_tracking:
            self.face_detector = FaceDetector(
                min_detection_confidence=self.config.face_confidence,
                min_tracking_confidence=self.config.face_tracking_confidence
            )
            self.attention_tracker = AttentionTracker(
                buffer_size=self.config.attention_buffer_size,
                attention_threshold=self.config.attention_threshold
            )
        
        # Initialize gesture recognizer
        self.gesture_recognizer = GestureRecognizer(
            hand_detector=self.hand_detector,
            cooldown=self.config.gesture_cooldown,
            pinch_threshold=self.config.pinch_threshold
        )
        
        # Initialize action executor
        self.action_executor = ActionExecutor(
            smoothing=self.config.cursor_smoothing
        )
        
        # Initialize UI renderer
        self.ui_renderer = UIRenderer() if self.config.show_ui else None
        
        # State
        self.running = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
    
    def _init_camera(self):
        """Initialize camera with error handling"""
        try:
            self.cap = cv2.VideoCapture(self.config.camera_index)
            
            if not self.cap.isOpened():
                print(f"⚠️  Camera {self.config.camera_index} not available, trying camera 1...")
                self.cap = cv2.VideoCapture(1)
            
            if not self.cap.isOpened():
                raise RuntimeError("No camera found")
            
            # Configure camera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
            
            # Warm up
            time.sleep(0.5)
            
            # Test read
            ret, _ = self.cap.read()
            if not ret:
                raise RuntimeError("Cannot read from camera")
            
            print(f"✅ Camera initialized: {self.config.camera_width}x{self.config.camera_height} @ {self.config.camera_fps}fps")
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Close other apps using the camera (Zoom, FaceTime, etc.)")
            print("   2. Check camera permissions in System Preferences")
            print("   3. Try running: python fix_camera.sh")
            raise
    
    def run(self):
        """Main control loop"""
        if not self.cap:
            raise RuntimeError("Camera not initialized")
        
        self.running = True
        print("\n🎮 Gestify Started!")
        print("📹 Camera feed window will open...")
        print("Press 'q' or ESC to quit\n")
        
        last_frame_time = time.time()
        
        try:
            while self.running:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️  Failed to read frame")
                    break
                
                # Calculate FPS
                current_time = time.time()
                self.fps = 1.0 / (current_time - last_frame_time) if last_frame_time else 0
                last_frame_time = current_time
                
                # Process frame
                self._process_frame(frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('d'):  # Toggle debug
                    self.config.show_debug = not self.config.show_debug
                elif key == ord('f'):  # Toggle face tracking
                    self.config.enable_face_tracking = not self.config.enable_face_tracking
                    if self.config.enable_face_tracking:
                        print("👁️  Face tracking enabled")
                    else:
                        print("👁️  Face tracking disabled")
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self._cleanup()
    
    def _process_frame(self, frame: np.ndarray):
        """Process single frame
        
        Args:
            frame: Camera frame
        """
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        
        # Detect hands
        hands = self.hand_detector.detect(frame_rgb)
        
        # Detect face and check attention
        user_looking = True
        if self.config.enable_face_tracking and self.face_detector:
            face_landmarks = self.face_detector.detect(frame_rgb)
            is_looking = self.attention_tracker.check_attention(face_landmarks)
            user_looking = self.attention_tracker.update_attention(is_looking)
        
        # Make frame writable again
        frame_rgb.flags.writeable = True
        
        # Recognize gesture
        h, w = frame.shape[:2]
        gesture = self.gesture_recognizer.recognize(hands, w, h, user_looking)
        
        # Execute action
        if gesture != Gesture.NONE:
            # Get cursor position for movement gestures
            cursor_pos = None
            if hands and gesture in [Gesture.CURSOR_MOVE, Gesture.DRAG_START]:
                hand_state = self.gesture_recognizer.analyze_hand(hands[0], w, h)
                cursor_pos = self.gesture_recognizer.get_cursor_position(
                    hand_state,
                    self.action_executor.screen_width,
                    self.action_executor.screen_height,
                    w, h
                )
            
            # Execute gesture action
            self.action_executor.execute(gesture, cursor_pos)
            
            # Handle scroll separately (continuous action)
            if gesture == Gesture.SCROLL and hands:
                hand_state = self.gesture_recognizer.analyze_hand(hands[0], w, h)
                self.action_executor.scroll(hand_state.velocity[1])
        
        # Render UI
        if self.config.show_ui and self.ui_renderer:
            # Draw hand landmarks
            if hands:
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                self.hand_detector.draw_landmarks(frame_bgr, hands)
                frame = frame_bgr
            
            # Draw UI overlay
            frame = self.ui_renderer.render(
                frame=frame,
                hands=hands,
                gesture=gesture,
                user_looking=user_looking,
                fps=self.fps,
                show_debug=self.config.show_debug
            )
            
            # Show window
            cv2.imshow('Gestify - Hand Gesture Control', frame)
    
    def _cleanup(self):
        """Clean up resources"""
        print("\n🛑 Shutting down...")
        
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        self.hand_detector.close()
        if self.face_detector:
            self.face_detector.close()
        
        # Print statistics
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 Statistics:")
        print(f"   Frames processed: {self.frame_count}")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print("\n👋 Gestify stopped. Goodbye!")
    
    def stop(self):
        """Stop the controller"""
        self.running = False

