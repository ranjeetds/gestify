# 🚀 Gestify v2.0 - Quick Start Guide

## Installation

```bash
# 1. Clone and navigate
git clone https://github.com/ranjeetds/gestify.git
cd gestify

# 2. Run setup (automated)
chmod +x setup.sh
./setup.sh
```

## Basic Usage

### Option 1: Command Line (Recommended)

```bash
# Activate environment
source venv/bin/activate

# Run with default settings
gestify

# Run in fast mode (best for M1 Pro)
gestify --fast

# Run without face tracking (more responsive)
gestify --no-face
```

### Option 2: Python Script

```bash
python run_gestify.py
```

### Option 3: Python API

```python
from gestify_lib import GestifyController

controller = GestifyController()
controller.run()
```

## Gestures at a Glance

| Gesture | How | Action |
|---------|-----|--------|
| **Move Cursor** | ☝️ Index finger only | Move mouse |
| **Click** | 👌 Quick pinch | Left click |
| **Double Click** | 👌👌 Two quick pinches | Double click |
| **Drag** | ✌️ Peace sign (hold) | Drag item |
| **Scroll** | ✊ Fist up/down | Scroll page |
| **Pause** | 🖐️ Open palm | Space bar |
| **Confirm** | 👍 Thumbs up | Enter |
| **Cancel** | 👎 Thumbs down | Escape |

### Two-Hand Gestures (with `--two-hand`)

| Gesture | How | Action |
|---------|-----|--------|
| **Zoom In** | 🤲 Hands apart | Cmd/Ctrl + |
| **Zoom Out** | 🤲 Hands together | Cmd/Ctrl - |
| **Rotate** | 🤲 Rotate hands | Rotate gesture |

## Configuration

### Quick Presets

```bash
gestify --fast       # Speed optimized (M1 Pro)
gestify --accurate   # Precision optimized
gestify --two-hand   # Two-hand gestures enabled
```

### Custom Configuration

```python
from gestify_lib import GestifyController, GestifyConfig

config = GestifyConfig(
    max_hands=1,                     # Single hand
    enable_face_tracking=False,      # No attention tracking
    hand_model_complexity=0,         # Lite model (faster)
    cursor_smoothing=3,              # Less smoothing
    gesture_cooldown=0.2,            # Faster response
)

controller = GestifyController(config)
controller.run()
```

## Keyboard Controls

While running:
- **Q** or **ESC**: Quit
- **D**: Toggle debug info
- **F**: Toggle face tracking

## Troubleshooting

### Camera Not Working
```bash
python fix_camera.sh
```

### Permissions (macOS)
1. **System Preferences** → **Security & Privacy** → **Privacy**
2. Grant permissions for:
   - Camera
   - Accessibility
   - Screen Recording

### Low Performance
- Use `--fast` mode
- Disable face tracking: `--no-face`
- Reduce camera resolution: `--width 320 --height 240`

## Tips for Best Experience

1. **Lighting**: Good, even lighting
2. **Distance**: 30-60cm from camera
3. **Background**: Plain background helps
4. **Gestures**: Clear, deliberate movements
5. **Practice**: Spend 2-3 minutes learning gestures

## Examples

See `examples/` directory:
- `basic_usage.py` - Simple default usage
- `custom_config.py` - Custom configuration
- `two_hand_mode.py` - Two-hand gestures

## Next Steps

- Read full [README.md](README.md) for comprehensive guide
- Check [CHANGELOG.md](CHANGELOG.md) for v2.0 changes
- Explore example scripts in `examples/`
- Customize configuration for your needs

## Getting Help

- **Issues**: https://github.com/ranjeetds/gestify/issues
- **Documentation**: See README.md
- **Examples**: See `examples/` directory

---

**Happy gesturing! 🎮**

