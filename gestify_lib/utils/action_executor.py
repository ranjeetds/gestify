"""
Execute system actions based on gestures
"""

import pyautogui
import platform
from typing import Tuple
from collections import deque

from ..detectors.gesture_recognizer import Gesture


class ActionExecutor:
    """Execute system actions for gestures"""
    
    def __init__(self, smoothing: int = 5):
        """Initialize action executor
        
        Args:
            smoothing: Number of frames for cursor position smoothing
        """
        # Configure pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.001    # Minimal delay between actions
        
        # Cursor smoothing
        self.cursor_history = deque(maxlen=smoothing)
        
        # Drag state
        self.is_dragging = False
        
        # Get screen size
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Platform-specific settings
        self.is_macos = platform.system() == 'Darwin'
        self.mod_key = 'command' if self.is_macos else 'ctrl'
    
    def execute(self, gesture: Gesture, cursor_pos: Tuple[int, int] = None):
        """Execute action for gesture
        
        Args:
            gesture: Detected gesture
            cursor_pos: Cursor position for move/drag
        """
        try:
            if gesture == Gesture.CURSOR_MOVE:
                if cursor_pos:
                    self._move_cursor(cursor_pos)
            
            elif gesture == Gesture.CLICK:
                pyautogui.click()
                print("🖱️  Click")
            
            elif gesture == Gesture.DOUBLE_CLICK:
                pyautogui.doubleClick()
                print("🖱️  Double Click")
            
            elif gesture == Gesture.DRAG_START:
                if not self.is_dragging:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    print("✊ Drag Start")
            
            elif gesture == Gesture.DRAG_END:
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                    print("✋ Drag End")
            
            elif gesture == Gesture.SCROLL:
                # Scroll will be handled with velocity
                pass
            
            elif gesture == Gesture.ZOOM_IN:
                pyautogui.hotkey(self.mod_key, 'plus')
                print("🔍 Zoom In")
            
            elif gesture == Gesture.ZOOM_OUT:
                pyautogui.hotkey(self.mod_key, 'minus')
                print("🔍 Zoom Out")
            
            elif gesture == Gesture.ROTATE_CW:
                print("🔄 Rotate Clockwise")
                # App-specific rotation
            
            elif gesture == Gesture.ROTATE_CCW:
                print("🔄 Rotate Counter-Clockwise")
                # App-specific rotation
            
            elif gesture == Gesture.PAUSE:
                pyautogui.press('space')
                print("⏸️  Pause/Play")
            
            elif gesture == Gesture.CONFIRM:
                pyautogui.press('enter')
                print("✅ Confirm (Enter)")
            
            elif gesture == Gesture.CANCEL:
                pyautogui.press('escape')
                print("❌ Cancel (Escape)")
        
        except Exception as e:
            print(f"⚠️  Action error: {e}")
    
    def scroll(self, velocity: float):
        """Execute scroll with velocity
        
        Args:
            velocity: Vertical velocity (negative = up, positive = down)
        """
        try:
            # Convert velocity to scroll amount
            scroll_amount = int(-velocity * 2)  # Scale and invert
            
            if abs(scroll_amount) > 0:
                pyautogui.scroll(scroll_amount)
        
        except Exception as e:
            print(f"⚠️  Scroll error: {e}")
    
    def _move_cursor(self, position: Tuple[int, int]):
        """Move cursor with smoothing
        
        Args:
            position: Target cursor position
        """
        self.cursor_history.append(position)
        
        # Average recent positions for smoothing
        if len(self.cursor_history) > 0:
            avg_x = sum(p[0] for p in self.cursor_history) // len(self.cursor_history)
            avg_y = sum(p[1] for p in self.cursor_history) // len(self.cursor_history)
            
            pyautogui.moveTo(avg_x, avg_y)
    
    def reset(self):
        """Reset executor state"""
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
        
        self.cursor_history.clear()

