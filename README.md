# 🎮 Gestify - Hand Gesture Control & AR Games Library

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)]()

A professional Python library for hand gesture recognition and AR games using computer vision. Control your computer naturally with hand gestures or play interactive AR games!

## ✨ Features

### 🎯 Gesture Control Library
- **13 Distinct Gestures**: Move cursor, click, drag, scroll, and more
- **Smart Detection**: Attention tracking, gesture cooldown, cursor smoothing
- **Two-Hand Support**: Advanced multi-hand gestures (zoom, rotate)
- **Professional API**: Easy-to-use, well-documented, configurable
- **Production Ready**: Robust error handling, resource cleanup

### 🎮 AR Games (New!)
- **Puzzle Game**: Match shapes using hand gestures
- **Ping Pong**: Two-player competitive game with hand-controlled paddles
- **Full HD**: 1080p fullscreen immersive experience
- **Natural Controls**: Direct hand tracking for intuitive gameplay

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/ranjeetds/gestify.git
cd gestify

# Setup (creates venv and installs dependencies)
chmod +x setup.sh
./setup.sh

# Activate environment
source venv/bin/activate

# Install as package (optional)
pip install -e .
```

## 🚀 Quick Start

### Gesture Control

```bash
# Run gesture control
python -m gestify_lib

# Or if installed as package
gestify --fast
```

### AR Puzzle Game

```bash
# Play shape matching puzzle
python run_ar_game.py

# Or with difficulty
python run_ar_game.py easy    # 3 shapes
python run_ar_game.py medium  # 4 shapes
python run_ar_game.py hard    # 5 shapes
```

**Controls:**
- Move hand to control cursor
- Pinch fingers to pick objects
- Hold pinch and move to drag
- Release to place objects

### AR Ping Pong

```bash
# Two-player ping pong
python run_pingpong.py
```

**Controls:**
- LEFT PLAYER: Show hand on left side
- RIGHT PLAYER: Show hand on right side
- Move hand UP/DOWN to control paddle
- First to 11 points wins!

## 📖 Library Usage

### Basic Gesture Control

```python
from gestify_lib import GestifyController

# Simple usage
controller = GestifyController()
controller.run()
```

### Custom Configuration

```python
from gestify_lib import GestifyController, GestifyConfig

# Fast mode configuration
config = GestifyConfig.fast_mode()
controller = GestifyController(config)
controller.run()

# Custom configuration
config = GestifyConfig(
    max_hands=1,
    enable_face_tracking=False,
    cursor_smoothing=5,
    hand_confidence=0.7
)
controller = GestifyController(config)
controller.run()
```

### AR Games API

```python
# Puzzle Game
from gestify_lib.games import ARGameController

controller = ARGameController(
    game_width=1920,
    game_height=1080,
    difficulty="medium"
)
controller.run()
```

```python
# Ping Pong
from gestify_lib.games import PingPongGameController

controller = PingPongGameController(
    game_width=1920,
    game_height=1080
)
controller.run()
```

## 🎯 Gesture Reference

| Gesture | Hand Shape | Action | Use Case |
|---------|-----------|--------|----------|
| **Cursor Move** | ☝️ Index finger | Move cursor | Navigation |
| **Click** | 👌 Pinch | Left click | Selection |
| **Double Click** | 👌👌 Two pinches | Double click | Open files |
| **Drag** | ✌️ Peace sign | Click & drag | Move items |
| **Scroll** | ✊ Fist moving | Scroll | Browse content |
| **Pause** | 🖐️ Open palm | Press Space | Media control |
| **Confirm** | 👍 Thumbs up | Press Enter | Confirm action |
| **Cancel** | 👎 Thumbs down | Press Escape | Cancel/back |
| **Zoom In** | 🤲 Hands apart | Zoom in | Maps, images |
| **Zoom Out** | 🤲 Hands together | Zoom out | Maps, images |

## 🎮 AR Games

### Puzzle Game

**Objective:** Match colored shapes to their target zones

**Features:**
- 5 different shapes (circle, square, triangle, star, heart)
- Pick and place mechanics
- Score tracking
- 3 difficulty levels
- Particle effects

**Controls:**
- Point finger: Move cursor
- Pinch: Pick/place objects
- Hold & drag: Move objects around

### Ping Pong

**Objective:** Two-player competitive ping pong

**Features:**
- Hand-controlled paddles
- Dynamic ball physics
- Score tracking (first to 11 wins)
- Ball speeds up with each hit
- Smooth hand tracking

**Controls:**
- Move hand up/down: Control paddle
- Hands automatically assigned to left/right players

## 🛠️ Project Structure

```
gestify/
├── gestify_lib/              # Main library
│   ├── core/                 # Core functionality
│   │   ├── controller.py     # Main controller
│   │   └── config.py         # Configuration
│   ├── detectors/            # Detection modules
│   │   ├── hand_detector.py  # Hand tracking
│   │   ├── face_detector.py  # Face/attention
│   │   └── gesture_recognizer.py  # Gestures
│   ├── utils/                # Utilities
│   │   ├── action_executor.py  # System actions
│   │   └── ui_renderer.py    # UI rendering
│   └── games/                # AR Games
│       ├── ar_game_controller.py  # Puzzle game
│       ├── pingpong_controller.py # Ping pong
│       ├── game_objects.py   # Game objects
│       ├── puzzle_game.py    # Puzzle logic
│       └── pingpong_game.py  # Pong logic
├── examples/                 # Example scripts
│   ├── basic_usage.py
│   ├── custom_config.py
│   ├── ar_puzzle_game.py
│   └── ar_ping_pong.py
├── run_ar_game.py           # Quick puzzle launcher
├── run_pingpong.py          # Quick pong launcher
├── requirements.txt         # Dependencies
└── setup.py                 # Package setup
```

## ⚙️ Configuration

### Preset Modes

```python
from gestify_lib import GestifyConfig

# Fast mode (speed optimized)
config = GestifyConfig.fast_mode()

# Accurate mode (precision optimized)
config = GestifyConfig.accurate_mode()

# Two-hand mode (multi-hand gestures)
config = GestifyConfig.two_hand_mode()
```

### Custom Configuration

```python
config = GestifyConfig(
    # Camera settings
    camera_index=0,
    camera_width=640,
    camera_height=480,
    camera_fps=30,
    
    # Detection settings
    max_hands=2,
    hand_confidence=0.7,
    face_confidence=0.5,
    enable_face_tracking=True,
    
    # Behavior settings
    cursor_smoothing=3,
    gesture_cooldown=0.25,
    pinch_threshold=20,
    
    # UI settings
    show_ui=True,
    show_debug=False
)
```

## 🎓 Examples

### 1. Basic Gesture Control

```python
from gestify_lib import GestifyController

controller = GestifyController()
controller.run()
```

### 2. Custom Game

```python
from gestify_lib.games import PuzzleGame
import cv2

# Create custom game
game = PuzzleGame(1920, 1080, difficulty="hard")

# Game loop
while True:
    # Get hand position from your tracking
    cursor_pos = (x, y)
    is_picking = detect_pinch()
    is_releasing = not is_picking
    
    # Update game
    game.update(cursor_pos, is_picking, is_releasing, is_holding)
    
    # Draw game
    frame = get_camera_frame()
    game.draw(frame)
    cv2.imshow('Game', frame)
```

### 3. Fast Mode Gesture Control

```python
from gestify_lib import GestifyController, GestifyConfig

config = GestifyConfig(
    max_hands=1,
    enable_face_tracking=False,
    hand_model_complexity=0,  # Lite model
    cursor_smoothing=2
)

controller = GestifyController(config)
controller.run()
```

## 🐛 Troubleshooting

### Camera Issues

```bash
# Test setup
python test_setup.py

# Check camera permissions
# macOS: System Preferences → Security & Privacy → Camera

# Try different camera
gestify --camera 1
```

### Performance Issues

- Use fast mode: `gestify --fast`
- Disable face tracking: `gestify --no-face`
- Lower resolution in config
- Close other camera applications

### Gesture Recognition Issues

- Ensure good lighting
- Keep hands clearly visible
- Use distinct gestures
- Adjust confidence thresholds
- Check gesture cooldown timing

## 📊 Requirements

- Python 3.8+
- Webcam (720p or higher recommended)
- Operating System: macOS, Linux, or Windows
- RAM: 4GB minimum, 8GB recommended
- Good lighting conditions

## 📝 Dependencies

Core dependencies (auto-installed):
- OpenCV (cv2) - Video processing
- MediaPipe - Hand/face tracking
- NumPy - Numerical operations
- PyAutoGUI - System control

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand and face tracking
- [OpenCV](https://opencv.org/) for computer vision
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for system control

## 📧 Contact

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/ranjeetds/gestify/issues
- Repository: https://github.com/ranjeetds/gestify

---

**Made with ❤️ for natural human-computer interaction**

🎮 **Try the games:** `python run_ar_game.py` or `python run_pingpong.py`  
✋ **Control your computer:** `gestify --fast`  
📚 **Read the code:** Well-documented, easy to extend
