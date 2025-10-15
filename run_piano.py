#!/usr/bin/env python3
"""
Quick launcher for Realistic AR Piano with gesture controls
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gestify_lib.games import RealisticARPianoController


def main():
    print("\n" + "=" * 60)
    print("🎹  REALISTIC AR PIANO - All Fingers, Real Sound!")
    print("=" * 60)
    print("\n✨ Revolutionary Features:")
    print("  • Track ALL 10 fingers simultaneously")
    print("  • Real piano sound generation")
    print("  • Motion-based key presses (move finger DOWN)")
    print("  • 100% gesture control (no keyboard needed)")
    print("\n🎵 How to Play:")
    print("  1. Hold hands above the vertical piano")
    print("  2. Move ANY finger DOWN to press a key")
    print("  3. Hear real piano sounds!")
    print("  4. Hover over song in menu to select (1.5s)")
    print("  5. Follow falling notes when song plays")
    print("\n🎮 Gestures:")
    print("  • Hover: Select song (dwell 1.5 seconds)")
    print("  • Open palm: Return to menu")
    print("  • ESC: Quit")
    print("\n🎼 4 Songs Available:")
    print("  • Happy Birthday")
    print("  • Twinkle Twinkle Little Star")
    print("  • Mary Had a Little Lamb")
    print("  • Jingle Bells")
    print("=" * 60)
    print("\n⏳ Starting Realistic AR Piano...\n")
    
    try:
        # Create and run piano
        controller = RealisticARPianoController(
            game_width=1920,
            game_height=1080
        )
        controller.run()
        
    except KeyboardInterrupt:
        print("\n\n✋ Piano interrupted by user")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try:")
        print("   - Close other apps using the camera")
        print("   - Check camera permissions")
        print("   - Ensure good lighting")
        print("   - Keep hands visible")
        print("   - Install pygame: pip install pygame")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

