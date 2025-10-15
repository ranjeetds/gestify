"""
Configuration management for Gestify
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class GestifyConfig:
    """Configuration for Gestify controller
    
    Attributes:
        camera_index: Camera device index (0 for default)
        camera_width: Camera capture width
        camera_height: Camera capture height
        camera_fps: Target FPS for camera
        
        max_hands: Maximum number of hands to detect (1 or 2)
        hand_confidence: Minimum confidence for hand detection (0-1)
        hand_tracking_confidence: Minimum confidence for hand tracking (0-1)
        
        enable_face_tracking: Enable face and attention tracking
        face_confidence: Minimum confidence for face detection (0-1)
        attention_threshold: Number of frames needed for attention confirmation
        
        gesture_cooldown: Minimum seconds between gesture actions
        cursor_smoothing: Number of frames for cursor smoothing (1-10)
        
        enable_two_hand: Enable two-hand gestures
        pinch_threshold: Distance threshold for pinch detection (pixels)
        
        show_ui: Show camera window with overlays
        show_debug: Show debug information
    """
    
    # Camera settings
    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    
    # Hand detection
    max_hands: int = 2
    hand_confidence: float = 0.7
    hand_tracking_confidence: float = 0.5
    hand_model_complexity: int = 0  # 0=lite, 1=full
    
    # Face tracking
    enable_face_tracking: bool = True
    face_confidence: float = 0.5
    face_tracking_confidence: float = 0.5
    attention_threshold: int = 3  # frames
    attention_buffer_size: int = 10
    
    # Gesture settings
    gesture_cooldown: float = 0.25
    cursor_smoothing: int = 5
    
    # Two-hand gestures
    enable_two_hand: bool = True
    pinch_threshold: int = 20  # pixels
    two_hand_distance_threshold: int = 50  # pixels
    
    # UI settings
    show_ui: bool = True
    show_debug: bool = False
    show_fps: bool = True
    
    # Performance
    enable_gpu: bool = True
    
    # Gesture thresholds
    finger_extension_threshold: float = 1.15
    thumb_angle_threshold: float = 0.15
    scroll_sensitivity: float = 250.0
    
    def __post_init__(self):
        """Validate configuration"""
        if self.max_hands not in [1, 2]:
            raise ValueError("max_hands must be 1 or 2")
        
        if not 0 <= self.hand_confidence <= 1:
            raise ValueError("hand_confidence must be between 0 and 1")
        
        if not 0 <= self.face_confidence <= 1:
            raise ValueError("face_confidence must be between 0 and 1")
        
        if self.cursor_smoothing < 1:
            raise ValueError("cursor_smoothing must be >= 1")
    
    @classmethod
    def fast_mode(cls) -> 'GestifyConfig':
        """Configuration optimized for speed"""
        return cls(
            hand_model_complexity=0,
            max_hands=1,
            enable_face_tracking=False,
            cursor_smoothing=3,
        )
    
    @classmethod
    def accurate_mode(cls) -> 'GestifyConfig':
        """Configuration optimized for accuracy"""
        return cls(
            hand_model_complexity=1,
            hand_confidence=0.8,
            face_confidence=0.7,
            cursor_smoothing=7,
            attention_threshold=5,
        )
    
    @classmethod
    def two_hand_mode(cls) -> 'GestifyConfig':
        """Configuration optimized for two-hand gestures"""
        return cls(
            max_hands=2,
            enable_two_hand=True,
            enable_face_tracking=True,
        )

