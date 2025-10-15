"""
Gesture recognition with simplified, distinct gestures
"""

import time
import numpy as np
from enum import Enum, auto
from typing import Optional, List, Tuple
from collections import deque
from dataclasses import dataclass

from .hand_detector import Hand, HandDetector


class Gesture(Enum):
    """Simplified gesture set - distinct and non-overlapping"""
    
    # Single hand gestures
    NONE = auto()
    CURSOR_MOVE = auto()          # Index finger pointing (only finger extended)
    CLICK = auto()                 # Quick thumb-index pinch
    DOUBLE_CLICK = auto()          # Two quick pinches
    SCROLL = auto()                # Fist moving up/down
    DRAG_START = auto()            # Peace sign (index + middle)
    DRAG_END = auto()              # From peace to fist
    
    # Two-hand gestures (requires both hands)
    ZOOM_IN = auto()               # Both hands moving apart
    ZOOM_OUT = auto()              # Both hands moving together
    ROTATE_CW = auto()             # Hands rotating clockwise
    ROTATE_CCW = auto()            # Hands rotating counter-clockwise
    
    # Control gestures
    PAUSE = auto()                 # Open palm (5 fingers extended)
    CONFIRM = auto()               # Thumbs up
    CANCEL = auto()                # Thumbs down


@dataclass
class HandState:
    """Current state of a hand"""
    hand: Hand
    position: Tuple[int, int]
    fingers_extended: List[bool]  # [thumb, index, middle, ring, pinky]
    is_fist: bool
    pinch_distance: float
    velocity: Tuple[float, float]


class GestureRecognizer:
    """Recognize gestures from hand landmarks"""
    
    def __init__(self, 
                 hand_detector: HandDetector,
                 cooldown: float = 0.25,
                 pinch_threshold: int = 20):
        """Initialize gesture recognizer
        
        Args:
            hand_detector: HandDetector instance
            cooldown: Minimum seconds between gestures
            pinch_threshold: Distance for pinch detection (pixels)
        """
        self.detector = hand_detector
        self.cooldown = cooldown
        self.pinch_threshold = pinch_threshold
        
        # State tracking
        self.last_gesture_time = 0
        self.last_gesture = Gesture.NONE
        self.is_dragging = False
        
        # Position history for velocity calculation
        self.position_history = deque(maxlen=5)
        self.left_hand_history = deque(maxlen=5)
        self.right_hand_history = deque(maxlen=5)
        
        # Two-hand state
        self.initial_hands_distance = None
        self.initial_hands_angle = None
        
        # Click detection
        self.click_times = deque(maxlen=3)
        self.last_pinch_state = False
        
    def can_trigger_gesture(self) -> bool:
        """Check if cooldown period has passed"""
        return (time.time() - self.last_gesture_time) >= self.cooldown
    
    def trigger_gesture(self, gesture: Gesture):
        """Mark gesture as triggered"""
        self.last_gesture = gesture
        self.last_gesture_time = time.time()
    
    def analyze_hand(self, hand: Hand, width: int, height: int) -> HandState:
        """Analyze hand state
        
        Args:
            hand: Hand object
            width: Frame width
            height: Frame height
            
        Returns:
            HandState object
        """
        # Get key landmarks
        wrist = hand.get_landmark_px(HandDetector.WRIST, width, height)
        thumb_tip = hand.get_landmark_px(HandDetector.THUMB_TIP, width, height)
        index_tip = hand.get_landmark_px(HandDetector.INDEX_TIP, width, height)
        middle_tip = hand.get_landmark_px(HandDetector.MIDDLE_TIP, width, height)
        
        # Check finger extension
        fingers_extended = [
            self._is_thumb_extended(hand),
            self.detector.is_finger_extended(hand, HandDetector.INDEX_TIP, HandDetector.INDEX_PIP),
            self.detector.is_finger_extended(hand, HandDetector.MIDDLE_TIP, HandDetector.MIDDLE_PIP),
            self.detector.is_finger_extended(hand, HandDetector.RING_TIP, HandDetector.RING_PIP),
            self.detector.is_finger_extended(hand, HandDetector.PINKY_TIP, HandDetector.PINKY_PIP),
        ]
        
        # Check if fist (no fingers extended)
        is_fist = not any(fingers_extended)
        
        # Calculate pinch distance
        pinch_distance = self.detector.calculate_distance(thumb_tip, index_tip)
        
        # Calculate velocity
        velocity = self._calculate_velocity(index_tip)
        
        return HandState(
            hand=hand,
            position=index_tip,
            fingers_extended=fingers_extended,
            is_fist=is_fist,
            pinch_distance=pinch_distance,
            velocity=velocity
        )
    
    def recognize(self, hands: Optional[List[Hand]], 
                  width: int, height: int,
                  user_looking: bool = True) -> Gesture:
        """Recognize gesture from hands
        
        Args:
            hands: List of detected hands
            width: Frame width
            height: Frame height
            user_looking: Whether user is looking at screen
            
        Returns:
            Recognized gesture
        """
        # No gesture if user not looking (prevents unintentional actions)
        if not user_looking:
            return Gesture.NONE
        
        # No hands detected
        if not hands or len(hands) == 0:
            self.is_dragging = False
            return Gesture.NONE
        
        # Single hand gestures
        if len(hands) == 1:
            hand_state = self.analyze_hand(hands[0], width, height)
            return self._recognize_single_hand(hand_state)
        
        # Two hand gestures
        elif len(hands) == 2:
            left_state = self.analyze_hand(hands[0], width, height)
            right_state = self.analyze_hand(hands[1], width, height)
            
            # Try two-hand gesture first
            two_hand_gesture = self._recognize_two_hands(left_state, right_state)
            if two_hand_gesture != Gesture.NONE:
                return two_hand_gesture
            
            # Fall back to single hand (use right hand or dominant)
            return self._recognize_single_hand(right_state)
        
        return Gesture.NONE
    
    def _recognize_single_hand(self, state: HandState) -> Gesture:
        """Recognize single-hand gesture
        
        Args:
            state: Hand state
            
        Returns:
            Recognized gesture
        """
        fingers = state.fingers_extended
        
        # CURSOR_MOVE: Only index finger extended
        if fingers == [False, True, False, False, False]:
            return Gesture.CURSOR_MOVE
        
        # DRAG: Peace sign (index + middle, no thumb)
        if fingers == [False, True, True, False, False]:
            if not self.is_dragging:
                self.is_dragging = True
                if self.can_trigger_gesture():
                    self.trigger_gesture(Gesture.DRAG_START)
                    return Gesture.DRAG_START
            # Continue dragging
            return Gesture.CURSOR_MOVE
        
        # DRAG_END: Was dragging, now changed gesture
        if self.is_dragging and fingers != [False, True, True, False, False]:
            self.is_dragging = False
            if self.can_trigger_gesture():
                self.trigger_gesture(Gesture.DRAG_END)
                return Gesture.DRAG_END
        
        # PAUSE: Open palm (all 5 fingers)
        if all(fingers):
            if self.can_trigger_gesture():
                self.trigger_gesture(Gesture.PAUSE)
                return Gesture.PAUSE
        
        # CONFIRM: Thumbs up (only thumb extended)
        if fingers == [True, False, False, False, False]:
            # Check thumb pointing up
            if self.can_trigger_gesture():
                self.trigger_gesture(Gesture.CONFIRM)
                return Gesture.CONFIRM
        
        # CANCEL: Thumbs down (only thumb extended but pointing down)
        # This is tricky - we need to check thumb orientation
        # For now, use fist with thumb out pointing to side
        if fingers[0] and not any(fingers[1:]):
            thumb_y = state.hand.get_landmark(HandDetector.THUMB_TIP)[1]
            wrist_y = state.hand.get_landmark(HandDetector.WRIST)[1]
            if thumb_y > wrist_y:  # Thumb below wrist
                if self.can_trigger_gesture():
                    self.trigger_gesture(Gesture.CANCEL)
                    return Gesture.CANCEL
        
        # CLICK: Pinch detection
        is_pinching = state.pinch_distance < self.pinch_threshold
        
        # Detect pinch edge (transition from not pinching to pinching)
        if is_pinching and not self.last_pinch_state:
            now = time.time()
            self.click_times.append(now)
            
            # Check for double click (two clicks within 0.5 seconds)
            if len(self.click_times) >= 2:
                if (self.click_times[-1] - self.click_times[-2]) < 0.5:
                    self.click_times.clear()
                    if self.can_trigger_gesture():
                        self.trigger_gesture(Gesture.DOUBLE_CLICK)
                        self.last_pinch_state = is_pinching
                        return Gesture.DOUBLE_CLICK
            
            # Single click
            if self.can_trigger_gesture():
                self.trigger_gesture(Gesture.CLICK)
                self.last_pinch_state = is_pinching
                return Gesture.CLICK
        
        self.last_pinch_state = is_pinching
        
        # SCROLL: Fist moving up/down
        if state.is_fist:
            # Check significant vertical movement
            if abs(state.velocity[1]) > 5:  # pixels per frame
                return Gesture.SCROLL
        
        return Gesture.NONE
    
    def _recognize_two_hands(self, left: HandState, right: HandState) -> Gesture:
        """Recognize two-hand gesture
        
        Args:
            left: Left hand state
            right: Right hand state
            
        Returns:
            Recognized gesture or NONE
        """
        # Both hands should have index fingers extended for zoom/rotate
        if not (left.fingers_extended[1] and right.fingers_extended[1]):
            self.initial_hands_distance = None
            self.initial_hands_angle = None
            return Gesture.NONE
        
        # Calculate distance between index fingers
        current_distance = self.detector.calculate_distance(
            left.position, right.position
        )
        
        # Calculate angle between hands
        current_angle = np.arctan2(
            right.position[1] - left.position[1],
            right.position[0] - left.position[0]
        )
        
        # Initialize baseline
        if self.initial_hands_distance is None:
            self.initial_hands_distance = current_distance
            self.initial_hands_angle = current_angle
            return Gesture.NONE
        
        # Check for zoom (distance change)
        distance_change = current_distance - self.initial_hands_distance
        
        if abs(distance_change) > 50:  # Significant distance change
            if distance_change > 0:
                # Moving apart - zoom in
                if self.can_trigger_gesture():
                    self.trigger_gesture(Gesture.ZOOM_IN)
                    self.initial_hands_distance = current_distance
                    return Gesture.ZOOM_IN
            else:
                # Moving together - zoom out
                if self.can_trigger_gesture():
                    self.trigger_gesture(Gesture.ZOOM_OUT)
                    self.initial_hands_distance = current_distance
                    return Gesture.ZOOM_OUT
        
        # Check for rotation (angle change)
        angle_change = current_angle - self.initial_hands_angle
        
        # Normalize angle to [-pi, pi]
        while angle_change > np.pi:
            angle_change -= 2 * np.pi
        while angle_change < -np.pi:
            angle_change += 2 * np.pi
        
        if abs(angle_change) > 0.3:  # ~17 degrees
            if angle_change > 0:
                # Counter-clockwise
                if self.can_trigger_gesture():
                    self.trigger_gesture(Gesture.ROTATE_CCW)
                    self.initial_hands_angle = current_angle
                    return Gesture.ROTATE_CCW
            else:
                # Clockwise
                if self.can_trigger_gesture():
                    self.trigger_gesture(Gesture.ROTATE_CW)
                    self.initial_hands_angle = current_angle
                    return Gesture.ROTATE_CW
        
        return Gesture.NONE
    
    def _is_thumb_extended(self, hand: Hand) -> bool:
        """Check if thumb is extended
        
        Thumb extension is measured differently than other fingers
        """
        thumb_tip = hand.get_landmark(HandDetector.THUMB_TIP)
        thumb_ip = hand.get_landmark(HandDetector.THUMB_IP)
        wrist = hand.get_landmark(HandDetector.WRIST)
        
        # Distance from thumb tip to wrist
        tip_to_wrist = self.detector.calculate_distance(
            (thumb_tip[0], thumb_tip[1]),
            (wrist[0], wrist[1])
        )
        
        # Distance from thumb IP to wrist
        ip_to_wrist = self.detector.calculate_distance(
            (thumb_ip[0], thumb_ip[1]),
            (wrist[0], wrist[1])
        )
        
        return tip_to_wrist > ip_to_wrist * 1.2
    
    def _calculate_velocity(self, position: Tuple[int, int]) -> Tuple[float, float]:
        """Calculate velocity from position history
        
        Args:
            position: Current position
            
        Returns:
            (vx, vy) velocity in pixels per frame
        """
        self.position_history.append(position)
        
        if len(self.position_history) < 2:
            return (0.0, 0.0)
        
        # Average velocity over last frames
        vx = self.position_history[-1][0] - self.position_history[0][0]
        vy = self.position_history[-1][1] - self.position_history[0][1]
        
        frames = len(self.position_history) - 1
        return (vx / frames, vy / frames)
    
    def get_cursor_position(self, state: HandState, 
                           screen_width: int, screen_height: int,
                           frame_width: int, frame_height: int) -> Tuple[int, int]:
        """Convert hand position to screen coordinates
        
        Args:
            state: Hand state
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            frame_width: Camera frame width
            frame_height: Camera frame height
            
        Returns:
            (x, y) screen coordinates
        """
        # Map from camera space to screen space
        # Flip X for mirror effect
        x = int((1 - state.position[0] / frame_width) * screen_width)
        y = int((state.position[1] / frame_height) * screen_height)
        
        # Clamp to screen bounds
        x = max(0, min(x, screen_width - 1))
        y = max(0, min(y, screen_height - 1))
        
        return (x, y)
    
    def reset(self):
        """Reset gesture state"""
        self.last_gesture = Gesture.NONE
        self.is_dragging = False
        self.position_history.clear()
        self.click_times.clear()
        self.initial_hands_distance = None
        self.initial_hands_angle = None

