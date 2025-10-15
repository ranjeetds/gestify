"""
Puzzle game logic with pick and place mechanics
"""

import cv2
import numpy as np
import random
import time
from typing import List, Optional, Tuple

from .game_objects import PuzzlePiece, TargetZone, ObjectShape


class PuzzleGame:
    """Simple shape-matching puzzle game"""
    
    def __init__(self, width: int, height: int, difficulty: str = "easy"):
        """Initialize puzzle game
        
        Args:
            width: Game area width
            height: Game area height
            difficulty: Game difficulty (easy, medium, hard)
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        
        # Game state
        self.pieces: List[PuzzlePiece] = []
        self.target_zones: List[TargetZone] = []
        self.picked_piece: Optional[PuzzlePiece] = None
        self.cursor_pos: Optional[Tuple[int, int]] = None
        
        # Scoring
        self.score = 0
        self.moves = 0
        self.start_time = time.time()
        self.is_completed = False
        
        # Visual effects
        self.particles: List[dict] = []
        
        # Initialize game
        self._setup_puzzle()
    
    def _setup_puzzle(self):
        """Set up puzzle pieces and target zones"""
        # Determine number of pieces based on difficulty
        num_pieces = {
            "easy": 3,
            "medium": 4,
            "hard": 5
        }.get(self.difficulty, 3)
        
        # Available shapes and colors
        shapes = [ObjectShape.CIRCLE, ObjectShape.SQUARE, ObjectShape.TRIANGLE, 
                 ObjectShape.STAR, ObjectShape.HEART]
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
        ]
        
        # Select random shapes for this puzzle
        selected_shapes = random.sample(shapes, min(num_pieces, len(shapes)))
        
        # Piece size
        piece_size = 80
        
        # Create target zones in the right half of screen
        target_start_x = self.width * 2 // 3
        target_spacing = self.height // (num_pieces + 1)
        
        for i, shape in enumerate(selected_shapes):
            # Create target zone
            zone_x = target_start_x
            zone_y = target_spacing * (i + 1) - piece_size // 2
            target = TargetZone(zone_x, zone_y, piece_size, shape, i)
            self.target_zones.append(target)
            
            # Create puzzle piece in random position on left side
            piece_x = random.randint(50, self.width // 3 - piece_size)
            piece_y = random.randint(100, self.height - piece_size - 100)
            color = colors[i % len(colors)]
            
            piece = PuzzlePiece(piece_x, piece_y, piece_size, shape, color, i)
            self.pieces.append(piece)
        
        print(f"🎮 Puzzle created with {num_pieces} pieces!")
    
    def update(self, cursor_pos: Optional[Tuple[int, int]], 
               is_picking: bool, is_releasing: bool, is_holding: bool = False) -> bool:
        """Update game state
        
        Args:
            cursor_pos: Current cursor position (x, y)
            is_picking: Whether user just started picking (edge trigger)
            is_releasing: Whether user just released (edge trigger)
            is_holding: Whether user is continuously holding (level trigger)
            
        Returns:
            True if game state changed
        """
        self.cursor_pos = cursor_pos
        changed = False
        
        if cursor_pos is None:
            return False
        
        # Handle picking - only pick on initial trigger
        if is_picking and self.picked_piece is None:
            # Try to pick a piece at cursor
            for piece in sorted(self.pieces, key=lambda p: p.z_index, reverse=True):
                if piece.contains_point(cursor_pos[0], cursor_pos[1]) and not piece.is_placed_correctly:
                    self.picked_piece = piece
                    piece.is_picked = True
                    piece.z_index = 100  # Bring to front
                    self.moves += 1
                    changed = True
                    print(f"✋ Picked {piece.shape.value}")
                    break
        
        # Handle releasing - only release on release trigger
        if is_releasing and self.picked_piece is not None:
            piece = self.picked_piece
            piece.is_picked = False
            piece.z_index = 0
            
            # Check if placed in correct zone
            placed_correctly = False
            for zone in self.target_zones:
                if zone.required_piece_id == piece.piece_id:
                    # Check if piece is close to zone
                    piece_center = piece.get_center()
                    zone_center = zone.get_center()
                    distance = np.sqrt(
                        (piece_center[0] - zone_center[0])**2 + 
                        (piece_center[1] - zone_center[1])**2
                    )
                    
                    if distance < 100:  # Snap distance
                        # Snap to zone
                        piece.move_to(zone_center[0], zone_center[1])
                        piece.is_placed_correctly = True
                        zone.is_filled = True
                        self.score += 100
                        placed_correctly = True
                        
                        # Create celebration particles
                        self._create_particles(zone_center)
                        
                        print(f"✓ Correct placement! Score: {self.score}")
                        
                        # Check if puzzle complete
                        if all(p.is_placed_correctly for p in self.pieces):
                            self._complete_puzzle()
                        break
            
            if not placed_correctly:
                print(f"✗ Incorrect placement")
            
            self.picked_piece = None
            changed = True
        
        # Move picked piece with cursor while holding
        # This allows continuous drag while pinching
        if self.picked_piece is not None and cursor_pos is not None and (is_holding or is_picking):
            self.picked_piece.move_to(cursor_pos[0], cursor_pos[1])
            changed = True
        
        # Update particles
        self._update_particles()
        
        return changed
    
    def _complete_puzzle(self):
        """Handle puzzle completion"""
        self.is_completed = True
        elapsed = time.time() - self.start_time
        
        print(f"\n🎉 PUZZLE COMPLETED! 🎉")
        print(f"Score: {self.score}")
        print(f"Moves: {self.moves}")
        print(f"Time: {elapsed:.1f}s")
        
        # Bonus for efficiency
        if self.moves == len(self.pieces):
            self.score += 500
            print("🌟 PERFECT! +500 bonus")
    
    def _create_particles(self, position: Tuple[int, int]):
        """Create celebration particles at position"""
        for _ in range(20):
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': position[0],
                'y': position[1],
                'vx': speed * np.cos(angle),
                'vy': speed * np.sin(angle),
                'life': 1.0,
                'color': (random.randint(100, 255), 
                         random.randint(100, 255), 
                         random.randint(100, 255))
            })
    
    def _update_particles(self):
        """Update particle effects"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['life'] -= 0.02
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, frame: np.ndarray):
        """Draw game on frame
        
        Args:
            frame: Frame to draw on
        """
        # Draw semi-transparent game area background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw target zones first (behind pieces)
        for zone in self.target_zones:
            zone.draw(frame)
        
        # Draw pieces (not picked ones first, then picked on top)
        for piece in sorted(self.pieces, key=lambda p: (p.is_picked, p.z_index)):
            alpha = 0.9 if not piece.is_picked else 0.7
            piece.draw(frame, alpha)
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                size = int(5 * particle['life'])
                pos = (int(particle['x']), int(particle['y']))
                cv2.circle(frame, pos, size, particle['color'], -1)
        
        # Draw cursor highlight if hovering over piece
        if self.cursor_pos and self.picked_piece is None:
            for piece in self.pieces:
                if piece.contains_point(self.cursor_pos[0], self.cursor_pos[1]) and not piece.is_placed_correctly:
                    # Draw highlight
                    center = piece.get_center()
                    cv2.circle(frame, center, piece.width // 2 + 10, 
                             (255, 255, 255), 2)
        
        # Draw UI
        self._draw_ui(frame)
    
    def _draw_ui(self, frame: np.ndarray):
        """Draw game UI elements"""
        # Title
        cv2.putText(frame, "AR SHAPE PUZZLE", 
                   (20, 50),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)
        
        # Instructions (if not completed)
        if not self.is_completed:
            instructions = [
                "Move hand to control",
                "Pinch fingers to pick",
                "Hold pinch to drag",
                "Release to place!"
            ]
            y = 100
            for instruction in instructions:
                cv2.putText(frame, instruction, 
                           (20, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                y += 25
        
        # Score panel
        panel_x = self.width - 250
        panel_y = 20
        panel_w = 230
        panel_h = 150
        
        # Draw panel background
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_w, panel_y + panel_h),
                     (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Score info
        cv2.putText(frame, f"SCORE: {self.score}", 
                   (panel_x + 10, panel_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.putText(frame, f"Moves: {self.moves}", 
                   (panel_x + 10, panel_y + 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Time
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        cv2.putText(frame, f"Time: {minutes:02d}:{seconds:02d}", 
                   (panel_x + 10, panel_y + 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Progress
        completed = sum(1 for p in self.pieces if p.is_placed_correctly)
        total = len(self.pieces)
        cv2.putText(frame, f"Progress: {completed}/{total}", 
                   (panel_x + 10, panel_y + 125),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Completion message
        if self.is_completed:
            # Draw celebration overlay
            overlay = frame.copy()
            h, w = frame.shape[:2]
            cv2.rectangle(overlay, (w//4, h//4), (3*w//4, 3*h//4),
                         (0, 128, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            cv2.putText(frame, "PUZZLE COMPLETE!", 
                       (w//4 + 40, h//2 - 50),
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 4)
            
            cv2.putText(frame, f"Final Score: {self.score}", 
                       (w//4 + 80, h//2 + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
            
            cv2.putText(frame, "Press 'R' to restart", 
                       (w//4 + 80, h//2 + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
    
    def reset(self):
        """Reset game to start new puzzle"""
        self.pieces.clear()
        self.target_zones.clear()
        self.picked_piece = None
        self.cursor_pos = None
        self.score = 0
        self.moves = 0
        self.start_time = time.time()
        self.is_completed = False
        self.particles.clear()
        self._setup_puzzle()
        print("\n🔄 New puzzle started!")

