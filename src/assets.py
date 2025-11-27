import pygame
import os
from .config import *


class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.images = {}
            cls._instance.fonts = {}
            cls._instance.load_assets()
        return cls._instance

    def load_assets(self):
        # 1. Czcionki
        try:
            self.fonts['big'] = pygame.font.Font(FONT_PATH, 90)
            self.fonts['medium'] = pygame.font.Font(FONT_PATH, 65)
            self.fonts['small'] = pygame.font.Font(FONT_PATH, 40)
            self.fonts['tiny'] = pygame.font.Font(FONT_PATH, 30)
        except:
            print("Using system font fallback")
            self.fonts['big'] = pygame.font.SysFont("Arial", 80, bold=True)
            self.fonts['medium'] = pygame.font.SysFont("Arial", 60, bold=True)
            self.fonts['small'] = pygame.font.SysFont("Arial", 40)
            self.fonts['tiny'] = pygame.font.SysFont("Arial", 30)

        # 2. Obrazy
        self._load_image(os.path.join(BOMB_DIR, "bomb.png"), key="bomb")
        self._load_image(os.path.join(BOMB_DIR, "boom.png"), key="boom")

        for f in FRUIT_TYPES:
            self._load_image(os.path.join(FRUIT_DIR, f"{f}.png"), key=f)
            self._load_image(os.path.join(FRUIT_DIR, f"{f}-sliced.png"), key=f"{f}-sliced")

    def _load_image(self, filename, key=None):
        if key is None: key = filename.split('.')[0]
        try:
            img = pygame.image.load(filename).convert_alpha()
            self.images[key] = img
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            surf = pygame.Surface((100, 100))
            surf.fill(RED)
            self.images[key] = surf

    def get_image(self, key):
        return self.images.get(key)

    def get_font(self, size_key):
        return self.fonts.get(size_key)