"""
Basic usage example for Gestify
"""

from gestify_lib import GestifyController, GestifyConfig

def main():
    """Run Gestify with default settings"""
    # Create controller with default config
    controller = GestifyController()
    
    # Run gesture control
    controller.run()

if __name__ == '__main__':
    main()

