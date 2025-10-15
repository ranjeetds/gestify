#!/usr/bin/env python3
"""
AR Puzzle Game Example

A simple AR game where you pick up shapes and place them in matching zones
using hand gestures.

Controls:
- Point finger: Move cursor
- Pinch: Pick/place objects
- Peace sign: Drag objects
- Open palm: Pause
- Press 'R': Restart puzzle
- Press 'Q' or ESC: Quit

Run with:
    python examples/ar_puzzle_game.py
    
Or with difficulty:
    python examples/ar_puzzle_game.py easy
    python examples/ar_puzzle_game.py medium
    python examples/ar_puzzle_game.py hard
"""

import sys
from gestify_lib.games import ARGameController


def main():
    # Get difficulty from command line or use default
    difficulty = "easy"
    if len(sys.argv) > 1:
        difficulty = sys.argv[1].lower()
        if difficulty not in ["easy", "medium", "hard"]:
            print(f"Unknown difficulty: {difficulty}")
            print("Valid options: easy, medium, hard")
            difficulty = "easy"
    
    print(f"\n🎮 Starting AR Puzzle Game (Difficulty: {difficulty})")
    print("=" * 60)
    print("Make sure you have good lighting and your camera can see you!")
    print("=" * 60)
    
    try:
        # Initialize game controller
        # For HD 1080p: game_width=1920, game_height=1080
        # For 720p: game_width=1280, game_height=720
        controller = ARGameController(
            game_width=1920,
            game_height=1080,
            difficulty=difficulty
        )
        
        # Run game
        controller.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Game interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("   1. Make sure your camera is not being used by another app")
        print("   2. Check camera permissions in System Preferences")
        print("   3. Try lowering the resolution to 720p")
        print("   4. Ensure you have good lighting")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

