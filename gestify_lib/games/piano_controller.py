"""
AR Piano Controller - Hand tracking for piano playing
"""

import cv2
import time
import numpy as np
from typing import Optional, Tuple, List

from ..core.config import GestifyConfig
from ..detectors.hand_detector import HandDetector, Hand
from .piano_game import ARPiano


class ARPianoController:
    """AR Piano controller with hand tracking"""
    
    def __init__(self, game_width: int = 1920, game_height: int = 1080):
        """Initialize AR piano controller
        
        Args:
            game_width: Game resolution width
            game_height: Game resolution height
        """
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
            cursor_smoothing=2
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
        
        # Initialize piano game
        self.piano = ARPiano(game_width, game_height)
        
        # State
        self.running = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Hand tracking
        self._hand_history = {'left': [], 'right': []}
        
        print(f"✅ AR Piano initialized: {game_width}x{game_height}")
    
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
        
        print("\n🎹 AR PIANO STARTED!")
        print("=" * 60)
        print("Welcome to AR Piano!")
        print("")
        print("How to Play:")
        print("  • Position hands above piano keys")
        print("  • Touch keys with fingertips to play")
        print("  • Select a song from the menu")
        print("  • Follow falling notes and hit keys in time")
        print("  • Build combos for higher scores!")
        print("")
        print("Controls:")
        print("  • 1-4: Select song from menu")
        print("  • M: Return to song menu")
        print("  • Q or ESC: Quit")
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
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Q or ESC
                    break
                elif key != 255:  # Any other key
                    self.piano.handle_key_press(key)
                
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
        
        # Get fingertip positions
        h, w = frame.shape[:2]
        left_hand_pos, right_hand_pos = self._get_hand_positions(hands, w, h)
        
        # Update piano
        self.piano.update(left_hand_pos, right_hand_pos)
        
        # Draw piano on frame
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        self.piano.draw(frame_bgr)
        
        # Draw hand landmarks (semi-transparent)
        if hands:
            overlay = frame_bgr.copy()
            for hand in hands:
                self.hand_detector.draw_landmarks(overlay, [hand])
            cv2.addWeighted(overlay, 0.3, frame_bgr, 0.7, 0, frame_bgr)
        
        # Draw fingertip indicators
        if left_hand_pos:
            cv2.circle(frame_bgr, left_hand_pos, 15, (0, 255, 0), 3)
            cv2.circle(frame_bgr, left_hand_pos, 5, (0, 255, 0), -1)
        
        if right_hand_pos:
            cv2.circle(frame_bgr, right_hand_pos, 15, (0, 0, 255), 3)
            cv2.circle(frame_bgr, right_hand_pos, 5, (0, 0, 255), -1)
        
        # Draw FPS
        cv2.putText(frame_bgr, f"FPS: {int(self.fps)}", 
                   (10, self.game_height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show window
        cv2.imshow('AR Piano', frame_bgr)
    
    def _get_hand_positions(self, hands: Optional[List[Hand]], 
                           width: int, height: int) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """Get fingertip positions for both hands
        
        Args:
            hands: Detected hands
            width: Frame width
            height: Frame height
            
        Returns:
            (left_hand_pos, right_hand_pos) - Index fingertip positions
        """
        if not hands:
            return None, None
        
        # Select up to 2 nearest hands
        if len(hands) > 2:
            hands = self._select_nearest_hands(hands, width, height, count=2)
        
        left_hand_pos = None
        right_hand_pos = None
        
        for hand in hands:
            # Get index finger tip position
            index_tip = hand.get_landmark_px(self.hand_detector.INDEX_TIP, width, height)
            
            # Determine which hand based on position
            center = width // 2
            
            if index_tip[0] < center:
                # Left side
                left_hand_pos = self._smooth_hand_position(index_tip, 'left')
            else:
                # Right side
                right_hand_pos = self._smooth_hand_position(index_tip, 'right')
        
        return left_hand_pos, right_hand_pos
    
    def _select_nearest_hands(self, hands: List[Hand], width: int, height: int, count: int = 2) -> List[Hand]:
        """Select N nearest hands"""
        hand_sizes = []
        for hand in hands:
            wrist = hand.get_landmark_px(self.hand_detector.WRIST, width, height)
            middle_tip = hand.get_landmark_px(self.hand_detector.MIDDLE_TIP, width, height)
            
            import math
            size = math.sqrt((middle_tip[0] - wrist[0])**2 + (middle_tip[1] - wrist[1])**2)
            hand_sizes.append((size, hand))
        
        hand_sizes.sort(key=lambda x: x[0], reverse=True)
        return [hand for _, hand in hand_sizes[:count]]
    
    def _smooth_hand_position(self, pos: Tuple[int, int], side: str) -> Tuple[int, int]:
        """Smooth hand position using history"""
        history = self._hand_history[side]
        
        history.append(pos)
        if len(history) > 3:  # Less smoothing for piano (more responsive)
            history.pop(0)
        
        # Average position
        if len(history) > 0:
            avg_x = sum(p[0] for p in history) // len(history)
            avg_y = sum(p[1] for p in history) // len(history)
            return (avg_x, avg_y)
        
        return pos
    
    def _cleanup(self):
        """Clean up resources"""
        print("\n🛑 Shutting down AR Piano...")
        
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        self.hand_detector.close()
        
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

