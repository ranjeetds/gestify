"""
AR Ping Pong Game - Two player hand-controlled game
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple
import random


class Ball:
    """Ping pong ball"""
    
    def __init__(self, x: int, y: int, radius: int = 15):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = random.choice([-8, 8])  # Horizontal velocity
        self.vy = random.choice([-5, -3, 3, 5])  # Vertical velocity
        self.speed_multiplier = 1.0
        self.trail = []  # For visual effect
        
    def update(self, width: int, height: int) -> bool:
        """Update ball position
        
        Returns:
            True if ball went out of bounds (left or right)
        """
        # Update position
        self.x += int(self.vx * self.speed_multiplier)
        self.y += int(self.vy * self.speed_multiplier)
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Bounce off top and bottom
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy)  # Bounce down
        elif self.y + self.radius >= height:
            self.y = height - self.radius
            self.vy = -abs(self.vy)  # Bounce up
        
        # Check if out of bounds (left or right)
        if self.x - self.radius < 0 or self.x + self.radius > width:
            return True  # Ball went out
        
        return False
    
    def bounce_off_paddle(self, paddle_y: int, paddle_height: int, paddle_side: str):
        """Bounce ball off paddle
        
        Args:
            paddle_y: Paddle center Y position
            paddle_height: Paddle height
            paddle_side: 'left' or 'right'
        """
        # Reverse horizontal direction
        self.vx = -self.vx
        
        # Calculate hit position (relative to paddle center)
        hit_pos = (self.y - paddle_y) / (paddle_height / 2)  # -1 to 1
        
        # Adjust vertical velocity based on where ball hit paddle
        self.vy = int(hit_pos * 10)  # More angle if hit near edges
        
        # Increase speed slightly
        self.speed_multiplier = min(self.speed_multiplier + 0.1, 2.0)
        
        # Move ball away from paddle to prevent sticking
        if paddle_side == 'left':
            self.x = max(self.x, 50 + self.radius)
        else:
            self.x = min(self.x, 1920 - 50 - self.radius)
    
    def reset(self, x: int, y: int):
        """Reset ball to center"""
        self.x = x
        self.y = y
        self.vx = random.choice([-8, 8])
        self.vy = random.choice([-5, -3, 3, 5])
        self.speed_multiplier = 1.0
        self.trail.clear()
    
    def draw(self, frame: np.ndarray):
        """Draw ball on frame"""
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            size = int(self.radius * alpha * 0.5)
            cv2.circle(frame, pos, size, (100, 100, 100), -1)
        
        # Draw ball
        cv2.circle(frame, (self.x, self.y), self.radius, (255, 255, 0), -1)
        cv2.circle(frame, (self.x, self.y), self.radius, (255, 255, 255), 2)


class Paddle:
    """Player paddle"""
    
    def __init__(self, x: int, width: int, height: int, side: str):
        self.x = x
        self.width = width
        self.height = height
        self.y = 540  # Center Y
        self.side = side
        self.color = (0, 255, 0) if side == 'left' else (0, 0, 255)
        
    def update_position(self, hand_y: int):
        """Update paddle Y position based on hand with smoothing"""
        # Apply stronger smoothing for stable paddle control
        target_y = hand_y
        # 80% previous + 20% new for very smooth movement
        self.y = int(self.y * 0.8 + target_y * 0.2)
        
        # Clamp to screen bounds
        self.y = max(self.height // 2, min(self.y, 1080 - self.height // 2))
    
    def get_rect(self) -> Tuple[int, int, int, int]:
        """Get paddle rectangle (x, y, width, height)"""
        return (
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def check_collision(self, ball: Ball) -> bool:
        """Check if ball collides with paddle"""
        px, py, pw, ph = self.get_rect()
        
        # Check if ball is in paddle's X range
        if self.side == 'left':
            in_x_range = ball.x - ball.radius <= px + pw and ball.x + ball.radius >= px
        else:
            in_x_range = ball.x + ball.radius >= px and ball.x - ball.radius <= px + pw
        
        # Check if ball is in paddle's Y range
        in_y_range = ball.y + ball.radius >= py and ball.y - ball.radius <= py + ph
        
        return in_x_range and in_y_range
    
    def draw(self, frame: np.ndarray, has_player: bool):
        """Draw paddle on frame"""
        px, py, pw, ph = self.get_rect()
        
        if has_player:
            # Draw paddle with glow effect
            # Glow
            glow_overlay = frame.copy()
            cv2.rectangle(glow_overlay, (px - 3, py - 3), 
                         (px + pw + 3, py + ph + 3), self.color, -1)
            cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0, frame)
            
            # Main paddle
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), self.color, -1)
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (255, 255, 255), 3)
        else:
            # Draw waiting message with pulsing effect
            pulse = 0.5 + 0.3 * np.sin(cv2.getTickCount() / 500.0)
            color = tuple(int(c * pulse) for c in (150, 150, 150))
            text = "Waiting..."
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = px - (text_size[0] - pw) // 2
            cv2.putText(frame, text, (text_x, py + ph // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


class PingPongGame:
    """Two-player AR Ping Pong game"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        
        # Game objects
        self.ball = Ball(width // 2, height // 2)
        self.left_paddle = Paddle(50, 20, 150, 'left')
        self.right_paddle = Paddle(width - 50, 20, 150, 'right')
        
        # Scores
        self.left_score = 0
        self.right_score = 0
        
        # State
        self.game_active = False
        self.countdown = 0
        self.countdown_start = 0
        self.winner = None
        self.win_score = 11  # First to 11 wins
        
        # Player detection
        self.left_player_hand = None
        self.right_player_hand = None
        
        # Start countdown
        self.start_countdown()
    
    def start_countdown(self):
        """Start 3-second countdown"""
        self.countdown = 3
        self.countdown_start = time.time()
        self.game_active = False
    
    def update(self, left_hand_y: Optional[int], right_hand_y: Optional[int]) -> bool:
        """Update game state
        
        Args:
            left_hand_y: Left player hand Y position (None if not detected)
            right_hand_y: Right player hand Y position (None if not detected)
            
        Returns:
            True if game state changed
        """
        changed = False
        
        # Update player presence
        self.left_player_hand = left_hand_y
        self.right_player_hand = right_hand_y
        
        # Handle countdown
        if self.countdown > 0:
            elapsed = time.time() - self.countdown_start
            new_countdown = 3 - int(elapsed)
            if new_countdown != self.countdown:
                self.countdown = new_countdown
                changed = True
            
            if self.countdown <= 0:
                self.game_active = True
                self.countdown = 0
                changed = True
            
            return changed
        
        # Game over
        if self.winner:
            return False
        
        # Need both players
        if left_hand_y is None or right_hand_y is None:
            return False
        
        # Update paddles
        self.left_paddle.update_position(left_hand_y)
        self.right_paddle.update_position(right_hand_y)
        
        # Update ball
        out_of_bounds = self.ball.update(self.width, self.height)
        
        if out_of_bounds:
            # Score point
            if self.ball.x < self.width // 2:
                # Ball went out on left side
                self.right_score += 1
                print(f"🎯 Right player scores! {self.left_score} - {self.right_score}")
            else:
                # Ball went out on right side
                self.left_score += 1
                print(f"🎯 Left player scores! {self.left_score} - {self.right_score}")
            
            # Check for winner
            if self.left_score >= self.win_score:
                self.winner = 'left'
                print(f"🏆 LEFT PLAYER WINS! {self.left_score} - {self.right_score}")
            elif self.right_score >= self.win_score:
                self.winner = 'right'
                print(f"🏆 RIGHT PLAYER WINS! {self.left_score} - {self.right_score}")
            else:
                # Reset ball
                self.ball.reset(self.width // 2, self.height // 2)
            
            changed = True
        
        # Check paddle collisions
        if self.left_paddle.check_collision(self.ball):
            self.ball.bounce_off_paddle(self.left_paddle.y, self.left_paddle.height, 'left')
            changed = True
        
        if self.right_paddle.check_collision(self.ball):
            self.ball.bounce_off_paddle(self.right_paddle.y, self.right_paddle.height, 'right')
            changed = True
        
        return changed
    
    def draw(self, frame: np.ndarray):
        """Draw game on frame"""
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw center line
        for y in range(0, self.height, 40):
            cv2.rectangle(frame, (self.width // 2 - 2, y), 
                         (self.width // 2 + 2, y + 20),
                         (100, 100, 100), -1)
        
        # Draw paddles
        self.left_paddle.draw(frame, self.left_player_hand is not None)
        self.right_paddle.draw(frame, self.right_player_hand is not None)
        
        # Draw ball (if game active)
        if self.game_active and not self.winner:
            self.ball.draw(frame)
        
        # Draw countdown
        if self.countdown > 0:
            text = str(self.countdown)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 5, 10)[0]
            text_x = (self.width - text_size[0]) // 2
            text_y = (self.height + text_size[1]) // 2
            cv2.putText(frame, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_DUPLEX, 5, (255, 255, 255), 10)
        
        # Draw scores
        self._draw_scores(frame)
        
        # Draw winner message
        if self.winner:
            self._draw_winner(frame)
        
        # Draw instructions
        if not self.game_active or self.left_player_hand is None or self.right_player_hand is None:
            self._draw_instructions(frame)
    
    def _draw_scores(self, frame: np.ndarray):
        """Draw score display"""
        # Left score
        cv2.putText(frame, str(self.left_score),
                   (self.width // 4, 100),
                   cv2.FONT_HERSHEY_DUPLEX, 3, (0, 255, 0), 5)
        
        # Right score
        score_text = str(self.right_score)
        text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_DUPLEX, 3, 5)[0]
        cv2.putText(frame, score_text,
                   (3 * self.width // 4 - text_size[0] // 2, 100),
                   cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5)
    
    def _draw_instructions(self, frame: np.ndarray):
        """Draw game instructions"""
        instructions = [
            "AR PING PONG",
            "",
            "LEFT PLAYER: Show hand on LEFT side",
            "RIGHT PLAYER: Show hand on RIGHT side",
            "",
            "Move hand UP/DOWN to control paddle",
            f"First to {self.win_score} wins!",
        ]
        
        y = self.height // 2 - len(instructions) * 20
        for instruction in instructions:
            if instruction:
                text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                x = (self.width - text_size[0]) // 2
                cv2.putText(frame, instruction, (x, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y += 40
    
    def _draw_winner(self, frame: np.ndarray):
        """Draw winner message"""
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.width // 4, self.height // 4),
                     (3 * self.width // 4, 3 * self.height // 4),
                     (0, 128, 0) if self.winner == 'left' else (0, 0, 128), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        winner_text = "LEFT PLAYER WINS!" if self.winner == 'left' else "RIGHT PLAYER WINS!"
        text_size = cv2.getTextSize(winner_text, cv2.FONT_HERSHEY_DUPLEX, 2, 4)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        cv2.putText(frame, winner_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 4)
        
        score_text = f"{self.left_score} - {self.right_score}"
        text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
        text_x = (self.width - text_size[0]) // 2
        cv2.putText(frame, score_text, (text_x, text_y + 60),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 0), 3)
        
        cv2.putText(frame, "Press 'R' to restart", 
                   (self.width // 2 - 150, text_y + 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
    
    def reset(self):
        """Reset game"""
        self.left_score = 0
        self.right_score = 0
        self.winner = None
        self.ball.reset(self.width // 2, self.height // 2)
        self.start_countdown()
        print("\n🔄 New game started!")

