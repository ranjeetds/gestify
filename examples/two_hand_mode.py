"""
Two-hand gesture mode example
"""

from gestify_lib import GestifyController, GestifyConfig

def main():
    """Run Gestify optimized for two-hand gestures"""
    
    # Use two-hand preset configuration
    config = GestifyConfig.two_hand_mode()
    
    # Create controller
    controller = GestifyController(config)
    
    print("🤲 Two-Hand Gesture Mode")
    print("=" * 40)
    print("Supported gestures:")
    print("  🔍 Zoom In: Move both hands apart")
    print("  🔍 Zoom Out: Move both hands together")
    print("  🔄 Rotate: Rotate both hands")
    print()
    
    # Run gesture control
    controller.run()

if __name__ == '__main__':
    main()

