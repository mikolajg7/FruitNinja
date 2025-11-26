import pygame
from .config import *


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, font):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hover_timer = 0
        self.required_hover_time = BUTTON_HOVER_TIME
        self.triggered = False

    def update(self, cursors):
        is_hovered = False

        if cursors:
            for cursor in cursors:
                if self.rect.colliderect(cursor.rect):
                    is_hovered = True
                    break

        if is_hovered:
            self.hover_timer += 1
            if self.hover_timer >= self.required_hover_time:
                self.hover_timer = 0
                self.triggered = True
                return True
        else:
            self.hover_timer = 0
            self.triggered = False

        return False

    def draw(self, screen):
        progress = min(self.hover_timer / self.required_hover_time, 1.0)

        base = BTN_BASE_COLOR
        active = BTN_ACTIVE_COLOR
        border_col = BTN_BORDER_COLOR

        if progress > 0:
            # Interpolacja
            curr_r = int(base[0] + (active[0] - base[0]) * progress)
            curr_g = int(base[1] + (active[1] - base[1]) * progress)
            curr_b = int(base[2] + (active[2] - base[2]) * progress)
            current_color = (curr_r, curr_g, curr_b)
            border_width = 3 + int(5 * progress)
        else:
            current_color = base
            border_width = 2

        pygame.draw.rect(screen, current_color, self.rect, border_radius=20)
        pygame.draw.rect(screen, border_col, self.rect, border_width, border_radius=20)

        # Tekst
        text_surf = self.font.render(self.text, True, BTN_TEXT_COLOR)
        shadow_surf = self.font.render(self.text, True, BLACK)

        center_x, center_y = self.rect.center
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        shad_rect = shadow_surf.get_rect(center=(center_x + 2, center_y + 2))

        screen.blit(shadow_surf, shad_rect)
        screen.blit(text_surf, text_rect)

        if progress > 0:
            bw = self.rect.width * progress
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.bottom + 5, bw, 5), border_radius=5)
