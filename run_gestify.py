#!/usr/bin/env python3
"""
Simple launcher for Gestify
"""

from gestify_lib import GestifyController

if __name__ == '__main__':
    print("🎮 Starting Gestify...")
    controller = GestifyController()
    controller.run()

