"""
UI rendering for gesture feedback
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple

from ..detectors.gesture_recognizer import Gesture, HandState
from ..detectors.hand_detector import Hand


class UIRenderer:
    """Render UI overlays on camera feed"""
    
    # Colors (BGR format for OpenCV)
    COLOR_PRIMARY = (0, 255, 0)      # Green
    COLOR_ACTIVE = (0, 165, 255)     # Orange
    COLOR_ATTENTION = (0, 255, 255)  # Yellow
    COLOR_WARNING = (0, 0, 255)      # Red
    COLOR_INFO = (255, 255, 255)     # White
    COLOR_BG = (0, 0, 0)              # Black
    
    def __init__(self):
        """Initialize UI renderer"""
        self.fps_history = []
        self.max_fps_samples = 30
    
    def render(self, 
               frame: np.ndarray,
               hands: Optional[List[Hand]],
               gesture: Gesture,
               user_looking: bool,
               fps: float,
               show_debug: bool = False) -> np.ndarray:
        """Render UI on frame
        
        Args:
            frame: Camera frame
            hands: Detected hands
            gesture: Current gesture
            user_looking: Whether user is looking at screen
            fps: Current FPS
            show_debug: Show debug information
            
        Returns:
            Frame with UI overlay
        """
        # Create overlay
        overlay = frame.copy()
        
        # Draw attention indicator
        self._draw_attention_indicator(overlay, user_looking)
        
        # Draw gesture name
        self._draw_gesture(overlay, gesture, user_looking)
        
        # Draw FPS
        self._draw_fps(overlay, fps)
        
        # Debug info
        if show_debug and hands:
            self._draw_debug_info(overlay, hands)
        
        # Draw instructions
        self._draw_instructions(overlay)
        
        return overlay
    
    def _draw_attention_indicator(self, frame: np.ndarray, looking: bool):
        """Draw attention status indicator
        
        Args:
            frame: Frame to draw on
            looking: Whether user is looking
        """
        h, w = frame.shape[:2]
        
        # Status indicator in top-right
        indicator_pos = (w - 30, 30)
        color = self.COLOR_PRIMARY if looking else self.COLOR_WARNING
        status_text = "👁️" if looking else "⚠️"
        
        cv2.circle(frame, indicator_pos, 15, color, -1)
        
        # Text label
        label = "Looking" if looking else "Not Looking"
        text_pos = (w - 120, 35)
        cv2.putText(frame, label, text_pos, cv2.FONT_HERSHEY_SIMPLEX,
                   0.5, color, 2)
    
    def _draw_gesture(self, frame: np.ndarray, gesture: Gesture, active: bool):
        """Draw current gesture name
        
        Args:
            frame: Frame to draw on
            gesture: Current gesture
            active: Whether gesture is active
        """
        if gesture == Gesture.NONE or gesture == Gesture.CURSOR_MOVE:
            return
        
        h, w = frame.shape[:2]
        
        # Gesture name mapping
        gesture_names = {
            Gesture.CLICK: "🖱️  Click",
            Gesture.DOUBLE_CLICK: "🖱️  Double Click",
            Gesture.DRAG_START: "✊ Drag Start",
            Gesture.DRAG_END: "✋ Drag End",
            Gesture.SCROLL: "📜 Scroll",
            Gesture.ZOOM_IN: "🔍 Zoom In",
            Gesture.ZOOM_OUT: "🔍 Zoom Out",
            Gesture.ROTATE_CW: "🔄 Rotate →",
            Gesture.ROTATE_CCW: "🔄 Rotate ←",
            Gesture.PAUSE: "⏸️  Pause",
            Gesture.CONFIRM: "✅ Confirm",
            Gesture.CANCEL: "❌ Cancel",
        }
        
        text = gesture_names.get(gesture, "")
        if not text:
            return
        
        # Draw gesture name in center
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
        text_x = (w - text_size[0]) // 2
        text_y = h // 2
        
        # Background rectangle
        padding = 20
        cv2.rectangle(frame,
                     (text_x - padding, text_y - text_size[1] - padding),
                     (text_x + text_size[0] + padding, text_y + padding),
                     self.COLOR_BG, -1)
        
        # Text
        color = self.COLOR_ACTIVE if active else self.COLOR_PRIMARY
        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    
    def _draw_fps(self, frame: np.ndarray, fps: float):
        """Draw FPS counter
        
        Args:
            frame: Frame to draw on
            fps: Current FPS
        """
        # Smooth FPS
        self.fps_history.append(fps)
        if len(self.fps_history) > self.max_fps_samples:
            self.fps_history.pop(0)
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        
        # Draw in top-left
        text = f"FPS: {avg_fps:.1f}"
        cv2.putText(frame, text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_INFO, 2)
    
    def _draw_debug_info(self, frame: np.ndarray, hands: List[Hand]):
        """Draw debug information
        
        Args:
            frame: Frame to draw on
            hands: Detected hands
        """
        h, w = frame.shape[:2]
        y_offset = 60
        
        for i, hand in enumerate(hands):
            info = f"Hand {i+1}: {hand.handedness} ({hand.confidence:.2f})"
            cv2.putText(frame, info, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_INFO, 1)
            y_offset += 25
    
    def _draw_instructions(self, frame: np.ndarray):
        """Draw gesture instructions
        
        Args:
            frame: Frame to draw on
        """
        h, w = frame.shape[:2]
        
        instructions = [
            "Gestures:",
            "☝️  Index: Move cursor",
            "✌️  Peace: Drag",
            "👌 Pinch: Click",
            "✊ Fist: Scroll",
            "🖐️  Palm: Pause",
            "👍 Thumbs up: Confirm",
            "👎 Thumbs down: Cancel",
            "🤲 Two hands: Zoom/Rotate",
        ]
        
        y_offset = h - 20 * len(instructions) - 10
        
        for instruction in instructions:
            cv2.putText(frame, instruction, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.COLOR_INFO, 1)
            y_offset += 20
    
    def draw_cursor_indicator(self, frame: np.ndarray, 
                             position: Tuple[int, int],
                             is_dragging: bool = False):
        """Draw cursor position indicator
        
        Args:
            frame: Frame to draw on
            position: Cursor position in frame coordinates
            is_dragging: Whether currently dragging
        """
        color = self.COLOR_ACTIVE if is_dragging else self.COLOR_PRIMARY
        
        # Draw crosshair
        size = 20
        x, y = position
        
        cv2.line(frame, (x - size, y), (x + size, y), color, 2)
        cv2.line(frame, (x, y - size), (x, y + size), color, 2)
        cv2.circle(frame, position, 5, color, -1)

