#!/usr/bin/env python3
"""
Quick launcher for AR Piano
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gestify_lib.games import ARPianoController


def main():
    print("\n" + "=" * 60)
    print("🎹  AR PIANO - Play with Your Hands!")
    print("=" * 60)
    print("\nGet Ready:")
    print("  • Position hands above piano keys")
    print("  • Touch keys with fingertips to play")
    print("  • Select a song (1-4) and follow the notes")
    print("\n4 Songs Available:")
    print("  1. Happy Birthday")
    print("  2. Twinkle Twinkle Little Star")
    print("  3. Mary Had a Little Lamb")
    print("  4. Jingle Bells")
    print("=" * 60)
    print("\n⏳ Starting AR Piano...\n")
    
    try:
        # Create and run piano
        controller = ARPianoController(
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
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

