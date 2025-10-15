#!/usr/bin/env python3
"""
Quick launcher for AR Ping Pong Game
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gestify_lib.games import PingPongGameController


def main():
    print("\n" + "=" * 60)
    print("🏓  AR PING PONG - Two Player Game")
    print("=" * 60)
    print("\nGet Ready:")
    print("  LEFT PLAYER: Show hand on LEFT side")
    print("  RIGHT PLAYER: Show hand on RIGHT side")
    print("  Move UP/DOWN to control paddles")
    print("\nFirst to 11 wins!")
    print("=" * 60)
    print("\n⏳ Starting game...\n")
    
    try:
        # Create and run game
        controller = PingPongGameController(
            game_width=1920,
            game_height=1080
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
        print("   - Make sure both players are visible")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

