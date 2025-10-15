"""
CLI entry point for Gestify
"""

import argparse
import sys
from .core.config import GestifyConfig
from .core.controller import GestifyController


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Gestify - AI-Powered Hand Gesture Control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                    # Run with default settings
  %(prog)s --fast             # Fast mode (single hand, no face tracking)
  %(prog)s --accurate         # Accurate mode (higher confidence thresholds)
  %(prog)s --two-hand         # Two-hand gesture mode
  %(prog)s --no-ui            # Run without camera window
  %(prog)s --camera 1         # Use camera index 1
  
Gestures:
  ☝️  Index finger: Move cursor
  ✌️  Peace sign: Drag
  👌 Pinch: Click (quick pinch twice for double-click)
  ✊ Fist moving: Scroll
  🖐️  Open palm: Pause/Play (Space)
  👍 Thumbs up: Confirm (Enter)
  👎 Thumbs down: Cancel (Escape)
  🤲 Two hands: Zoom in/out, Rotate
  
Controls:
  Q or ESC: Quit
  D: Toggle debug info
  F: Toggle face tracking
        '''
    )
    
    # Preset modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--fast', action='store_true',
                           help='Fast mode (optimized for speed)')
    mode_group.add_argument('--accurate', action='store_true',
                           help='Accurate mode (optimized for accuracy)')
    mode_group.add_argument('--two-hand', action='store_true',
                           help='Two-hand mode (enable two-hand gestures)')
    
    # Camera settings
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--width', type=int, default=640,
                       help='Camera width (default: 640)')
    parser.add_argument('--height', type=int, default=480,
                       help='Camera height (default: 480)')
    parser.add_argument('--fps', type=int, default=30,
                       help='Camera FPS (default: 30)')
    
    # Feature toggles
    parser.add_argument('--no-face', action='store_true',
                       help='Disable face tracking')
    parser.add_argument('--no-ui', action='store_true',
                       help='Disable camera window')
    parser.add_argument('--debug', action='store_true',
                       help='Show debug information')
    
    # Advanced settings
    parser.add_argument('--max-hands', type=int, choices=[1, 2], default=2,
                       help='Maximum hands to detect (default: 2)')
    parser.add_argument('--hand-confidence', type=float, default=0.7,
                       help='Hand detection confidence (0-1, default: 0.7)')
    parser.add_argument('--cooldown', type=float, default=0.25,
                       help='Gesture cooldown in seconds (default: 0.25)')
    parser.add_argument('--smoothing', type=int, default=5,
                       help='Cursor smoothing frames (default: 5)')
    
    args = parser.parse_args()
    
    # Create configuration
    if args.fast:
        config = GestifyConfig.fast_mode()
    elif args.accurate:
        config = GestifyConfig.accurate_mode()
    elif args.two_hand:
        config = GestifyConfig.two_hand_mode()
    else:
        config = GestifyConfig()
    
    # Apply custom settings
    config.camera_index = args.camera
    config.camera_width = args.width
    config.camera_height = args.height
    config.camera_fps = args.fps
    
    if args.no_face:
        config.enable_face_tracking = False
    if args.no_ui:
        config.show_ui = False
    if args.debug:
        config.show_debug = True
    
    config.max_hands = args.max_hands
    config.hand_confidence = args.hand_confidence
    config.gesture_cooldown = args.cooldown
    config.cursor_smoothing = args.smoothing
    
    # Print banner
    print("=" * 60)
    print("🎮 Gestify - AI-Powered Hand Gesture Control v2.0")
    print("=" * 60)
    print(f"\n⚙️  Configuration:")
    print(f"   Mode: {'Fast' if args.fast else 'Accurate' if args.accurate else 'Two-Hand' if args.two_hand else 'Default'}")
    print(f"   Camera: {config.camera_index} ({config.camera_width}x{config.camera_height} @ {config.camera_fps}fps)")
    print(f"   Max hands: {config.max_hands}")
    print(f"   Face tracking: {'Enabled' if config.enable_face_tracking else 'Disabled'}")
    print(f"   UI: {'Enabled' if config.show_ui else 'Disabled'}")
    print()
    
    # Run controller
    try:
        controller = GestifyController(config)
        controller.run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

