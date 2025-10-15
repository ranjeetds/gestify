"""
Gestify - AI-Powered Hand Gesture Control Library
==================================================

A professional, object-oriented library for hand gesture recognition and control.

Features:
- Simplified, distinct gestures (no confusion)
- Two-hand gesture support
- Face and eye tracking for attention detection
- Prevents unintentional actions
- Easy-to-use API

Usage:
    from gestify_lib import GestifyController
    
    controller = GestifyController()
    controller.run()

Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Gestify Contributors"
__license__ = "MIT"

from .core.controller import GestifyController
from .core.config import GestifyConfig
from .detectors.hand_detector import HandDetector
from .detectors.face_detector import FaceDetector, AttentionTracker
from .detectors.gesture_recognizer import GestureRecognizer

__all__ = [
    'GestifyController',
    'GestifyConfig',
    'HandDetector',
    'FaceDetector',
    'AttentionTracker',
    'GestureRecognizer',
]

