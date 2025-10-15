# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] - 2025-10-15

### Added - AR Games Platform
- **AR Puzzle Game**: Interactive shape-matching game with hand gesture controls
  - Pick and place mechanics using pinch gestures
  - 5 different shapes (circle, square, triangle, star, heart)
  - 3 difficulty levels (easy, medium, hard)
  - Score tracking and particle effects
  - Full HD 1080p fullscreen experience

- **AR Ping Pong**: Two-player competitive game
  - Hand-controlled paddles for left and right players
  - Dynamic ball physics with speed increases
  - Score tracking (first to 11 wins)
  - Smooth hand tracking with 5-frame buffer
  - Intelligent 2-hand selection (nearest hands only)
  - Buffer zones to prevent player confusion

- **AR Piano** 🎹 NEW!: Interactive piano with song learning
  - 8 playable keys (C major scale + C5)
  - Touch keys with fingertips to play notes
  - Visual feedback for key presses (white/black keys)
  - 4 pre-loaded songs:
    - Happy Birthday
    - Twinkle Twinkle Little Star
    - Mary Had a Little Lamb
    - Jingle Bells
  - Falling note guides (like Piano Tiles/Simply Piano)
  - Real-time hit detection with hit zone indicator
  - Score and combo system
  - Build combos by hitting consecutive notes correctly
  - Song selection menu (press 1-4)
  - Quick launch: `python run_piano.py`

- **Games Module** (`gestify_lib/games/`)
  - `ARGameController` - Puzzle game controller
  - `PingPongGameController` - Ping pong game controller
  - `ARPianoController` - Piano game controller 🎹 NEW!
  - `PuzzleGame` - Puzzle game logic
  - `PingPongGame` - Ping pong game logic
  - `ARPiano` - Piano game logic 🎹 NEW!
  - `GameObject`, `PuzzlePiece`, `TargetZone` - Game objects
  - `Ball`, `Paddle` - Ping pong components
  - `PianoKey`, `FallingNote` - Piano components 🎹 NEW!

### Improved - Hand Tracking
- **Direct Hand Tracking**: Cursor always follows index finger position
  - Removed gesture dependency for cursor movement
  - Natural mirror-mode control
  - Reduced latency (~40ms vs ~50ms)

- **Hysteresis Thresholds**: Stable pinch-and-hold
  - Different thresholds for grab (60px) vs release (90px)
  - 30px buffer zone prevents accidental drops
  - Smooth hand movement doesn't break hold

- **Multi-Hand Selection**: Intelligent hand filtering
  - Selects only 2 nearest/largest hands
  - Ignores background people
  - Allows hands to leave/enter frame gracefully

- **Smoothing Improvements**:
  - 5-frame history buffer for hand positions
  - 80/20 weighted averaging for paddle movement
  - 3-frame smoothing for cursor (reduced from 5)

### Fixed
- Mirror mode: Cursor now moves in correct direction
- Pinch stability: Objects don't drop during lateral hand movement
- Player assignment: Buffer zone prevents paddle swapping
- Hand coordination: Smooth paddle control without jitter

### Changed
- Consolidated documentation into single README.md
- Restructured as proper library with games as examples
- Updated project structure for better organization

## [2.0.0] - Previous Version

### Complete Architectural Rewrite
- Transformed from scripts to professional Python library
- Object-oriented structure with modular design
- 13 distinct, non-overlapping gestures
- Attention detection with face tracking
- Configurable modes (fast, accurate, two-hand)
- CLI tool and Python API
- Comprehensive documentation

### Core Features
- Hand detection with MediaPipe
- Face tracking and attention detection
- Gesture recognition with cooldown
- Action execution with PyAutoGUI
- UI rendering and feedback
- Robust camera initialization
- Error handling and cleanup

---

For more details, see the [GitHub repository](https://github.com/ranjeetds/gestify)
