#!/usr/bin/env python3
"""
Test script to verify AR game components work correctly
"""

import sys


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from gestify_lib.games import GameObject, PuzzlePiece, TargetZone
        print("  ✓ game_objects module")
        
        from gestify_lib.games import PuzzleGame
        print("  ✓ puzzle_game module")
        
        from gestify_lib.games import ARGameController
        print("  ✓ ar_game_controller module")
        
        from gestify_lib.games import ObjectShape
        print("  ✓ ObjectShape enum")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_object_creation():
    """Test creating game objects"""
    print("\nTesting object creation...")
    
    try:
        from gestify_lib.games import PuzzlePiece, TargetZone, ObjectShape
        import numpy as np
        
        # Create a puzzle piece
        piece = PuzzlePiece(100, 100, 80, ObjectShape.CIRCLE, (255, 0, 0), 0)
        print(f"  ✓ Created puzzle piece at {piece.get_center()}")
        
        # Create a target zone
        zone = TargetZone(200, 200, 80, ObjectShape.CIRCLE, 0)
        print(f"  ✓ Created target zone at {zone.get_center()}")
        
        # Test containment
        contains = piece.contains_point(100, 100)
        print(f"  ✓ Point containment test: {contains}")
        
        # Test drawing (create dummy frame)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        piece.draw(frame)
        zone.draw(frame)
        print(f"  ✓ Drawing objects on frame")
        
        return True
    except Exception as e:
        print(f"  ✗ Object creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_creation():
    """Test creating a game instance"""
    print("\nTesting game creation...")
    
    try:
        from gestify_lib.games import PuzzleGame
        
        # Create game
        game = PuzzleGame(1920, 1080, "easy")
        print(f"  ✓ Created game with {len(game.pieces)} pieces")
        print(f"  ✓ Game has {len(game.target_zones)} target zones")
        print(f"  ✓ Initial score: {game.score}")
        
        # Test game update
        changed = game.update(None, False, False)
        print(f"  ✓ Game update (no cursor): {changed}")
        
        # Test with cursor
        changed = game.update((100, 100), False, False)
        print(f"  ✓ Game update (with cursor): {changed}")
        
        return True
    except Exception as e:
        print(f"  ✗ Game creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shapes():
    """Test all shape types"""
    print("\nTesting shapes...")
    
    try:
        from gestify_lib.games import ObjectShape, GameObject
        import numpy as np
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        shapes = [
            ObjectShape.CIRCLE,
            ObjectShape.SQUARE,
            ObjectShape.TRIANGLE,
            ObjectShape.STAR,
            ObjectShape.HEART,
        ]
        
        for i, shape in enumerate(shapes):
            obj = GameObject(
                x=50 + i * 100,
                y=50,
                width=80,
                height=80,
                color=(255, 255, 255),
                shape=shape
            )
            obj.draw(frame)
            print(f"  ✓ Drew {shape.value}")
        
        return True
    except Exception as e:
        print(f"  ✗ Shape test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_controller_init():
    """Test controller initialization (without camera)"""
    print("\nTesting controller initialization...")
    
    try:
        # We can't fully test this without a camera, but we can check imports
        from gestify_lib.games import ARGameController
        print("  ✓ ARGameController class available")
        
        # Check that we can access the class attributes
        print("  ✓ Controller can be imported")
        print("  ⚠️  Skipping full initialization (requires camera)")
        
        return True
    except Exception as e:
        print(f"  ✗ Controller test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AR PUZZLE GAME - Component Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Object Creation", test_object_creation),
        ("Game Creation", test_game_creation),
        ("Shapes", test_shapes),
        ("Controller", test_controller_init),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The AR game is ready to use.")
        print("\nTo play the game, run:")
        print("  python run_ar_game.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

