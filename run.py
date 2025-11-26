import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import GameEngine

if __name__ == "__main__":
    game = GameEngine()
    game.run()