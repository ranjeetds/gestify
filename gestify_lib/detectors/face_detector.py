"""
Face and attention detection using MediaPipe Face Mesh
"""

import mediapipe as mp
import numpy as np
from typing import Optional, Tuple
from collections import deque


class FaceDetector:
    """Face detection and landmark tracking"""
    
    def __init__(self,
                 max_faces: int = 1,
                 refine_landmarks: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """Initialize face detector
        
        Args:
            max_faces: Maximum number of faces to detect
            refine_landmarks: Use refined landmarks (includes iris)
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=max_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect(self, frame: np.ndarray):
        """Detect face in frame
        
        Args:
            frame: RGB image frame
            
        Returns:
            Face landmarks or None
        """
        results = self.face_mesh.process(frame)
        
        if not results.multi_face_landmarks:
            return None
        
        return results.multi_face_landmarks[0]
    
    def draw_landmarks(self, frame: np.ndarray, face_landmarks, 
                      draw_irises: bool = True):
        """Draw face landmarks on frame
        
        Args:
            frame: Image frame to draw on
            face_landmarks: Face landmarks to draw
            draw_irises: Whether to draw iris landmarks
        """
        if draw_irises:
            self.mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                self.mp_face.FACEMESH_IRISES,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
            )
    
    def close(self):
        """Release resources"""
        self.face_mesh.close()


class AttentionTracker:
    """Track user attention using eye gaze estimation"""
    
    # Key facial landmark indices
    LEFT_EYE_CENTER = 33
    LEFT_IRIS = 468
    RIGHT_EYE_CENTER = 263
    RIGHT_IRIS = 473
    NOSE_TIP = 1
    LEFT_FACE = 234
    RIGHT_FACE = 454
    
    def __init__(self, 
                 buffer_size: int = 10,
                 attention_threshold: int = 3):
        """Initialize attention tracker
        
        Args:
            buffer_size: Size of attention history buffer
            attention_threshold: Minimum "looking" frames for confirmation
        """
        self.attention_history = deque(maxlen=buffer_size)
        self.attention_threshold = attention_threshold
    
    def check_attention(self, face_landmarks) -> bool:
        """Check if user is looking at screen
        
        Uses eye gaze estimation to determine if user is paying attention.
        
        Args:
            face_landmarks: MediaPipe face landmarks
            
        Returns:
            True if user is looking at screen
        """
        if not face_landmarks:
            return False
        
        try:
            landmarks = face_landmarks.landmark
            
            # Get eye and iris positions
            left_eye_center = landmarks[self.LEFT_EYE_CENTER]
            left_iris = landmarks[self.LEFT_IRIS]
            right_eye_center = landmarks[self.RIGHT_EYE_CENTER]
            right_iris = landmarks[self.RIGHT_IRIS]
            
            # Calculate gaze direction
            left_gaze_x = left_iris.x - left_eye_center.x
            right_gaze_x = right_iris.x - right_eye_center.x
            avg_gaze_x = (left_gaze_x + right_gaze_x) / 2
            
            left_gaze_y = left_iris.y - left_eye_center.y
            right_gaze_y = right_iris.y - right_eye_center.y
            avg_gaze_y = (left_gaze_y + right_gaze_y) / 2
            
            # Check if looking forward and slightly down (at screen)
            looking_forward = abs(avg_gaze_x) < 0.015
            looking_at_screen = -0.005 < avg_gaze_y < 0.020
            
            # Check head pose
            nose_tip = landmarks[self.NOSE_TIP]
            left_face = landmarks[self.LEFT_FACE]
            right_face = landmarks[self.RIGHT_FACE]
            
            # Face should be centered
            face_center_ok = 0.3 < nose_tip.x < 0.7
            
            # Face should be facing camera
            face_width = abs(right_face.x - left_face.x)
            face_angle_ok = face_width > 0.15
            
            return (looking_forward and looking_at_screen and 
                   face_center_ok and face_angle_ok)
            
        except Exception:
            return False
    
    def update_attention(self, is_looking: bool) -> bool:
        """Update attention state with smoothing
        
        Args:
            is_looking: Current frame attention state
            
        Returns:
            Smoothed attention state
        """
        self.attention_history.append(is_looking)
        
        if len(self.attention_history) < self.attention_threshold:
            return False
        
        # Majority voting for smooth transition
        attention_count = sum(self.attention_history)
        return attention_count >= self.attention_threshold
    
    def reset(self):
        """Reset attention history"""
        self.attention_history.clear()

