"""
Piano sound generator using pygame mixer
"""

import pygame
import numpy as np
from typing import Dict
import time


class PianoSoundGenerator:
    """Generate realistic piano sounds"""
    
    # Piano note frequencies (Hz)
    NOTE_FREQUENCIES = {
        'C': 261.63,
        'C#': 277.18,
        'D': 293.66,
        'D#': 311.13,
        'E': 329.63,
        'F': 349.23,
        'F#': 369.99,
        'G': 392.00,
        'G#': 415.30,
        'A': 440.00,
        'A#': 466.16,
        'B': 493.88,
        'C5': 523.25,
    }
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize sound generator
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        self.sample_rate = sample_rate
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._generate_all_sounds()
        print("✅ Piano sound system initialized")
    
    def _generate_all_sounds(self):
        """Pre-generate all piano sounds"""
        for note_name, frequency in self.NOTE_FREQUENCIES.items():
            self.sounds[note_name] = self._generate_piano_sound(frequency)
    
    def _generate_piano_sound(self, frequency: float, duration: float = 1.5) -> pygame.mixer.Sound:
        """Generate a single piano note with harmonics
        
        Args:
            frequency: Note frequency in Hz
            duration: Note duration in seconds
            
        Returns:
            pygame.mixer.Sound object
        """
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # Create piano-like sound with harmonics and envelope
        # Fundamental frequency
        wave = 0.4 * np.sin(2 * np.pi * frequency * t)
        
        # Add harmonics for richer sound
        wave += 0.2 * np.sin(2 * np.pi * 2 * frequency * t)  # 2nd harmonic
        wave += 0.1 * np.sin(2 * np.pi * 3 * frequency * t)  # 3rd harmonic
        wave += 0.05 * np.sin(2 * np.pi * 4 * frequency * t) # 4th harmonic
        
        # Apply ADSR envelope (Attack, Decay, Sustain, Release)
        attack_time = 0.01  # Fast attack
        decay_time = 0.1
        sustain_level = 0.7
        release_time = 0.5
        
        envelope = np.ones(n_samples)
        
        # Attack phase
        attack_samples = int(attack_time * self.sample_rate)
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        decay_samples = int(decay_time * self.sample_rate)
        if attack_samples + decay_samples < n_samples:
            envelope[attack_samples:attack_samples + decay_samples] = np.linspace(
                1, sustain_level, decay_samples)
        
        # Sustain phase (constant level)
        sustain_end = n_samples - int(release_time * self.sample_rate)
        if attack_samples + decay_samples < sustain_end:
            envelope[attack_samples + decay_samples:sustain_end] = sustain_level
        
        # Release phase (fade out)
        release_samples = n_samples - sustain_end
        if release_samples > 0:
            envelope[sustain_end:] = np.linspace(sustain_level, 0, release_samples)
        
        # Apply envelope
        wave = wave * envelope
        
        # Normalize
        wave = wave / np.max(np.abs(wave))
        
        # Convert to 16-bit audio
        audio = np.array(wave * 32767, dtype=np.int16)
        
        # Create stereo (duplicate to both channels)
        stereo_audio = np.column_stack((audio, audio))
        
        # Create pygame Sound from numpy array
        sound = pygame.sndarray.make_sound(stereo_audio)
        
        return sound
    
    def play_note(self, note_name: str, volume: float = 0.7):
        """Play a piano note
        
        Args:
            note_name: Note name (e.g., 'C', 'D#', 'A')
            volume: Volume level (0.0 to 1.0)
        """
        if note_name in self.sounds:
            sound = self.sounds[note_name]
            sound.set_volume(volume)
            sound.play()
    
    def stop_note(self, note_name: str):
        """Stop a playing note
        
        Args:
            note_name: Note name
        """
        if note_name in self.sounds:
            self.sounds[note_name].stop()
    
    def stop_all(self):
        """Stop all playing notes"""
        pygame.mixer.stop()
    
    def cleanup(self):
        """Cleanup audio system"""
        pygame.mixer.quit()

