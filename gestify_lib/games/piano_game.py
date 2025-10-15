"""
Realistic AR Piano Game - Multi-finger tracking with spatial motion detection
"""

import cv2
import numpy as np
import time
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, field
from .piano_audio import PianoSoundGenerator


# Note data for songs (note_name, duration_beats, key_index)
SONGS = {
    "Happy Birthday": [
        ("C", 0.75, 0), ("C", 0.25, 0), ("D", 1.0, 2), ("C", 1.0, 0), 
        ("F", 1.0, 5), ("E", 2.0, 4),
        ("C", 0.75, 0), ("C", 0.25, 0), ("D", 1.0, 2), ("C", 1.0, 0),
        ("G", 1.0, 7), ("F", 2.0, 5),
        ("C", 0.75, 0), ("C", 0.25, 0), ("C5", 1.0, 12), ("A", 1.0, 9),
        ("F", 1.0, 5), ("E", 1.0, 4), ("D", 2.0, 2),
        ("A#", 0.75, 10), ("A#", 0.25, 10), ("A", 1.0, 9), ("F", 1.0, 5),
        ("G", 1.0, 7), ("F", 2.0, 5),
    ],
    "Twinkle Twinkle": [
        ("C", 1.0, 0), ("C", 1.0, 0), ("G", 1.0, 7), ("G", 1.0, 7),
        ("A", 1.0, 9), ("A", 1.0, 9), ("G", 2.0, 7),
        ("F", 1.0, 5), ("F", 1.0, 5), ("E", 1.0, 4), ("E", 1.0, 4),
        ("D", 1.0, 2), ("D", 1.0, 2), ("C", 2.0, 0),
    ],
    "Mary Had a Little Lamb": [
        ("E", 1.0, 4), ("D", 1.0, 2), ("C", 1.0, 0), ("D", 1.0, 2),
        ("E", 1.0, 4), ("E", 1.0, 4), ("E", 2.0, 4),
        ("D", 1.0, 2), ("D", 1.0, 2), ("D", 2.0, 2),
        ("E", 1.0, 4), ("G", 1.0, 7), ("G", 2.0, 7),
    ],
    "Jingle Bells": [
        ("E", 1.0, 4), ("E", 1.0, 4), ("E", 2.0, 4),
        ("E", 1.0, 4), ("E", 1.0, 4), ("E", 2.0, 4),
        ("E", 1.0, 4), ("G", 1.0, 7), ("C", 1.0, 0), ("D", 1.0, 2),
        ("E", 4.0, 4),
    ],
}


@dataclass
class PianoKey:
    """Represents a piano key"""
    note: str
    index: int
    x: int
    y: int
    width: int
    height: int
    is_black: bool
    frequency: float
    is_pressed: bool = False
    last_press_time: float = 0
    press_cooldown: float = 0.1  # 100ms cooldown
    
    def can_press(self) -> bool:
        """Check if key can be pressed (cooldown expired)"""
        return time.time() - self.last_press_time > self.press_cooldown
    
    def press(self):
        """Mark key as pressed"""
        self.is_pressed = True
        self.last_press_time = time.time()
    
    def release(self):
        """Mark key as released"""
        self.is_pressed = False
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within key"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, frame: np.ndarray):
        """Draw piano key with realistic appearance"""
        # Key color based on state
        if self.is_pressed:
            color = (120, 255, 120) if not self.is_black else (100, 100, 100)
        else:
            color = (245, 245, 245) if not self.is_black else (30, 30, 30)
        
        # Draw key body
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height),
                     color, -1)
        
        # Draw 3D effect
        if not self.is_pressed:
            # Highlight (top-left)
            if not self.is_black:
                cv2.line(frame, (self.x + 2, self.y + 2), 
                        (self.x + self.width - 2, self.y + 2),
                        (255, 255, 255), 1)
                cv2.line(frame, (self.x + 2, self.y + 2), 
                        (self.x + 2, self.y + self.height - 2),
                        (255, 255, 255), 1)
            
            # Shadow (bottom-right)
            shadow_color = (180, 180, 180) if not self.is_black else (10, 10, 10)
            cv2.line(frame, (self.x + self.width - 2, self.y + 2), 
                    (self.x + self.width - 2, self.y + self.height - 2),
                    shadow_color, 1)
            cv2.line(frame, (self.x + 2, self.y + self.height - 2), 
                    (self.x + self.width - 2, self.y + self.height - 2),
                    shadow_color, 1)
        
        # Draw border
        border_color = (150, 150, 150) if not self.is_black else (0, 0, 0)
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height),
                     border_color, 2)
        
        # Draw note name at bottom (only white keys)
        if not self.is_black:
            text_size = cv2.getTextSize(self.note, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = self.x + (self.width - text_size[0]) // 2
            text_y = self.y + self.height - 10
            cv2.putText(frame, self.note, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 80), 1)


@dataclass
class FallingNote:
    """Represents a falling note guide"""
    key_index: int
    y: float
    duration: float
    note_name: str
    hit: bool = False
    
    def update(self, speed: float):
        """Update note position"""
        self.y += speed
    
    def draw(self, frame: np.ndarray, key: PianoKey):
        """Draw falling note"""
        note_height = int(self.duration * 50)
        note_y = int(self.y)
        
        # Choose color
        if self.hit:
            color = (100, 255, 100)
        else:
            color = (255, 200, 0) if not key.is_black else (255, 150, 0)
        
        # Draw note with transparency
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (key.x + 5, note_y), 
                     (key.x + key.width - 5, note_y + note_height),
                     color, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw border
        cv2.rectangle(frame,
                     (key.x + 5, note_y),
                     (key.x + key.width - 5, note_y + note_height),
                     (255, 255, 255) if self.hit else color, 2)


@dataclass
class Fingertip:
    """Represents a tracked fingertip"""
    position: Tuple[int, int]
    previous_position: Optional[Tuple[int, int]] = None
    velocity_y: float = 0  # Vertical velocity (downward is positive)
    name: str = "finger"
    
    def update_velocity(self):
        """Calculate vertical velocity"""
        if self.previous_position:
            self.velocity_y = self.position[1] - self.previous_position[1]
        else:
            self.velocity_y = 0


class RealisticARPiano:
    """Realistic AR Piano with multi-finger tracking and spatial motion detection"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        
        # Audio system
        self.audio = PianoSoundGenerator()
        
        # Piano setup - 13 keys (full octave + extras for black keys)
        self.keys: List[PianoKey] = []
        self._setup_keys()
        
        # Song system
        self.songs = SONGS
        self.current_song = None
        self.song_notes: List[Tuple[str, float, int]] = []
        self.falling_notes: List[FallingNote] = []
        self.song_playing = False
        self.song_start_time = 0
        self.song_tempo = 120  # BPM
        self.note_index = 0
        
        # Scoring
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.notes_hit = 0
        self.notes_missed = 0
        
        # Visual settings
        self.fall_speed = 3.5
        self.hit_zone_y = self.height - 500
        
        # Motion detection settings
        self.press_velocity_threshold = 8  # Pixels per frame downward
        
        # UI state
        self.show_song_menu = True
        self.menu_buttons: List[Dict] = []
        self.hovered_button = -1
        self.button_hover_start = 0
        self.hover_select_duration = 1.5  # seconds to hover for selection
        
        self._setup_menu_buttons()
        
        print("🎹 Realistic AR Piano initialized with sound!")
    
    def _setup_keys(self):
        """Setup full piano keyboard"""
        # Full octave: C C# D D# E F F# G G# A A# B C5
        notes_with_black = [
            ('C', False), ('C#', True), ('D', False), ('D#', True),
            ('E', False), ('F', False), ('F#', True), ('G', False),
            ('G#', True), ('A', False), ('A#', True), ('B', False),
            ('C5', False)
        ]
        
        frequencies = [
            261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99,
            392.00, 415.30, 440.00, 466.16, 493.88, 523.25
        ]
        
        # Calculate dimensions for vertical piano
        key_start_y = 100
        white_key_height = 150
        white_key_width = 90
        black_key_height = 100
        black_key_width = 60
        
        # Position keys vertically from top to bottom
        current_y = key_start_y
        white_key_x = 200  # Start from left
        
        for i, ((note, is_black), freq) in enumerate(zip(notes_with_black, frequencies)):
            if not is_black:
                # White key
                key = PianoKey(
                    note=note,
                    index=i,
                    x=white_key_x,
                    y=current_y,
                    width=white_key_width,
                    height=white_key_height,
                    is_black=False,
                    frequency=freq
                )
                self.keys.append(key)
                current_y += white_key_height
            else:
                # Black key (positioned to the right of white key)
                key = PianoKey(
                    note=note,
                    index=i,
                    x=white_key_x + 60,
                    y=current_y - white_key_height + 30,
                    width=black_key_width,
                    height=black_key_height,
                    is_black=True,
                    frequency=freq
                )
                self.keys.append(key)
    
    def _setup_menu_buttons(self):
        """Setup gesture-controlled menu buttons"""
        button_width = 400
        button_height = 80
        start_x = self.width // 2 - button_width // 2
        start_y = 250
        spacing = 100
        
        for i, song_name in enumerate(self.songs.keys()):
            button = {
                'name': song_name,
                'x': start_x,
                'y': start_y + i * spacing,
                'width': button_width,
                'height': button_height,
                'index': i
            }
            self.menu_buttons.append(button)
    
    def start_song(self, song_name: str):
        """Start playing a song"""
        if song_name in self.songs:
            self.current_song = song_name
            self.song_notes = self.songs[song_name].copy()
            self.falling_notes.clear()
            self.song_playing = True
            self.song_start_time = time.time()
            self.note_index = 0
            self.score = 0
            self.combo = 0
            self.max_combo = 0
            self.notes_hit = 0
            self.notes_missed = 0
            self.show_song_menu = False
            print(f"🎵 Starting song: {song_name}")
    
    def update(self, fingertips: List[Fingertip]) -> bool:
        """Update piano state with multi-finger tracking
        
        Args:
            fingertips: List of all detected fingertips with velocity
            
        Returns:
            True if state changed
        """
        changed = False
        
        # Handle menu if showing
        if self.show_song_menu:
            self._update_menu(fingertips)
            return True
        
        # Reset all keys (will be re-pressed if needed)
        for key in self.keys:
            if key.is_pressed and time.time() - key.last_press_time > 0.15:
                key.release()
        
        # Check each fingertip for key presses
        for fingertip in fingertips:
            # Check if finger is moving down fast enough (pressing motion)
            if fingertip.velocity_y > self.press_velocity_threshold:
                # Check collision with keys (prioritize black keys as they're on top)
                for key in sorted(self.keys, key=lambda k: not k.is_black):
                    if key.contains_point(fingertip.position[0], fingertip.position[1]):
                        if key.can_press():
                            key.press()
                            self._play_note(key)
                            changed = True
                        break
        
        # Update song if playing
        if self.song_playing:
            self._update_song()
            changed = True
        
        return changed
    
    def _update_menu(self, fingertips: List[Fingertip]):
        """Update menu with gesture hovering"""
        if not fingertips:
            self.hovered_button = -1
            return
        
        # Use first fingertip for menu interaction
        finger_pos = fingertips[0].position
        
        # Check which button is hovered
        current_hover = -1
        for i, button in enumerate(self.menu_buttons):
            if (button['x'] <= finger_pos[0] <= button['x'] + button['width'] and
                button['y'] <= finger_pos[1] <= button['y'] + button['height']):
                current_hover = i
                break
        
        # Handle hover timing
        if current_hover != self.hovered_button:
            # Changed button
            self.hovered_button = current_hover
            self.button_hover_start = time.time() if current_hover >= 0 else 0
        elif current_hover >= 0:
            # Still hovering on same button
            hover_duration = time.time() - self.button_hover_start
            if hover_duration >= self.hover_select_duration:
                # Selected!
                song_name = self.menu_buttons[current_hover]['name']
                self.start_song(song_name)
                self.hovered_button = -1
    
    def _play_note(self, key: PianoKey):
        """Play note sound and check if it matches falling note"""
        # Play sound
        self.audio.play_note(key.note, volume=0.8)
        
        print(f"🎹 Playing: {key.note} ({key.frequency:.2f} Hz)")
        
        # Check if this matches a falling note in hit zone
        if self.song_playing:
            hit_zone_start = self.hit_zone_y - 60
            hit_zone_end = self.hit_zone_y + 120
            
            for note in self.falling_notes:
                if note.key_index == key.index and not note.hit:
                    if hit_zone_start <= note.y <= hit_zone_end:
                        # Hit!
                        note.hit = True
                        self.score += 100 * (self.combo + 1)
                        self.combo += 1
                        self.max_combo = max(self.max_combo, self.combo)
                        self.notes_hit += 1
                        print(f"✨ Hit! Combo: {self.combo}x Score: {self.score}")
                        return
    
    def _update_song(self):
        """Update song progression"""
        current_time = time.time() - self.song_start_time
        beat_duration = 60.0 / self.song_tempo
        
        # Spawn new notes
        while (self.note_index < len(self.song_notes) and 
               current_time >= self.note_index * beat_duration * 0.8):
            note_name, duration, key_index = self.song_notes[self.note_index]
            
            falling_note = FallingNote(
                key_index=key_index,
                y=-100,
                duration=duration,
                note_name=note_name
            )
            self.falling_notes.append(falling_note)
            self.note_index += 1
        
        # Update falling notes
        for note in self.falling_notes[:]:
            note.update(self.fall_speed)
            
            if note.y > self.height:
                self.falling_notes.remove(note)
                if not note.hit:
                    self.notes_missed += 1
                    self.combo = 0
                    print(f"❌ Missed note!")
        
        # Check if song ended
        if self.note_index >= len(self.song_notes) and len(self.falling_notes) == 0:
            self._end_song()
    
    def _end_song(self):
        """End song"""
        self.song_playing = False
        total_notes = self.notes_hit + self.notes_missed
        accuracy = (self.notes_hit / total_notes * 100) if total_notes > 0 else 0
        
        print(f"\n🎵 Song Complete!")
        print(f"Score: {self.score}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Max Combo: {self.max_combo}x")
    
    def draw(self, frame: np.ndarray, fingertips: List[Fingertip]):
        """Draw piano and UI"""
        # Dark background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (10, 10, 10), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        if self.show_song_menu:
            self._draw_menu(frame, fingertips)
        else:
            # Draw falling notes
            for note in self.falling_notes:
                if 0 <= note.key_index < len(self.keys):
                    note.draw(frame, self.keys[note.key_index])
            
            # Draw hit zone
            cv2.line(frame, (150, self.hit_zone_y), 
                    (350, self.hit_zone_y),
                    (255, 255, 0), 4)
            cv2.putText(frame, "HIT", (80, self.hit_zone_y + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # Draw piano keys
            for key in sorted(self.keys, key=lambda k: k.is_black):
                key.draw(frame)
            
            # Draw score
            self._draw_score(frame)
        
        # Draw fingertips
        self._draw_fingertips(frame, fingertips)
        
        # Title
        cv2.putText(frame, "AR PIANO", (50, 60),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
    
    def _draw_menu(self, frame: np.ndarray, fingertips: List[Fingertip]):
        """Draw song selection menu"""
        # Title
        cv2.putText(frame, "SELECT A SONG", 
                   (self.width // 2 - 200, 150),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
        
        # Instruction
        cv2.putText(frame, "Hover hand over song for 1.5 seconds to select", 
                   (self.width // 2 - 350, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        # Draw buttons
        for i, button in enumerate(self.menu_buttons):
            # Determine color
            if i == self.hovered_button:
                hover_progress = min(1.0, (time.time() - self.button_hover_start) / self.hover_select_duration)
                color = (0, int(255 * hover_progress), 255)
                thickness = -1
            else:
                color = (100, 100, 100)
                thickness = 3
            
            # Draw button
            cv2.rectangle(frame, 
                         (button['x'], button['y']),
                         (button['x'] + button['width'], button['y'] + button['height']),
                         color, thickness)
            
            # Draw progress bar if hovering
            if i == self.hovered_button and thickness == -1:
                hover_progress = min(1.0, (time.time() - self.button_hover_start) / self.hover_select_duration)
                bar_width = int(button['width'] * hover_progress)
                cv2.rectangle(frame,
                             (button['x'], button['y'] + button['height'] - 10),
                             (button['x'] + bar_width, button['y'] + button['height']),
                             (0, 255, 0), -1)
            
            # Draw text
            text_color = (255, 255, 255) if i == self.hovered_button else (200, 200, 200)
            cv2.putText(frame, button['name'], 
                       (button['x'] + 50, button['y'] + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 2)
        
        # Instructions
        cv2.putText(frame, "Show open palm to return to menu during song", 
                   (self.width // 2 - 350, self.height - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
    
    def _draw_score(self, frame: np.ndarray):
        """Draw score panel"""
        panel_x = self.width - 350
        panel_y = 20
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + 330, panel_y + 250),
                     (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        if self.current_song:
            cv2.putText(frame, self.current_song[:20], 
                       (panel_x + 10, panel_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Score: {self.score}", 
                   (panel_x + 10, panel_y + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        combo_color = (0, 255, 0) if self.combo > 0 else (150, 150, 150)
        cv2.putText(frame, f"Combo: {self.combo}x", 
                   (panel_x + 10, panel_y + 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, combo_color, 2)
        
        cv2.putText(frame, f"Max: {self.max_combo}x", 
                   (panel_x + 10, panel_y + 155),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.putText(frame, f"Hit: {self.notes_hit}", 
                   (panel_x + 10, panel_y + 195),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        cv2.putText(frame, f"Miss: {self.notes_missed}", 
                   (panel_x + 10, panel_y + 225),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
    
    def _draw_fingertips(self, frame: np.ndarray, fingertips: List[Fingertip]):
        """Draw fingertip indicators"""
        for i, tip in enumerate(fingertips):
            # Color based on velocity (green=neutral, red=pressing)
            if tip.velocity_y > self.press_velocity_threshold:
                color = (0, 0, 255)  # Red - pressing
                radius = 12
            else:
                color = (0, 255, 0)  # Green - tracking
                radius = 8
            
            cv2.circle(frame, tip.position, radius, color, 2)
            cv2.circle(frame, tip.position, 3, color, -1)
            
            # Show velocity for debug
            if tip.velocity_y > 0:
                cv2.putText(frame, f"{tip.velocity_y:.0f}", 
                           (tip.position[0] + 15, tip.position[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    def handle_gesture(self, gesture_name: str):
        """Handle gesture commands"""
        if gesture_name == "open_palm" and not self.show_song_menu:
            # Return to menu
            self.show_song_menu = True
            self.song_playing = False
            self.falling_notes.clear()
            self.audio.stop_all()
            print("🔙 Returning to menu")
    
    def cleanup(self):
        """Cleanup resources"""
        self.audio.cleanup()
