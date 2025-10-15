"""
Realistic AR Piano Controller - Multi-finger tracking with motion detection
"""

import cv2
import time
import numpy as np
from typing import Optional, Tuple, List, Dict

from ..core.config import GestifyConfig
from ..detectors.hand_detector import HandDetector, Hand
from ..detectors.gesture_recognizer import GestureRecognizer
from .piano_game import RealisticARPiano, Fingertip


class RealisticARPianoController:
    """Realistic AR Piano controller with all-finger tracking"""
    
    def __init__(self, game_width: int = 1920, game_height: int = 1080):
        """Initialize realistic AR piano controller"""
        self.game_width = game_width
        self.game_height = game_height
        
        # Camera configuration
        self.config = GestifyConfig(
            camera_width=1920,
            camera_height=1080,
            camera_fps=30,
            max_hands=2,  # Track both hands
            enable_face_tracking=False,
            show_ui=True,
            show_debug=False,
            cursor_smoothing=1
        )
        
        # Initialize camera
        self.cap = None
        self._init_camera()
        
        # Initialize hand detector
        self.hand_detector = HandDetector(
            max_hands=self.config.max_hands,
            min_detection_confidence=self.config.hand_confidence,
            min_tracking_confidence=self.config.hand_tracking_confidence,
            model_complexity=self.config.hand_model_complexity
        )
        
        # Initialize gesture recognizer for menu gestures
        self.gesture_recognizer = GestureRecognizer()
        
        # Initialize piano game
        self.piano = RealisticARPiano(game_width, game_height)
        
        # State
        self.running = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Fingertip tracking history
        self._fingertip_history: Dict[str, List[Tuple[int, int]]] = {}
        
        # Finger landmark indices (MediaPipe)
        self.finger_tips = {
            'thumb': self.hand_detector.THUMB_TIP,
            'index': self.hand_detector.INDEX_TIP,
            'middle': self.hand_detector.MIDDLE_TIP,
            'ring': self.hand_detector.RING_TIP,
            'pinky': self.hand_detector.PINKY_TIP,
        }
        
        print(f"✅ Realistic AR Piano initialized: {game_width}x{game_height}")
    
    def _init_camera(self):
        """Initialize camera"""
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(1)
            
            if not self.cap.isOpened():
                raise RuntimeError("No camera found")
            
            # Set HD resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            
            # Warm up
            time.sleep(0.5)
            for _ in range(5):
                self.cap.read()
            
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Cannot read from camera")
            
            print(f"✅ Camera initialized: {frame.shape[1]}x{frame.shape[0]}")
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            raise
    
    def run(self):
        """Main game loop"""
        if not self.cap:
            raise RuntimeError("Camera not initialized")
        
        self.running = True
        
        print("\n🎹 REALISTIC AR PIANO STARTED!")
        print("=" * 60)
        print("Welcome to Realistic AR Piano!")
        print("")
        print("How to Play:")
        print("  • Hold hands above the piano keyboard")
        print("  • Move fingers DOWN to press keys (like real piano)")
        print("  • All 10 fingers are tracked!")
        print("  • Fast downward motion = key press")
        print("")
        print("Song Learning:")
        print("  • Hover hand over song for 1.5 seconds to select")
        print("  • Follow falling notes")
        print("  • Press keys when notes reach the HIT zone")
        print("  • Build combos for higher scores!")
        print("")
        print("Gestures:")
        print("  • Open palm: Return to menu")
        print("  • No keyboard needed - pure gesture control!")
        print("=" * 60)
        
        # Create fullscreen window
        cv2.namedWindow('AR Piano', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('AR Piano', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
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
                
                # Handle ESC to quit (only keyboard shortcut)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                
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
        """Process frame"""
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Resize if needed
        if frame.shape[1] != self.game_width or frame.shape[0] != self.game_height:
            frame = cv2.resize(frame, (self.game_width, self.game_height))
        
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        
        # Detect hands
        hands = self.hand_detector.detect(frame_rgb)
        
        frame_rgb.flags.writeable = True
        
        # Get all fingertips with velocity tracking
        h, w = frame.shape[:2]
        fingertips = self._get_all_fingertips(hands, w, h)
        
        # Check for gestures (for menu control)
        if hands and not self.piano.show_song_menu:
            gesture, _ = self.gesture_recognizer.recognize(hands)
            if gesture:
                self.piano.handle_gesture(gesture.name)
        
        # Update piano
        self.piano.update(fingertips)
        
        # Draw piano on frame
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        self.piano.draw(frame_bgr, fingertips)
        
        # Draw hand landmarks (semi-transparent)
        if hands:
            overlay = frame_bgr.copy()
            for hand in hands:
                self.hand_detector.draw_landmarks(overlay, [hand])
            cv2.addWeighted(overlay, 0.2, frame_bgr, 0.8, 0, frame_bgr)
        
        # Draw FPS and instructions
        cv2.putText(frame_bgr, f"FPS: {int(self.fps)}", 
                   (10, self.game_height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame_bgr, f"Fingers tracked: {len(fingertips)}", 
                   (10, self.game_height - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        if not self.piano.show_song_menu:
            cv2.putText(frame_bgr, "Move fingers DOWN to press keys", 
                       (self.game_width // 2 - 200, self.game_height - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Show window
        cv2.imshow('AR Piano', frame_bgr)
    
    def _get_all_fingertips(self, hands: Optional[List[Hand]], 
                           width: int, height: int) -> List[Fingertip]:
        """Get all fingertips from all hands with velocity tracking
        
        Args:
            hands: Detected hands
            width: Frame width
            height: Frame height
            
        Returns:
            List of Fingertip objects with position and velocity
        """
        if not hands:
            return []
        
        fingertips = []
        
        for hand_idx, hand in enumerate(hands):
            hand_label = f"{hand.label}_{hand_idx}"
            
            # Get all 5 fingertips
            for finger_name, landmark_idx in self.finger_tips.items():
                try:
                    # Get fingertip position
                    position = hand.get_landmark_px(landmark_idx, width, height)
                    
                    # Create unique key for this fingertip
                    tip_key = f"{hand_label}_{finger_name}"
                    
                    # Get previous position from history
                    history = self._fingertip_history.get(tip_key, [])
                    previous_position = history[-1] if history else None
                    
                    # Create fingertip object
                    fingertip = Fingertip(
                        position=position,
                        previous_position=previous_position,
                        name=f"{hand.label}_{finger_name}"
                    )
                    
                    # Calculate velocity
                    fingertip.update_velocity()
                    
                    # Update history
                    history.append(position)
                    if len(history) > 3:  # Keep last 3 positions
                        history.pop(0)
                    self._fingertip_history[tip_key] = history
                    
                    fingertips.append(fingertip)
                    
                except Exception as e:
                    continue
        
        return fingertips
    
    def _cleanup(self):
        """Clean up resources"""
        print("\n🛑 Shutting down AR Piano...")
        
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        self.hand_detector.close()
        
        # Cleanup piano (audio)
        self.piano.cleanup()
        
        # Print statistics
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 Session Statistics:")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Final Score: {self.piano.score}")
        print("\n👋 Thanks for playing!")
    
    def stop(self):
        """Stop the piano"""
        self.running = False
