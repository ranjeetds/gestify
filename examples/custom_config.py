"""
Custom configuration example for Gestify
"""

from gestify_lib import GestifyController, GestifyConfig

def main():
    """Run Gestify with custom configuration"""
    
    # Create custom config
    config = GestifyConfig(
        max_hands=1,                     # Single hand only
        enable_face_tracking=False,       # Disable face tracking for speed
        hand_model_complexity=0,          # Use lite model
        cursor_smoothing=3,              # Less smoothing = more responsive
        gesture_cooldown=0.2,             # Faster gesture repetition
        show_debug=True,                  # Show debug info
    )
    
    # Create controller with custom config
    controller = GestifyController(config)
    
    # Run gesture control
    controller.run()

if __name__ == '__main__':
    main()

