#!/usr/bin/env python3
"""
AR Ping Pong Game Example

A two-player AR ping pong game where players use their hands to control paddles.

How to Play:
- LEFT PLAYER: Show hand on left side of screen
- RIGHT PLAYER: Show hand on right side of screen  
- Move hand UP/DOWN to control your paddle
- First to 11 points wins!

Run with:
    python examples/ar_ping_pong.py
    python run_pingpong.py
"""

import sys
from gestify_lib.games import PingPongGameController


def main():
    print("\n🏓 Starting AR Ping Pong Game")
    print("=" * 60)
    print("Two-Player Hand-Controlled Ping Pong!")
    print("=" * 60)
    print("\nSetup:")
    print("  1. Two players needed")
    print("  2. LEFT player: Show hand on LEFT side")
    print("  3. RIGHT player: Show hand on RIGHT side")
    print("  4. Move hands UP/DOWN to control paddles")
    print("\nRules:")
    print("  • First to 11 points wins")
    print("  • Ball speeds up with each hit")
    print("  • Don't let ball go past your paddle!")
    print("\nControls:")
    print("  • R - Restart game")
    print("  • Q or ESC - Quit")
    print("=" * 60)
    
    try:
        # Initialize game controller
        controller = PingPongGameController(
            game_width=1920,
            game_height=1080
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
        print("   3. Ensure you have good lighting")
        print("   4. Make sure both hands are visible")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

