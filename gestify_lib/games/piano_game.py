"""
AR Piano Game - Play piano with hand gestures and learn songs
"""

import cv2
import numpy as np
import time
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import random


# Note data for songs (note_name, duration_beats, key_index)
SONGS = {
    "Happy Birthday": [
        # "Happy birthday to you"
        ("C", 0.75, 0), ("C", 0.25, 0), ("D", 1.0, 1), ("C", 1.0, 0), 
        ("F", 1.0, 3), ("E", 2.0, 2),
        # "Happy birthday to you"
        ("C", 0.75, 0), ("C", 0.25, 0), ("D", 1.0, 1), ("C", 1.0, 0),
        ("G", 1.0, 4), ("F", 2.0, 3),
        # "Happy birthday dear..."
        ("C", 0.75, 0), ("C", 0.25, 0), ("C5", 1.0, 7), ("A", 1.0, 5),
        ("F", 1.0, 3), ("E", 1.0, 2), ("D", 2.0, 1),
        # "Happy birthday to you"
        ("Bb", 0.75, 6), ("Bb", 0.25, 6), ("A", 1.0, 5), ("F", 1.0, 3),
        ("G", 1.0, 4), ("F", 2.0, 3),
    ],
    "Twinkle Twinkle": [
        ("C", 1.0, 0), ("C", 1.0, 0), ("G", 1.0, 4), ("G", 1.0, 4),
        ("A", 1.0, 5), ("A", 1.0, 5), ("G", 2.0, 4),
        ("F", 1.0, 3), ("F", 1.0, 3), ("E", 1.0, 2), ("E", 1.0, 2),
        ("D", 1.0, 1), ("D", 1.0, 1), ("C", 2.0, 0),
    ],
    "Mary Had a Little Lamb": [
        ("E", 1.0, 2), ("D", 1.0, 1), ("C", 1.0, 0), ("D", 1.0, 1),
        ("E", 1.0, 2), ("E", 1.0, 2), ("E", 2.0, 2),
        ("D", 1.0, 1), ("D", 1.0, 1), ("D", 2.0, 1),
        ("E", 1.0, 2), ("G", 1.0, 4), ("G", 2.0, 4),
    ],
    "Jingle Bells": [
        ("E", 1.0, 2), ("E", 1.0, 2), ("E", 2.0, 2),
        ("E", 1.0, 2), ("E", 1.0, 2), ("E", 2.0, 2),
        ("E", 1.0, 2), ("G", 1.0, 4), ("C", 1.0, 0), ("D", 1.0, 1),
        ("E", 4.0, 2),
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
    is_pressed: bool = False
    color: Tuple[int, int, int] = (255, 255, 255)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within key"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, frame: np.ndarray):
        """Draw piano key"""
        # Key color
        if self.is_pressed:
            color = (100, 255, 100) if not self.is_black else (150, 150, 150)
        else:
            color = (255, 255, 255) if not self.is_black else (50, 50, 50)
        
        # Draw key
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height),
                     color, -1)
        
        # Draw border
        border_color = (200, 200, 200) if not self.is_black else (30, 30, 30)
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height),
                     border_color, 2)
        
        # Draw note name at bottom
        if not self.is_black:
            text_size = cv2.getTextSize(self.note, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = self.x + (self.width - text_size[0]) // 2
            text_y = self.y + self.height - 10
            cv2.putText(frame, self.note, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


@dataclass
class FallingNote:
    """Represents a falling note guide"""
    key_index: int
    y: float  # Current Y position
    duration: float  # How long to hold
    note_name: str
    
    def update(self, speed: float):
        """Update note position"""
        self.y += speed
    
    def draw(self, frame: np.ndarray, key: PianoKey):
        """Draw falling note"""
        # Calculate note rectangle
        note_height = int(self.duration * 60)  # Longer notes are taller
        note_y = int(self.y)
        
        # Draw note with transparency
        overlay = frame.copy()
        color = (255, 200, 0) if not key.is_black else (255, 150, 0)
        cv2.rectangle(overlay, 
                     (key.x + 5, note_y), 
                     (key.x + key.width - 5, note_y + note_height),
                     color, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw border
        cv2.rectangle(frame,
                     (key.x + 5, note_y),
                     (key.x + key.width - 5, note_y + note_height),
                     (255, 255, 255), 2)


class ARPiano:
    """AR Piano with hand tracking and song guides"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        
        # Piano setup
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
        self.fall_speed = 3.0
        self.hit_zone_y = self.height - 300  # Where notes should be hit
        
        # UI state
        self.show_song_menu = True
        self.menu_selected = 0
        
    def _setup_keys(self):
        """Setup piano keyboard"""
        # White keys: C D E F G A B (7 keys, 1 octave)
        white_notes = ["C", "D", "E", "F", "G", "A", "B", "C5"]
        # Black keys: C# D# F# G# A#
        black_notes = ["C#", "D#", None, "F#", "G#", "A#", None]
        
        # Calculate dimensions
        key_start_x = 400  # Start from center-left
        white_key_width = 80
        white_key_height = 400
        black_key_width = 50
        black_key_height = 250
        
        # Create white keys
        for i, note in enumerate(white_notes):
            x = key_start_x + i * white_key_width
            y = self.height - white_key_height - 50
            key = PianoKey(
                note=note,
                index=i,
                x=x,
                y=y,
                width=white_key_width,
                height=white_key_height,
                is_black=False
            )
            self.keys.append(key)
        
        # Create black keys (on top of white keys)
        black_key_index = len(white_notes)
        for i, note in enumerate(black_notes):
            if note:  # Skip None positions (no black key between E-F and B-C)
                x = key_start_x + i * white_key_width + white_key_width - black_key_width // 2
                y = self.height - white_key_height - 50
                key = PianoKey(
                    note=note,
                    index=black_key_index,
                    x=x,
                    y=y,
                    width=black_key_width,
                    height=black_key_height,
                    is_black=True
                )
                self.keys.append(key)
                black_key_index += 1
    
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
    
    def update(self, left_hand_pos: Optional[Tuple[int, int]], 
               right_hand_pos: Optional[Tuple[int, int]]) -> bool:
        """Update piano state
        
        Args:
            left_hand_pos: Left hand fingertip position
            right_hand_pos: Right hand fingertip position
            
        Returns:
            True if state changed
        """
        changed = False
        
        # Reset all keys
        for key in self.keys:
            key.is_pressed = False
        
        # Check hand collisions with keys
        hands = [left_hand_pos, right_hand_pos]
        for hand_pos in hands:
            if hand_pos:
                # Check black keys first (they're on top)
                for key in sorted(self.keys, key=lambda k: k.is_black, reverse=True):
                    if key.contains_point(hand_pos[0], hand_pos[1]):
                        if not key.is_pressed:
                            key.is_pressed = True
                            self._play_note(key)
                            changed = True
                        break
        
        # Update song if playing
        if self.song_playing:
            self._update_song()
            changed = True
        
        return changed
    
    def _play_note(self, key: PianoKey):
        """Play note sound and check if it matches falling note"""
        print(f"🎹 Playing: {key.note}")
        
        # Check if this matches a falling note in hit zone
        if self.song_playing:
            hit_zone_start = self.hit_zone_y - 50
            hit_zone_end = self.hit_zone_y + 100
            
            for note in self.falling_notes:
                if note.key_index == key.index:
                    if hit_zone_start <= note.y <= hit_zone_end:
                        # Hit!
                        self.score += 100 * (self.combo + 1)
                        self.combo += 1
                        self.max_combo = max(self.max_combo, self.combo)
                        self.notes_hit += 1
                        self.falling_notes.remove(note)
                        print(f"✨ Hit! Combo: {self.combo}x Score: {self.score}")
                        return
    
    def _update_song(self):
        """Update song progression and falling notes"""
        current_time = time.time() - self.song_start_time
        beat_duration = 60.0 / self.song_tempo  # seconds per beat
        
        # Spawn new notes
        while (self.note_index < len(self.song_notes) and 
               current_time >= self.note_index * beat_duration * 0.8):
            note_name, duration, key_index = self.song_notes[self.note_index]
            
            # Create falling note
            falling_note = FallingNote(
                key_index=key_index,
                y=-100,  # Start above screen
                duration=duration,
                note_name=note_name
            )
            self.falling_notes.append(falling_note)
            self.note_index += 1
        
        # Update falling notes
        for note in self.falling_notes[:]:
            note.update(self.fall_speed)
            
            # Remove if passed bottom
            if note.y > self.height:
                self.falling_notes.remove(note)
                self.notes_missed += 1
                self.combo = 0  # Reset combo on miss
                print(f"❌ Missed note!")
        
        # Check if song ended
        if self.note_index >= len(self.song_notes) and len(self.falling_notes) == 0:
            self._end_song()
    
    def _end_song(self):
        """End song and show results"""
        self.song_playing = False
        total_notes = self.notes_hit + self.notes_missed
        accuracy = (self.notes_hit / total_notes * 100) if total_notes > 0 else 0
        
        print(f"\n🎵 Song Complete!")
        print(f"Score: {self.score}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Max Combo: {self.max_combo}x")
        print(f"Hit: {self.notes_hit} | Missed: {self.notes_missed}")
    
    def draw(self, frame: np.ndarray):
        """Draw piano and UI"""
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        if self.show_song_menu:
            self._draw_song_menu(frame)
        else:
            # Draw falling notes
            for note in self.falling_notes:
                if note.key_index < len(self.keys):
                    note.draw(frame, self.keys[note.key_index])
            
            # Draw hit zone indicator
            cv2.line(frame, (350, self.hit_zone_y), 
                    (self.width - 350, self.hit_zone_y),
                    (255, 255, 0), 3)
            cv2.putText(frame, "HIT", (300, self.hit_zone_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Draw piano keys
            # Draw white keys first, then black keys on top
            for key in sorted(self.keys, key=lambda k: k.is_black):
                key.draw(frame)
            
            # Draw score and info
            self._draw_score(frame)
        
        # Draw title
        cv2.putText(frame, "AR PIANO", (50, 60),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
    
    def _draw_song_menu(self, frame: np.ndarray):
        """Draw song selection menu"""
        # Title
        cv2.putText(frame, "SELECT A SONG", 
                   (self.width // 2 - 200, 150),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
        
        # Song list
        y = 250
        song_names = list(self.songs.keys())
        for i, song in enumerate(song_names):
            if i == self.menu_selected:
                color = (0, 255, 255)
                cv2.rectangle(frame, (self.width // 2 - 250, y - 40),
                             (self.width // 2 + 250, y + 10),
                             color, 3)
            else:
                color = (200, 200, 200)
            
            cv2.putText(frame, f"{i + 1}. {song}", 
                       (self.width // 2 - 200, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
            y += 80
        
        # Instructions
        cv2.putText(frame, "Press number key (1-4) to select song", 
                   (self.width // 2 - 300, self.height - 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        cv2.putText(frame, "Press 'M' to return to menu during song", 
                   (self.width // 2 - 300, self.height - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
    
    def _draw_score(self, frame: np.ndarray):
        """Draw score panel"""
        # Score panel background
        panel_x = self.width - 350
        panel_y = 20
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + 330, panel_y + 250),
                     (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Song name
        if self.current_song:
            cv2.putText(frame, self.current_song, 
                       (panel_x + 10, panel_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Score
        cv2.putText(frame, f"Score: {self.score}", 
                   (panel_x + 10, panel_y + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Combo
        combo_color = (0, 255, 0) if self.combo > 0 else (150, 150, 150)
        cv2.putText(frame, f"Combo: {self.combo}x", 
                   (panel_x + 10, panel_y + 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, combo_color, 2)
        
        # Max combo
        cv2.putText(frame, f"Max: {self.max_combo}x", 
                   (panel_x + 10, panel_y + 155),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Hit/Miss
        cv2.putText(frame, f"Hit: {self.notes_hit}", 
                   (panel_x + 10, panel_y + 195),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        cv2.putText(frame, f"Miss: {self.notes_missed}", 
                   (panel_x + 10, panel_y + 225),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
    
    def handle_key_press(self, key: int):
        """Handle keyboard input"""
        # Number keys to select song
        if self.show_song_menu:
            if ord('1') <= key <= ord('4'):
                song_index = key - ord('1')
                song_names = list(self.songs.keys())
                if song_index < len(song_names):
                    self.start_song(song_names[song_index])
        
        # M to return to menu
        if key == ord('m') or key == ord('M'):
            self.show_song_menu = True
            self.song_playing = False
            self.falling_notes.clear()
    
    def reset(self):
        """Reset piano"""
        self.show_song_menu = True
        self.song_playing = False
        self.falling_notes.clear()
        self.score = 0
        self.combo = 0

