"""
AR Game Controller - integrates gesture control with AR games
"""

import cv2
import time
import numpy as np
from typing import Optional

from ..core.config import GestifyConfig
from ..detectors.hand_detector import HandDetector
from ..detectors.face_detector import FaceDetector, AttentionTracker
from ..detectors.gesture_recognizer import GestureRecognizer, Gesture
from .puzzle_game import PuzzleGame


class ARGameController:
    """AR Game controller with gesture controls"""
    
    def __init__(self, game_width: int = 1920, game_height: int = 1080,
                 difficulty: str = "easy"):
        """Initialize AR game controller
        
        Args:
            game_width: Game resolution width (default 1920 for HD)
            game_height: Game resolution height (default 1080 for HD)
            difficulty: Game difficulty
        """
        self.game_width = game_width
        self.game_height = game_height
        
        # Camera configuration for HD fullscreen
        self.config = GestifyConfig(
            camera_width=1920,
            camera_height=1080,
            camera_fps=30,
            max_hands=2,  # Detect up to 2 hands, use nearest
            enable_face_tracking=True,
            show_ui=True,
            show_debug=False,
            cursor_smoothing=3
        )
        
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
            cooldown=0.2,  # Shorter cooldown for game
            pinch_threshold=30
        )
        
        # Initialize game
        self.game = PuzzleGame(game_width, game_height, difficulty)
        
        # State
        self.running = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Cursor state
        self.cursor_pos = None
        self.cursor_history = []
        
        # Gesture state for game
        self.is_picking = False
        self.is_dragging = False
        
        print(f"✅ AR Game initialized: {game_width}x{game_height}")
    
    def _init_camera(self):
        """Initialize camera with HD settings"""
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                print(f"⚠️  Camera 0 not available, trying camera 1...")
                self.cap = cv2.VideoCapture(1)
            
            if not self.cap.isOpened():
                raise RuntimeError("No camera found")
            
            # Set HD resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
            
            # Additional quality settings
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            
            # Warm up
            time.sleep(0.5)
            for _ in range(5):
                self.cap.read()
            
            # Test read
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Cannot read from camera")
            
            actual_width = frame.shape[1]
            actual_height = frame.shape[0]
            
            print(f"✅ Camera initialized: {actual_width}x{actual_height} @ {self.config.camera_fps}fps")
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Close other apps using the camera")
            print("   2. Check camera permissions")
            print("   3. Try a lower resolution")
            raise
    
    def run(self):
        """Main game loop"""
        if not self.cap:
            raise RuntimeError("Camera not initialized")
        
        self.running = True
        
        print("\n🎮 AR PUZZLE GAME STARTED!")
        print("=" * 50)
        print("Controls:")
        print("  👆 Point finger - Move cursor")
        print("  👌 Pinch - Pick/Place pieces")
        print("  ✌️  Peace sign - Drag pieces")
        print("  🖐️  Open palm - Pause")
        print("  Q or ESC - Quit")
        print("  R - Restart puzzle")
        print("=" * 50)
        
        # Create fullscreen window
        cv2.namedWindow('AR Puzzle Game', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('AR Puzzle Game', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
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
                elif key == ord('r'):  # Restart
                    self.game.reset()
                    self.gesture_recognizer.reset()
                elif key == ord('d'):  # Toggle debug
                    self.config.show_debug = not self.config.show_debug
                
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
        """Process single frame with game overlay
        
        Args:
            frame: Camera frame
        """
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Resize to game resolution if needed
        if frame.shape[1] != self.game_width or frame.shape[0] != self.game_height:
            frame = cv2.resize(frame, (self.game_width, self.game_height))
        
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        
        # Detect hands
        hands = self.hand_detector.detect(frame_rgb)
        
        # Detect face and check attention
        user_looking = True
        if self.face_detector:
            face_landmarks = self.face_detector.detect(frame_rgb)
            is_looking = self.attention_tracker.check_attention(face_landmarks)
            user_looking = self.attention_tracker.update_attention(is_looking)
        
        # Make frame writable
        frame_rgb.flags.writeable = True
        
        # Recognize gesture
        h, w = frame.shape[:2]
        gesture = self.gesture_recognizer.recognize(hands, w, h, user_looking)
        
        # Update cursor position FIRST (always follows hand)
        self._update_cursor(hands, gesture, w, h)
        
        # Check if user is actively pinching (for continuous hold)
        # Use HYSTERESIS: different thresholds for grab vs release
        is_pinching = False
        if hands:
            # Use nearest hand for pinch detection
            selected_hand = self._select_nearest_hand(hands, w, h)
            hand_state = self.gesture_recognizer.analyze_hand(selected_hand, w, h)
            
            # Store for debugging display
            self._last_pinch_distance = hand_state.pinch_distance
            
            # Hysteresis thresholds for stable holding
            grab_threshold = self.gesture_recognizer.pinch_threshold * 2.0  # 60px to grab
            release_threshold = self.gesture_recognizer.pinch_threshold * 3.0  # 90px to release
            
            # If already holding, use more forgiving threshold
            if self.is_picking:
                # While holding: more forgiving (harder to accidentally release)
                is_pinching = hand_state.pinch_distance < release_threshold
            else:
                # Not holding: stricter threshold to grab
                is_pinching = hand_state.pinch_distance < grab_threshold
        
        # Handle game input from gestures
        is_picking = False
        is_releasing = False
        
        # Pick when starting to pinch
        if is_pinching and not self.is_picking:
            is_picking = True
            self.is_picking = True
            print(f"🤏 Pinching detected! (distance: {hand_state.pinch_distance:.1f}px)")
        
        # Release when pinch stops (with buffer for stability)
        elif not is_pinching and self.is_picking:
            is_releasing = True
            self.is_picking = False
            print(f"✋ Released! (distance: {hand_state.pinch_distance:.1f}px)")
        
        # Update game (is_holding tells game to keep object attached)
        self.game.update(self.cursor_pos, is_picking, is_releasing, self.is_picking)
        
        # Draw game on frame
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        self.game.draw(frame_bgr)
        
        # Draw hand landmarks (semi-transparent)
        if hands:
            overlay = frame_bgr.copy()
            self.hand_detector.draw_landmarks(overlay, hands)
            cv2.addWeighted(overlay, 0.5, frame_bgr, 0.5, 0, frame_bgr)
        
        # Draw cursor
        if self.cursor_pos:
            self._draw_cursor(frame_bgr, self.cursor_pos, gesture)
        
        # Draw FPS and status
        self._draw_status(frame_bgr, gesture, user_looking)
        
        # Show window
        cv2.imshow('AR Puzzle Game', frame_bgr)
    
    def _update_cursor(self, hands, gesture, width, height):
        """Update cursor position from hand - always follows hand when visible"""
        if hands:
            # If multiple hands, use the nearest/largest one
            selected_hand = self._select_nearest_hand(hands, width, height)
            
            # Always update cursor when hand is visible
            hand_state = self.gesture_recognizer.analyze_hand(selected_hand, width, height)
            
            # Use index finger tip position directly
            raw_pos = hand_state.position  # This is index finger tip in frame coordinates
            
            # Convert to game coordinates
            # Note: Frame is already flipped, so use direct mapping (no additional flip)
            x = int((raw_pos[0] / width) * self.game_width)
            y = int((raw_pos[1] / height) * self.game_height)
            
            # Clamp to screen bounds
            x = max(0, min(x, self.game_width - 1))
            y = max(0, min(y, self.game_height - 1))
            
            raw_game_pos = (x, y)
            
            # Smooth cursor movement
            self.cursor_history.append(raw_game_pos)
            if len(self.cursor_history) > 3:  # Reduced for more responsive
                self.cursor_history.pop(0)
            
            # Average for smoothing
            avg_x = sum(p[0] for p in self.cursor_history) // len(self.cursor_history)
            avg_y = sum(p[1] for p in self.cursor_history) // len(self.cursor_history)
            
            self.cursor_pos = (avg_x, avg_y)
        else:
            self.cursor_pos = None
            self.cursor_history.clear()
    
    def _select_nearest_hand(self, hands, width, height):
        """Select the nearest/largest hand from multiple detected hands"""
        if len(hands) == 1:
            return hands[0]
        
        # Calculate hand size for each hand (larger = closer to camera)
        hand_sizes = []
        for hand in hands:
            # Get wrist and middle finger tip to estimate hand size
            wrist = hand.get_landmark_px(self.hand_detector.WRIST, width, height)
            middle_tip = hand.get_landmark_px(self.hand_detector.MIDDLE_TIP, width, height)
            
            # Calculate distance as a measure of hand size
            import math
            size = math.sqrt((middle_tip[0] - wrist[0])**2 + (middle_tip[1] - wrist[1])**2)
            hand_sizes.append(size)
        
        # Return the hand with largest size (nearest to camera)
        nearest_idx = hand_sizes.index(max(hand_sizes))
        return hands[nearest_idx]
    
    def _draw_cursor(self, frame: np.ndarray, pos: tuple, gesture: Gesture):
        """Draw cursor at hand position"""
        x, y = pos
        
        # Cursor color based on state
        if self.is_picking:
            color = (0, 255, 0)  # Green when holding/picking
            size = 35
            thickness = 3
        else:
            color = (100, 255, 255)  # Cyan/yellow when ready
            size = 25
            thickness = 2
        
        # Draw outer circle (hand indicator)
        cv2.circle(frame, (x, y), size, color, thickness)
        
        # Draw inner dot
        cv2.circle(frame, (x, y), 8, color, -1)
        
        # Draw crosshair lines
        line_len = size + 10
        cv2.line(frame, (x - line_len, y), (x - size, y), color, thickness)
        cv2.line(frame, (x + size, y), (x + line_len, y), color, thickness)
        cv2.line(frame, (x, y - line_len), (x, y - size), color, thickness)
        cv2.line(frame, (x, y + size), (x, y + line_len), color, thickness)
        
        # Status text
        if self.is_picking:
            status_text = "HOLDING"
            text_color = (0, 255, 0)
        else:
            status_text = "READY"
            text_color = (100, 255, 255)
        
        cv2.putText(frame, status_text, 
                   (x - 40, y - size - 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
    
    def _draw_status(self, frame: np.ndarray, gesture: Gesture, user_looking: bool):
        """Draw status information"""
        h, w = frame.shape[:2]
        
        # FPS
        cv2.putText(frame, f"FPS: {int(self.fps)}", 
                   (w - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Current gesture
        gesture_text = gesture.name.replace('_', ' ')
        cv2.putText(frame, f"Gesture: {gesture_text}", 
                   (w - 300, h - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Pinch distance (for debugging)
        if hasattr(self, '_last_pinch_distance'):
            cv2.putText(frame, f"Pinch: {self._last_pinch_distance:.0f}px", 
                       (w - 300, h - 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Attention indicator
        attention_color = (0, 255, 0) if user_looking else (0, 0, 255)
        attention_text = "LOOKING" if user_looking else "NOT LOOKING"
        cv2.circle(frame, (w - 350, h - 25), 10, attention_color, -1)
        cv2.putText(frame, attention_text, 
                   (w - 330, h - 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, attention_color, 1)
        
        # Controls reminder (bottom left)
        cv2.putText(frame, "Q: Quit | R: Restart | D: Debug", 
                   (10, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _cleanup(self):
        """Clean up resources"""
        print("\n🛑 Shutting down AR Game...")
        
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        self.hand_detector.close()
        self.face_detector.close()
        
        # Print statistics
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 Game Statistics:")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Final Score: {self.game.score}")
        print(f"   Total Moves: {self.game.moves}")
        print("\n👋 Thanks for playing!")
    
    def stop(self):
        """Stop the game"""
        self.running = False

