import pygame
import random
from .config import *
from .assets import AssetManager


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_key, x, y, vx, vy, size):
        super().__init__()
        assets = AssetManager()

        orig_img = assets.get_image(image_key)
        self.image = pygame.transform.scale(orig_img, size)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = vx
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += GRAVITY

        # Używamy marginesów z configu
        if (self.rect.y > WINDOW_HEIGHT + BOUNDS_MARGIN_Y_BOTTOM or
                self.rect.y < -BOUNDS_MARGIN_Y_TOP or
                self.rect.x < -BOUNDS_MARGIN_X or
                self.rect.x > WINDOW_WIDTH + BOUNDS_MARGIN_X):
            self.kill()


class Fruit(GameObject):
    def __init__(self, x, y, vx, vy, fruit_type, speed_mult=1.0):
        self.fruit_type = fruit_type
        super().__init__(fruit_type, x, y, vx * speed_mult, vy * speed_mult, size=FRUIT_SIZE)


class Slice(GameObject):
    def __init__(self, parent_rect, fruit_type, direction):
        vx = random.randint(2, 6) * direction
        vy = random.randint(-5, 0)
        super().__init__(f"{fruit_type}-sliced", parent_rect.x, parent_rect.y, vx, vy, size=SLICE_SIZE)


class Bomb(GameObject):
    def __init__(self, x, y, vx, vy, speed_mult=1.0):
        super().__init__("bomb", x, y, vx * speed_mult, vy * speed_mult, size=BOMB_SIZE)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__()
        assets = AssetManager()
        orig = assets.get_image("boom")
        self.image = pygame.transform.scale(orig, EXPLOSION_SIZE)
        self.rect = self.image.get_rect(center=center_pos)
        self.life = EXPLOSION_DURATION

    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill()