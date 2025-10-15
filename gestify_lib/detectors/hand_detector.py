"""
Hand detection using MediaPipe
"""

import mediapipe as mp
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Hand:
    """Represents a detected hand with landmarks"""
    landmarks: any  # MediaPipe landmarks
    handedness: str  # 'Left' or 'Right'
    confidence: float
    
    def get_landmark(self, index: int) -> Tuple[float, float, float]:
        """Get landmark coordinates (x, y, z)"""
        lm = self.landmarks.landmark[index]
        return (lm.x, lm.y, lm.z)
    
    def get_landmark_px(self, index: int, width: int, height: int) -> Tuple[int, int]:
        """Get landmark in pixel coordinates"""
        lm = self.landmarks.landmark[index]
        return (int(lm.x * width), int(lm.y * height))


class HandDetector:
    """Hand detection and tracking using MediaPipe"""
    
    # Landmark indices
    WRIST = 0
    THUMB_TIP = 4
    THUMB_IP = 3
    INDEX_TIP = 8
    INDEX_PIP = 6
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10
    RING_TIP = 16
    RING_PIP = 14
    PINKY_TIP = 20
    PINKY_PIP = 18
    
    def __init__(self, 
                 max_hands: int = 2,
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.5,
                 model_complexity: int = 0):
        """Initialize hand detector
        
        Args:
            max_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
            model_complexity: Model complexity (0=lite, 1=full)
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect(self, frame: np.ndarray) -> Optional[List[Hand]]:
        """Detect hands in frame
        
        Args:
            frame: RGB image frame
            
        Returns:
            List of detected hands or None
        """
        results = self.hands.process(frame)
        
        if not results.multi_hand_landmarks:
            return None
        
        hands = []
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[i].classification[0].label
            confidence = results.multi_handedness[i].classification[0].score
            
            hands.append(Hand(
                landmarks=hand_landmarks,
                handedness=handedness,
                confidence=confidence
            ))
        
        return hands
    
    def draw_landmarks(self, frame: np.ndarray, hands: List[Hand]):
        """Draw hand landmarks on frame
        
        Args:
            frame: Image frame to draw on
            hands: List of hands to draw
        """
        for hand in hands:
            self.mp_drawing.draw_landmarks(
                frame,
                hand.landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def is_finger_extended(self, hand: Hand, 
                          tip_idx: int, pip_idx: int,
                          threshold: float = 1.15) -> bool:
        """Check if finger is extended
        
        Args:
            hand: Hand object
            tip_idx: Index of finger tip landmark
            pip_idx: Index of finger PIP joint landmark
            threshold: Extension threshold multiplier
            
        Returns:
            True if finger is extended
        """
        wrist = hand.get_landmark(self.WRIST)
        tip = hand.get_landmark(tip_idx)
        pip = hand.get_landmark(pip_idx)
        
        tip_dist = self.calculate_distance((tip[0], tip[1]), (wrist[0], wrist[1]))
        pip_dist = self.calculate_distance((pip[0], pip[1]), (wrist[0], wrist[1]))
        
        return tip_dist > pip_dist * threshold
    
    def close(self):
        """Release resources"""
        self.hands.close()

