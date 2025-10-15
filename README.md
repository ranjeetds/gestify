# 🎮 Gestify - AI-Powered Hand Gesture Control

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)]()

Control your computer with hand gestures using AI-powered computer vision. Gestify is a professional, object-oriented library that turns your webcam into a natural user interface.

## ✨ Features

### 🎯 Simplified Gesture Set
**Distinct, non-overlapping gestures** designed to prevent confusion:
- ☝️ **Index Finger**: Move cursor
- ✌️ **Peace Sign**: Drag & drop
- 👌 **Pinch**: Click (double pinch for double-click)
- ✊ **Fist**: Scroll
- 🖐️ **Open Palm**: Pause/Play
- 👍 **Thumbs Up**: Confirm (Enter)
- 👎 **Thumbs Down**: Cancel (Escape)
- 🤲 **Two Hands**: Zoom in/out, Rotate

### 🧠 Smart Features
- **Attention Detection**: Uses face tracking to only respond when you're looking at the screen
- **Two-Hand Support**: Advanced gestures using both hands simultaneously
- **Gesture Cooldown**: Prevents unintentional repeated actions
- **Cursor Smoothing**: Precise, jitter-free cursor movement
- **Configurable Modes**: Fast, Accurate, and Two-Hand presets

### 🏗️ Professional Architecture
- Object-oriented, modular design
- Easy-to-use API
- Comprehensive configuration options
- Installable as a Python package
- Extensive examples and documentation

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Webcam
- macOS, Linux, or Windows

### Quick Install

```bash
# Clone the repository
git clone https://github.com/ranjeetds/gestify.git
cd gestify

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package (enables 'gestify' command)
pip install -e .
```

### Alternative: Setup Script (macOS/Linux)

```bash
chmod +x setup.sh
./setup.sh
```

## 🚀 Quick Start

### Option 1: Command Line

```bash
# Run with default settings
python -m gestify_lib

# Or if installed as package
gestify

# Fast mode (single hand, no face tracking)
gestify --fast

# Accurate mode (higher confidence thresholds)
gestify --accurate

# Two-hand gesture mode
gestify --two-hand

# Custom camera
gestify --camera 1

# Disable face tracking
gestify --no-face

# Show help
gestify --help
```

### Option 2: Python Script

```python
from gestify_lib import GestifyController

# Run with default settings
controller = GestifyController()
controller.run()
```

### Option 3: Custom Configuration

```python
from gestify_lib import GestifyController, GestifyConfig

# Create custom configuration
config = GestifyConfig(
    max_hands=1,                     # Single hand only
    enable_face_tracking=False,       # Disable face tracking
    hand_model_complexity=0,          # Use lite model (faster)
    cursor_smoothing=5,              # Smoothing level (1-10)
    gesture_cooldown=0.25,            # Seconds between gestures
    show_debug=True,                  # Show debug info
)

# Create and run controller
controller = GestifyController(config)
controller.run()
```

## 📖 Gesture Reference

| Gesture | Hand Shape | Action | Notes |
|---------|-----------|---------|-------|
| **Cursor Move** | ☝️ Only index finger extended | Move mouse cursor | Smooth, precise tracking |
| **Click** | 👌 Quick pinch (thumb + index) | Left click | Release immediately |
| **Double Click** | 👌👌 Two quick pinches | Double left click | Within 0.5 seconds |
| **Drag** | ✌️ Peace sign (index + middle) | Click and drag | Keep peace sign while moving |
| **Drag End** | Change from peace to any other | Release drag | Automatically releases |
| **Scroll** | ✊ Fist moving up/down | Scroll | Speed = hand velocity |
| **Pause/Play** | 🖐️ All 5 fingers extended | Press Space | Toggle media playback |
| **Confirm** | 👍 Thumbs up | Press Enter | Accept/submit |
| **Cancel** | 👎 Thumbs down | Press Escape | Cancel/back |
| **Zoom In** | 🤲 Two hands moving apart | Cmd/Ctrl + | Requires two-hand mode |
| **Zoom Out** | 🤲 Two hands moving together | Cmd/Ctrl - | Requires two-hand mode |
| **Rotate CW** | 🤲 Rotate both hands clockwise | Rotate right | Application specific |
| **Rotate CCW** | 🤲 Rotate both hands counter-clockwise | Rotate left | Application specific |

## ⚙️ Configuration

### Preset Modes

#### Fast Mode
Optimized for speed and responsiveness:
```python
config = GestifyConfig.fast_mode()
```
- Single hand only
- Lite hand model
- No face tracking
- Less cursor smoothing

#### Accurate Mode
Optimized for precision:
```python
config = GestifyConfig.accurate_mode()
```
- Higher confidence thresholds
- Full hand model
- Face tracking enabled
- More cursor smoothing

#### Two-Hand Mode
Optimized for two-hand gestures:
```python
config = GestifyConfig.two_hand_mode()
```
- Detects 2 hands
- Two-hand gestures enabled
- Face tracking enabled

### Custom Configuration Options

```python
config = GestifyConfig(
    # Camera settings
    camera_index=0,              # Camera device index
    camera_width=640,            # Frame width
    camera_height=480,           # Frame height
    camera_fps=30,               # Target FPS
    
    # Hand detection
    max_hands=2,                 # 1 or 2 hands
    hand_confidence=0.7,         # Detection confidence (0-1)
    hand_tracking_confidence=0.5, # Tracking confidence (0-1)
    hand_model_complexity=0,     # 0=lite, 1=full
    
    # Face tracking
    enable_face_tracking=True,   # Enable attention detection
    face_confidence=0.5,         # Face detection confidence
    attention_threshold=3,       # Frames needed for attention
    
    # Gesture settings
    gesture_cooldown=0.25,       # Seconds between gestures
    cursor_smoothing=5,          # Cursor smoothing frames (1-10)
    pinch_threshold=20,          # Pinch distance (pixels)
    
    # Two-hand gestures
    enable_two_hand=True,        # Enable two-hand gestures
    
    # UI settings
    show_ui=True,                # Show camera window
    show_debug=False,            # Show debug info
    show_fps=True,               # Show FPS counter
)
```

## 🎯 Use Cases

### Presentations
- Control slides with gestures
- Pause/play videos with open palm
- Navigate with thumbs up/down

### Media Playback
- Control video player without touching keyboard
- Scroll through content with fist gestures
- Pause/play with palm gesture

### Accessibility
- Alternative input method for users with limited keyboard access
- Hands-free computer control
- Customizable gesture mappings

### Gaming & VR
- Natural gesture controls
- Immersive interaction
- Prototype gesture-based interfaces

## 🏗️ Library Structure

```
gestify/
├── gestify_lib/                    # Main library package
│   ├── __init__.py                # Package exports
│   ├── __main__.py                # CLI entry point
│   ├── core/                      # Core components
│   │   ├── controller.py          # Main controller
│   │   └── config.py              # Configuration management
│   ├── detectors/                 # Detection modules
│   │   ├── hand_detector.py       # Hand detection (MediaPipe)
│   │   ├── face_detector.py       # Face & attention tracking
│   │   └── gesture_recognizer.py  # Gesture recognition logic
│   └── utils/                     # Utility modules
│       ├── action_executor.py     # System action execution
│       └── ui_renderer.py         # UI rendering
├── examples/                      # Example scripts
│   ├── basic_usage.py
│   ├── custom_config.py
│   └── two_hand_mode.py
├── setup.py                       # Package setup
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## 🔧 Development

### Project Structure

The library is organized into distinct modules:

- **`core/`**: Main controller and configuration
- **`detectors/`**: Hand, face, and gesture detection
- **`utils/`**: System actions and UI rendering

### Adding Custom Gestures

To add a new gesture, modify `gesture_recognizer.py`:

```python
# 1. Add gesture to enum
class Gesture(Enum):
    MY_GESTURE = auto()

# 2. Add recognition logic
def _recognize_single_hand(self, state: HandState) -> Gesture:
    # Your detection logic here
    if state.fingers_extended == [True, True, False, False, False]:
        return Gesture.MY_GESTURE
    ...

# 3. Add action to action_executor.py
def execute(self, gesture: Gesture, cursor_pos=None):
    if gesture == Gesture.MY_GESTURE:
        # Your action here
        pyautogui.press('f')
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when available)
pytest tests/

# Run linting
flake8 gestify_lib/
black gestify_lib/
```

## 🐛 Troubleshooting

### Camera Issues

**Problem**: Camera not found or not opening

**Solutions**:
1. Check if another app is using the camera (Zoom, FaceTime, etc.)
2. Grant camera permissions in System Preferences (macOS)
3. Try different camera index: `gestify --camera 1`
4. Run camera fix script: `python fix_camera.sh`

### Permission Issues (macOS)

**Problem**: Gestures not controlling system

**Solutions**:
1. Grant Accessibility permissions: System Preferences → Security & Privacy → Privacy → Accessibility
2. Grant Screen Recording permissions (for cursor control)

### Performance Issues

**Problem**: Low FPS or laggy gestures

**Solutions**:
1. Use fast mode: `gestify --fast`
2. Disable face tracking: `gestify --no-face`
3. Reduce camera resolution: `gestify --width 320 --height 240`
4. Use single hand: `gestify --max-hands 1`
5. Close other resource-intensive applications

### Gesture Detection Issues

**Problem**: Gestures not recognized reliably

**Solutions**:
1. Ensure good lighting
2. Keep hand at comfortable distance from camera (30-60cm)
3. Use accurate mode: `gestify --accurate`
4. Increase confidence threshold: `gestify --hand-confidence 0.8`
5. Make gestures more distinct and deliberate

## 💡 Tips for Best Experience

1. **Lighting**: Ensure good, even lighting on your hands
2. **Distance**: Keep hands 30-60cm from camera
3. **Background**: Plain background helps detection
4. **Distinct Gestures**: Make clear, deliberate gestures
5. **Practice**: Spend a few minutes learning gesture shapes
6. **Calibration**: Adjust `cursor_smoothing` and `gesture_cooldown` to your preference

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup

```bash
# Clone repo
git clone https://github.com/ranjeetds/gestify.git
cd gestify

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Make changes and test
python -m gestify_lib
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MediaPipe**: Hand and face detection
- **OpenCV**: Computer vision and camera capture
- **PyAutoGUI**: System control and automation

## 🔮 Future Enhancements

- [ ] Custom gesture recording and training
- [ ] Gesture macros and scripting
- [ ] Multi-monitor support
- [ ] Voice command integration
- [ ] Mobile app for remote control
- [ ] Plugin system for custom actions
- [ ] Gesture history and analytics
- [ ] Pre-trained gesture models
- [ ] Web interface for configuration

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub:
https://github.com/ranjeetds/gestify/issues

---

**Made with ❤️ by the Gestify team**

*Control your computer naturally with the power of AI*
