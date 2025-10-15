# Changelog

All notable changes to Gestify will be documented in this file.

## [2.0.0] - 2025-10-15

### 🎉 Major Release - Complete Rewrite

This is a complete rewrite of Gestify as a professional, object-oriented library.

### ✨ Added

#### Architecture
- **Object-Oriented Design**: Complete modular architecture with clean separation of concerns
- **Library Structure**: Proper Python package with installable setup
- **CLI Tool**: Full command-line interface with multiple options
- **Configuration System**: Comprehensive config management with presets
- **Example Scripts**: Multiple examples demonstrating different use cases

#### Core Features
- **Simplified Gestures**: 13 distinct, non-overlapping gestures
  - Cursor Move (index finger)
  - Click & Double Click (pinch)
  - Drag & Drop (peace sign)
  - Scroll (fist)
  - Pause (open palm)
  - Confirm/Cancel (thumbs up/down)
  - Two-hand gestures (zoom, rotate)

- **Attention Detection**: Face tracking to prevent unintentional actions
- **Two-Hand Support**: Advanced gestures using both hands
- **Smart Features**:
  - Gesture cooldown prevention
  - Cursor smoothing
  - Velocity-based scrolling
  - State tracking for drag operations

#### Components
- **Core**:
  - `GestifyController`: Main orchestration class
  - `GestifyConfig`: Configuration management with presets

- **Detectors**:
  - `HandDetector`: MediaPipe-based hand tracking
  - `FaceDetector`: Face landmark detection
  - `AttentionTracker`: Eye gaze estimation
  - `GestureRecognizer`: Intelligent gesture recognition

- **Utils**:
  - `ActionExecutor`: System action execution
  - `UIRenderer`: Camera feed visualization

#### Developer Experience
- **Examples**: 3 comprehensive example scripts
- **Documentation**: Professional README with extensive guides
- **Setup Scripts**: Automated setup with `setup.sh`
- **Testing**: Environment verification with `test_setup.py`
- **Packaging**: Proper `setup.py` for pip installation

### 🔄 Changed

- **Gesture Set**: Redesigned from overlapping to distinct gestures
- **Dependencies**: Simplified to core libraries only (removed Ollama/Transformers)
- **Performance**: Optimized with lite model option and configurable complexity
- **UI**: Enhanced visualization with FPS counter, debug info, and status indicators

### 🗑️ Removed

- **Old Scripts**: Removed `gestify.py`, `gestify_enhanced.py`, `gestify_v2.py`
- **AI Integration**: Removed Ollama and Qwen dependencies (kept simple and focused)
- **Redundant Docs**: Consolidated multiple markdown files into single README
- **Swift Code**: Removed all macOS-specific Swift implementation

### 🐛 Fixed

- Camera initialization reliability
- Gesture detection accuracy
- Cursor jitter issues
- Memory leaks in detector cleanup
- Thread safety in UI rendering

### 📚 Documentation

- Comprehensive README with:
  - Quick start guide
  - Detailed gesture reference
  - Configuration options
  - Troubleshooting section
  - Development guide
- Inline code documentation
- Type hints throughout

### 🎯 Migration from v1.x

If you're using the old version:

1. **Backup your customizations**
2. **Install v2.0**: `pip install -e .`
3. **Use the new API**:

```python
# Old way
from gestify import GestureController
controller = GestureController()

# New way
from gestify_lib import GestifyController
controller = GestifyController()
controller.run()
```

4. **Check the examples** in the `examples/` directory

---

## [1.0.0] - 2025-10-14

### Initial Release

- Basic hand gesture recognition
- MediaPipe integration
- PyAutoGUI system control
- Optional Ollama AI assistance
- 7 core gestures

---

**Note**: Version 2.0.0 is not backward compatible with 1.x due to complete architectural changes.

