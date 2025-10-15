#!/usr/bin/env python3
"""
Realistic AR Piano Game Example

A realistic AR piano with ALL finger tracking and real sound!

Revolutionary Features:
- Tracks all 10 fingers simultaneously (all fingertips on both hands)
- Real piano sound generation with harmonics
- Motion-based key detection (press by moving finger DOWN)
- 100% gesture-controlled interface (no keyboard needed)
- Hover-to-select menu system
- Vertical piano keyboard layout

How to Play:
- Hold hands above the vertical piano keyboard
- Move ANY finger downward to press keys (like real piano)
- Fast downward motion triggers the key press
- All 10 fingers work independently!

Song Learning Mode:
- Hover hand over song name for 1.5 seconds to select
- Follow falling notes down the screen
- Press keys when notes reach the HIT zone
- Build combos for higher scores

Gesture Controls:
- Hover + dwell: Select menu items (1.5 seconds)
- Open palm: Return to main menu
- ESC key: Quit (only keyboard shortcut)

Songs Available:
- Happy Birthday
- Twinkle Twinkle Little Star
- Mary Had a Little Lamb
- Jingle Bells

Run with:
    python examples/ar_piano.py
    python run_piano.py
"""

import sys
from gestify_lib.games import RealisticARPianoController


def main():
    print("\n🎹 Starting Realistic AR Piano")
    print("=" * 60)
    print("Play realistic piano with gesture controls!")
    print("=" * 60)
    print("\n✨ Features:")
    print("  ✓ All 10 fingers tracked")
    print("  ✓ Real piano sounds")
    print("  ✓ Motion-based key presses")
    print("  ✓ Gesture-only interface")
    print("\nHow to Play:")
    print("  1. Hold hands above piano keyboard")
    print("  2. Move fingers DOWN to press keys")
    print("  3. Any finger can press any key!")
    print("  4. Hover over songs to select (1.5s)")
    print("\nScoring:")
    print("  • Hit notes in the HIT zone")
    print("  • Build combos by hitting consecutive notes")
    print("  • Higher combos = more points!")
    print("\nGestures:")
    print("  • Hover: Select song (dwell time)")
    print("  • Open palm: Return to menu")
    print("  • ESC: Quit")
    print("=" * 60)
    
    try:
        # Initialize realistic piano controller
        controller = RealisticARPianoController(
            game_width=1920,
            game_height=1080
        )
        
        # Run piano
        controller.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Piano interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("   1. Install pygame: pip install pygame")
        print("   2. Check camera permissions")
        print("   3. Close other apps using camera")
        print("   4. Ensure good lighting")
        print("   5. Keep both hands visible")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

