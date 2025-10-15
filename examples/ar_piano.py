#!/usr/bin/env python3
"""
AR Piano Game Example

An AR piano where you play with your hands! Follow falling notes to learn songs.

How to Play:
- Position hands above piano keys on screen
- Touch keys with fingertips to play notes
- Select a song from menu (1-4)
- Follow falling notes and hit keys in rhythm
- Build combos for higher scores!

Songs Available:
1. Happy Birthday
2. Twinkle Twinkle Little Star
3. Mary Had a Little Lamb
4. Jingle Bells

Run with:
    python examples/ar_piano.py
    python run_piano.py
"""

import sys
from gestify_lib.games import ARPianoController


def main():
    print("\n🎹 Starting AR Piano")
    print("=" * 60)
    print("Play piano with your hands!")
    print("=" * 60)
    print("\nHow to Play:")
    print("  1. Position hands above piano keys")
    print("  2. Touch keys with fingertips")
    print("  3. Select a song (press 1-4)")
    print("  4. Follow falling notes")
    print("  5. Hit keys in time with the music")
    print("\nScoring:")
    print("  • Hit notes in the yellow zone for points")
    print("  • Build combos by hitting consecutive notes")
    print("  • Higher combos = more points!")
    print("\nControls:")
    print("  • 1-4: Select song")
    print("  • M: Return to menu")
    print("  • Q or ESC: Quit")
    print("=" * 60)
    
    try:
        # Initialize piano controller
        controller = ARPianoController(
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
        print("   1. Make sure your camera is not being used by another app")
        print("   2. Check camera permissions in System Preferences")
        print("   3. Ensure you have good lighting")
        print("   4. Keep both hands visible to camera")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

