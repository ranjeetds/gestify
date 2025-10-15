"""
Game objects for AR interactions
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ObjectShape(Enum):
    """Available object shapes"""
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    STAR = "star"
    HEART = "heart"


@dataclass
class GameObject:
    """Base class for interactive game objects"""
    x: int
    y: int
    width: int
    height: int
    color: Tuple[int, int, int]
    shape: ObjectShape
    is_picked: bool = False
    z_index: int = 0  # For layering
    
    def contains_point(self, px: int, py: int) -> bool:
        """Check if point is within object bounds"""
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def get_center(self) -> Tuple[int, int]:
        """Get center point of object"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def move_to(self, x: int, y: int):
        """Move object to new position (centered)"""
        self.x = x - self.width // 2
        self.y = y - self.height // 2
    
    def draw(self, frame: np.ndarray, alpha: float = 1.0):
        """Draw object on frame
        
        Args:
            frame: Frame to draw on
            alpha: Transparency (0.0 to 1.0)
        """
        # Create overlay for transparency
        overlay = frame.copy()
        
        center = self.get_center()
        
        if self.shape == ObjectShape.CIRCLE:
            cv2.circle(overlay, center, self.width // 2, self.color, -1)
            # Add border
            cv2.circle(overlay, center, self.width // 2, (0, 0, 0), 2)
            
        elif self.shape == ObjectShape.SQUARE:
            cv2.rectangle(overlay, 
                         (self.x, self.y), 
                         (self.x + self.width, self.y + self.height),
                         self.color, -1)
            cv2.rectangle(overlay, 
                         (self.x, self.y), 
                         (self.x + self.width, self.y + self.height),
                         (0, 0, 0), 2)
            
        elif self.shape == ObjectShape.TRIANGLE:
            points = np.array([
                [center[0], self.y],  # Top
                [self.x, self.y + self.height],  # Bottom left
                [self.x + self.width, self.y + self.height],  # Bottom right
            ], np.int32)
            cv2.fillPoly(overlay, [points], self.color)
            cv2.polylines(overlay, [points], True, (0, 0, 0), 2)
            
        elif self.shape == ObjectShape.STAR:
            self._draw_star(overlay, center, self.width // 2, self.color)
            
        elif self.shape == ObjectShape.HEART:
            self._draw_heart(overlay, center, self.width // 2, self.color)
        
        # Blend with alpha
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    def _draw_star(self, frame: np.ndarray, center: Tuple[int, int], 
                   radius: int, color: Tuple[int, int, int]):
        """Draw a 5-pointed star"""
        points = []
        for i in range(10):
            angle = np.pi / 2 + i * 2 * np.pi / 10
            r = radius if i % 2 == 0 else radius // 2
            x = int(center[0] + r * np.cos(angle))
            y = int(center[1] - r * np.sin(angle))
            points.append([x, y])
        
        points = np.array(points, np.int32)
        cv2.fillPoly(frame, [points], color)
        cv2.polylines(frame, [points], True, (0, 0, 0), 2)
    
    def _draw_heart(self, frame: np.ndarray, center: Tuple[int, int], 
                    radius: int, color: Tuple[int, int, int]):
        """Draw a heart shape"""
        # Simplified heart using two circles and a triangle
        r = radius // 2
        
        # Top left circle
        cv2.circle(frame, (center[0] - r//2, center[1] - r//2), r, color, -1)
        # Top right circle
        cv2.circle(frame, (center[0] + r//2, center[1] - r//2), r, color, -1)
        # Bottom triangle
        points = np.array([
            [center[0] - radius, center[1] - r//2],
            [center[0] + radius, center[1] - r//2],
            [center[0], center[1] + radius],
        ], np.int32)
        cv2.fillPoly(frame, [points], color)
        
        # Border (simplified)
        cv2.circle(frame, (center[0] - r//2, center[1] - r//2), r, (0, 0, 0), 2)
        cv2.circle(frame, (center[0] + r//2, center[1] - r//2), r, (0, 0, 0), 2)


class PuzzlePiece(GameObject):
    """A puzzle piece that can be picked and placed"""
    
    def __init__(self, x: int, y: int, size: int, 
                 shape: ObjectShape, color: Tuple[int, int, int],
                 piece_id: int):
        super().__init__(x, y, size, size, color, shape)
        self.piece_id = piece_id
        self.is_placed_correctly = False
        self.original_pos = (x, y)
    
    def draw(self, frame: np.ndarray, alpha: float = 1.0):
        """Draw puzzle piece with special effects"""
        # Glow effect when picked
        if self.is_picked:
            glow_size = 10
            glow_overlay = frame.copy()
            center = self.get_center()
            cv2.circle(glow_overlay, center, 
                      self.width // 2 + glow_size, 
                      (255, 255, 255), -1)
            cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0, frame)
        
        # Green check mark if placed correctly
        if self.is_placed_correctly:
            super().draw(frame, alpha)
            center = self.get_center()
            cv2.putText(frame, "✓", 
                       (center[0] - 15, center[1] + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        else:
            super().draw(frame, alpha)


class TargetZone(GameObject):
    """A target zone where puzzle pieces should be placed"""
    
    def __init__(self, x: int, y: int, size: int, 
                 shape: ObjectShape, required_piece_id: int):
        # Target zones are semi-transparent outlines
        super().__init__(x, y, size, size, (200, 200, 200), shape)
        self.required_piece_id = required_piece_id
        self.is_filled = False
    
    def draw(self, frame: np.ndarray, alpha: float = 0.3):
        """Draw target zone as outline"""
        overlay = frame.copy()
        center = self.get_center()
        
        # Draw outline based on shape
        if self.shape == ObjectShape.CIRCLE:
            cv2.circle(overlay, center, self.width // 2, self.color, 3)
            
        elif self.shape == ObjectShape.SQUARE:
            cv2.rectangle(overlay, 
                         (self.x, self.y), 
                         (self.x + self.width, self.y + self.height),
                         self.color, 3)
            
        elif self.shape == ObjectShape.TRIANGLE:
            points = np.array([
                [center[0], self.y],
                [self.x, self.y + self.height],
                [self.x + self.width, self.y + self.height],
            ], np.int32)
            cv2.polylines(overlay, [points], True, self.color, 3)
            
        elif self.shape == ObjectShape.STAR:
            points = []
            for i in range(10):
                angle = np.pi / 2 + i * 2 * np.pi / 10
                r = self.width // 2 if i % 2 == 0 else self.width // 4
                x = int(center[0] + r * np.cos(angle))
                y = int(center[1] - r * np.sin(angle))
                points.append([x, y])
            points = np.array(points, np.int32)
            cv2.polylines(overlay, [points], True, self.color, 3)
            
        elif self.shape == ObjectShape.HEART:
            # Draw heart outline (simplified)
            r = self.width // 4
            cv2.circle(overlay, (center[0] - r//2, center[1] - r//2), r, self.color, 2)
            cv2.circle(overlay, (center[0] + r//2, center[1] - r//2), r, self.color, 2)
        
        # Add dashed effect for empty zones
        if not self.is_filled:
            # Add pulsing effect
            pulse_alpha = 0.2 + 0.1 * np.sin(cv2.getTickCount() / 1000.0)
            alpha = pulse_alpha
        
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Label with shape icon
        cv2.putText(frame, f"{self.shape.value}", 
                   (self.x, self.y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

