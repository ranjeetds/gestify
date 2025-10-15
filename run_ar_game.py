#!/usr/bin/env python3
"""
Quick launcher for AR Puzzle Game

This is a convenience script to quickly launch the AR puzzle game.
For more options, use the example script directly.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gestify_lib.games import ARGameController


def main():
    difficulty = "easy"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        difficulty = sys.argv[1].lower()
    
    print("\n" + "=" * 60)
    print("🎮  GESTIFY AR PUZZLE GAME")
    print("=" * 60)
    print(f"Difficulty: {difficulty.upper()}")
    print("\nControls:")
    print("  👆 Point finger - Move cursor")
    print("  👌 Pinch - Pick/place objects")
    print("  ✌️  Peace sign - Drag objects")
    print("  Q or ESC - Quit")
    print("  R - Restart")
    print("=" * 60)
    print("\n⏳ Starting game...\n")
    
    try:
        # Create and run game
        controller = ARGameController(
            game_width=1920,
            game_height=1080,
            difficulty=difficulty
        )
        controller.run()
        
    except KeyboardInterrupt:
        print("\n\n✋ Game interrupted by user")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try:")
        print("   - Close other apps using the camera")
        print("   - Check camera permissions")
        print("   - Ensure good lighting")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

