"""
AR Ping Pong Game Controller - Two player hand-controlled game
"""

import cv2
import time
import numpy as np
from typing import Optional, Tuple, List

from ..core.config import GestifyConfig
from ..detectors.hand_detector import HandDetector, Hand
from ..detectors.face_detector import FaceDetector, AttentionTracker
from ..detectors.gesture_recognizer import GestureRecognizer, Gesture
from .pingpong_game import PingPongGame


class PingPongGameController:
    """AR Ping Pong game controller with two-player hand tracking"""
    
    def __init__(self, game_width: int = 1920, game_height: int = 1080):
        """Initialize ping pong game controller
        
        Args:
            game_width: Game resolution width
            game_height: Game resolution height
        """
        self.game_width = game_width
        self.game_height = game_height
        
        # Camera configuration for HD fullscreen
        self.config = GestifyConfig(
            camera_width=1920,
            camera_height=1080,
            camera_fps=30,
            max_hands=2,  # Two players!
            enable_face_tracking=False,  # Not needed for ping pong
            show_ui=True,
            show_debug=False,
            cursor_smoothing=2  # Faster response for game
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
        
        # Initialize game
        self.game = PingPongGame(game_width, game_height)
        
        # State
        self.running = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        print(f"✅ AR Ping Pong initialized: {game_width}x{game_height}")
    
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
        
        print("\n🏓 AR PING PONG GAME STARTED!")
        print("=" * 60)
        print("Controls:")
        print("  LEFT PLAYER: Show hand on LEFT side of screen")
        print("  RIGHT PLAYER: Show hand on RIGHT side of screen")
        print("  Move hand UP/DOWN to control paddle")
        print("  First to 11 points wins!")
        print("")
        print("  R - Restart game")
        print("  Q or ESC - Quit")
        print("=" * 60)
        
        # Create fullscreen window
        cv2.namedWindow('AR Ping Pong', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('AR Ping Pong', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
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
        
        # Make frame writable
        frame_rgb.flags.writeable = True
        
        # Separate hands by screen position
        h, w = frame.shape[:2]
        left_hand_y, right_hand_y = self._get_player_hands(hands, w, h)
        
        # Update game
        self.game.update(left_hand_y, right_hand_y)
        
        # Draw game on frame
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        self.game.draw(frame_bgr)
        
        # Draw hand landmarks (semi-transparent)
        if hands:
            overlay = frame_bgr.copy()
            for hand in hands:
                self.hand_detector.draw_landmarks(overlay, [hand])
            cv2.addWeighted(overlay, 0.3, frame_bgr, 0.7, 0, frame_bgr)
        
        # Draw hand indicators
        if left_hand_y:
            self._draw_hand_indicator(frame_bgr, 100, left_hand_y, (0, 255, 0), "LEFT")
        if right_hand_y:
            self._draw_hand_indicator(frame_bgr, w - 100, right_hand_y, (0, 0, 255), "RIGHT")
        
        # Draw FPS
        self._draw_fps(frame_bgr)
        
        # Show window
        cv2.imshow('AR Ping Pong', frame_bgr)
    
    def _get_player_hands(self, hands: Optional[List[Hand]], 
                          width: int, height: int) -> Tuple[Optional[int], Optional[int]]:
        """Separate hands into left and right players with smoothing
        
        Args:
            hands: Detected hands
            width: Frame width
            height: Frame height
            
        Returns:
            (left_hand_y, right_hand_y) - Y positions or None
        """
        if not hands:
            return None, None
        
        # If more than 2 hands, select 2 nearest/largest
        if len(hands) > 2:
            hands = self._select_nearest_hands(hands, width, height, count=2)
        
        left_hand_y = None
        right_hand_y = None
        
        for hand in hands:
            # Get hand center position
            wrist = hand.get_landmark_px(self.hand_detector.WRIST, width, height)
            middle_tip = hand.get_landmark_px(self.hand_detector.MIDDLE_TIP, width, height)
            
            # Average Y position
            hand_y = (wrist[1] + middle_tip[1]) // 2
            hand_x = (wrist[0] + middle_tip[0]) // 2
            
            # Determine which side of screen (with buffer zone in middle)
            center = width // 2
            buffer = width // 6  # 1/6 of screen width as buffer
            
            if hand_x < center - buffer:
                # Left side - left player
                left_hand_y = hand_y
            elif hand_x > center + buffer:
                # Right side - right player
                right_hand_y = hand_y
            # Hands in middle buffer zone are ignored
        
        # Apply smoothing using history
        left_hand_y = self._smooth_hand_position(left_hand_y, 'left')
        right_hand_y = self._smooth_hand_position(right_hand_y, 'right')
        
        return left_hand_y, right_hand_y
    
    def _select_nearest_hands(self, hands: List[Hand], width: int, height: int, count: int = 2) -> List[Hand]:
        """Select N nearest/largest hands from detected hands
        
        Args:
            hands: All detected hands
            width: Frame width
            height: Frame height
            count: Number of hands to select
            
        Returns:
            List of N nearest hands
        """
        # Calculate hand size for each hand
        hand_sizes = []
        for hand in hands:
            wrist = hand.get_landmark_px(self.hand_detector.WRIST, width, height)
            middle_tip = hand.get_landmark_px(self.hand_detector.MIDDLE_TIP, width, height)
            
            # Calculate size (larger = closer to camera)
            import math
            size = math.sqrt((middle_tip[0] - wrist[0])**2 + (middle_tip[1] - wrist[1])**2)
            hand_sizes.append((size, hand))
        
        # Sort by size (largest first) and take top N
        hand_sizes.sort(key=lambda x: x[0], reverse=True)
        return [hand for _, hand in hand_sizes[:count]]
    
    def _smooth_hand_position(self, hand_y: Optional[int], side: str) -> Optional[int]:
        """Smooth hand position using history buffer
        
        Args:
            hand_y: Current hand Y position (or None if not detected)
            side: 'left' or 'right'
            
        Returns:
            Smoothed Y position or None
        """
        # Initialize history buffers if needed
        if not hasattr(self, '_hand_history'):
            self._hand_history = {'left': [], 'right': []}
        
        history = self._hand_history[side]
        
        # Add current position to history
        if hand_y is not None:
            history.append(hand_y)
            # Keep last 5 positions
            if len(history) > 5:
                history.pop(0)
        else:
            # Hand not detected - clear history after a few frames
            if len(history) > 0:
                # Keep history for 2 frames to handle brief occlusions
                history.pop(0)
            return None
        
        # Return averaged position
        if len(history) > 0:
            return sum(history) // len(history)
        
        return None
    
    def _draw_hand_indicator(self, frame: np.ndarray, x: int, y: int, 
                            color: Tuple[int, int, int], label: str):
        """Draw hand position indicator"""
        # Draw circle at hand position
        cv2.circle(frame, (x, y), 20, color, 3)
        cv2.circle(frame, (x, y), 5, color, -1)
        
        # Draw vertical line
        cv2.line(frame, (x, 0), (x, frame.shape[0]), color, 1)
        
        # Draw label
        cv2.putText(frame, label, (x - 30, y - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _draw_fps(self, frame: np.ndarray):
        """Draw FPS counter"""
        cv2.putText(frame, f"FPS: {int(self.fps)}", 
                   (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def _cleanup(self):
        """Clean up resources"""
        print("\n🛑 Shutting down AR Ping Pong...")
        
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        self.hand_detector.close()
        
        # Print statistics
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 Game Statistics:")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Final Score: {self.game.left_score} - {self.game.right_score}")
        print("\n👋 Thanks for playing!")
    
    def stop(self):
        """Stop the game"""
        self.running = False

