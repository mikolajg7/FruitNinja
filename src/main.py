import pygame
import cv2
import numpy as np
from src.config import *
from src.assets import AssetManager
from src.input import HandTracker
from src.entities import Slice, Explosion
from src.ranking import RankingManager
from src.ui import Button
from src.spawner import Spawner

# Stany gry
STATE_MENU = "menu"
STATE_MODE = "mode"
STATE_GAME = "game"
STATE_OVER = "over"
STATE_RANK = "rank"


class GameEngine:
    def __init__(self):
        pygame.init()

        flags = 0
        if FULLSCREEN_MODE:
            flags = pygame.FULLSCREEN | pygame.SCALED

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

        pygame.display.set_caption(CAPTION)
        if FULLSCREEN_MODE:
            pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

        # 1. Ładowanie zasobów
        self.assets = AssetManager()
        self.assets.load_assets()

        # 2. Inicjalizacja systemów
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, WINDOW_WIDTH)
        self.cap.set(4, WINDOW_HEIGHT)
        self.tracker = HandTracker()
        self.ranking = RankingManager()

        # 3. Grupy Sprite'ów
        self.fruits = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.slices = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        # 4. Spawner
        self.spawner = Spawner(self.fruits, self.bombs)

        # 5. Zmienne stanu
        self.state = STATE_MENU
        self.mode = "arcade"
        self.score = 0
        self.lives = MAX_LIVES
        self.time_left = GAME_TIME
        self.cooldown = 0
        self.player_name = ""
        self.hand_trails = {}
        self.running = True

        # 6. UI
        self._init_ui()

    def _init_ui(self):
        f_big = self.assets.get_font('big')
        f_med = self.assets.get_font('medium')
        f_small = self.assets.get_font('small')

        cx = WINDOW_WIDTH // 2

        # Menu
        self.btns_menu = pygame.sprite.Group()
        self.btns_menu.add(Button(cx - BTN_W_LARGE // 2, 320, BTN_W_LARGE, BTN_H_LARGE, "START", f_big))
        self.btns_menu.add(Button(cx - BTN_W_LARGE // 2, 480, BTN_W_LARGE, BTN_H_LARGE, "RANKING", f_big))

        # Mode
        self.btns_mode = pygame.sprite.Group()
        self.btn_arc = Button(cx - 400, 350, BTN_W_MED, BTN_H_MED, "ARCADE", f_med)
        self.btn_time = Button(cx + 50, 350, BTN_W_MED, BTN_H_MED, "TIME", f_med)
        self.btns_mode.add(self.btn_arc, self.btn_time)
        self.btn_back = Button(cx - 100, 600, 200, 60, "MENU", f_small)

        # Ranking
        self.btns_rank = pygame.sprite.Group()
        self.btns_rank.add(Button(cx - 350, 620, BTN_W_SMALL, BTN_H_SMALL, "ARCADE", f_small))
        self.btns_rank.add(Button(cx + 120, 620, BTN_W_SMALL, BTN_H_SMALL, "TIME", f_small))

    def switch_state(self, new_state):
        self.state = new_state
        self.cooldown = INPUT_COOLDOWN

    def start_game(self, mode):
        self.mode = mode
        self.score = 0
        self.fruits.empty()
        self.bombs.empty()
        self.slices.empty()
        self.explosions.empty()
        self.player_name = ""
        self.spawner.reset()

        if mode == "arcade":
            self.lives = MAX_LIVES
        else:
            self.time_left = GAME_TIME

        self.switch_state(STATE_GAME)

    def update(self, landmarks):
        cursors = []
        if landmarks:
            num_hands = len(landmarks) // HAND_LANDMARKS_COUNT
            for i in range(num_hands):
                idx = i * HAND_LANDMARKS_COUNT + INDEX_FINGER_TIP
                if idx < len(landmarks):
                    c = pygame.sprite.Sprite()
                    c.rect = pygame.Rect(0, 0, CURSOR_HITBOX_SIZE, CURSOR_HITBOX_SIZE)
                    c.rect.center = landmarks[idx]
                    cursors.append(c)

        if self.cooldown > 0:
            self.cooldown -= 1
            cursors = []

        if self.state == STATE_MENU:
            for b in self.btns_menu:
                if b.update(cursors):
                    if b.text == "START":
                        self.switch_state(STATE_MODE)
                    else:
                        self.ranking.set_mode("arcade")
                        self.switch_state(STATE_RANK)

        elif self.state == STATE_MODE:
            if self.btn_back.update(cursors): self.switch_state(STATE_MENU)
            if self.btn_arc.update(cursors): self.start_game("arcade")
            if self.btn_time.update(cursors): self.start_game("time")

        elif self.state == STATE_GAME:
            self._update_gameplay(cursors)

        elif self.state == STATE_OVER:
            self.fruits.update()
            self.slices.update()
            self.explosions.update()

        elif self.state == STATE_RANK:
            if self.btn_back.update(cursors): self.switch_state(STATE_MENU)
            for b in self.btns_rank:
                if b.update(cursors):
                    self.ranking.set_mode(b.text.lower())

    def _update_gameplay(self, cursors):
        self.spawner.update()
        self.fruits.update()
        self.bombs.update()
        self.slices.update()
        self.explosions.update()

        if self.mode == "time":
            self.time_left -= 1 / FPS
            if self.time_left <= 0:
                self.ranking.set_mode("time")
                self.switch_state(STATE_OVER)

        for cursor in cursors:
            hits = pygame.sprite.spritecollide(cursor, self.fruits, True)
            for f in hits:
                self.score += 1
                self.slices.add(Slice(f.rect, f.fruit_type, -1))
                self.slices.add(Slice(f.rect, f.fruit_type, 1))

            hits = pygame.sprite.spritecollide(cursor, self.bombs, True)
            for b in hits:
                self.explosions.add(Explosion(b.rect.center))
                if self.mode == "arcade":
                    self.lives -= 1
                    if self.lives <= 0:
                        self.ranking.set_mode("arcade")
                        self.switch_state(STATE_OVER)
                else:
                    self.score = max(0, self.score - SCORE_BOMB_PENALTY)

    def draw(self, bg_surf, landmarks):
        self.screen.blit(bg_surf, (0, 0)) if bg_surf else self.screen.fill(BLACK)

        self._update_trails_logic(landmarks)
        self._draw_trails()

        if self.state == STATE_MENU:
            self._draw_overlay()
            self._draw_text_centered("FRUIT NINJA CV", 40, self.assets.get_font('big'), GOLD)
            for b in self.btns_menu: b.draw(self.screen)

        elif self.state == STATE_MODE:
            self._draw_overlay()
            self._draw_text_centered("WYBIERZ TRYB", 40, self.assets.get_font('big'), GOLD)
            for b in self.btns_mode: b.draw(self.screen)
            self.btn_back.draw(self.screen)

            f_tiny = self.assets.get_font('tiny')
            t1 = f_tiny.render("3 ZYCIA", True, GRAY)
            t2 = f_tiny.render(f"{int(GAME_TIME)} SEKUND", True, GRAY)
            self.screen.blit(t1, (WINDOW_WIDTH // 2 - 380, 480))
            self.screen.blit(t2, (WINDOW_WIDTH // 2 + 70, 480))

        elif self.state == STATE_GAME:
            self.fruits.draw(self.screen)
            self.bombs.draw(self.screen)
            self.slices.draw(self.screen)
            self.explosions.draw(self.screen)
            self._draw_hud()

        elif self.state == STATE_OVER:
            self._draw_overlay()
            self._draw_text_centered("GAME OVER", 120, self.assets.get_font('big'), RED)
            self._draw_text_centered(f"WYNIK: {self.score}", 240, self.assets.get_font('medium'), WHITE)
            self._draw_text_centered("WPISZ IMIE I WCISNIJ ENTER", 350, self.assets.get_font('small'), GRAY)

            blink = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            self._draw_text_centered(self.player_name + blink, 420, self.assets.get_font('medium'), GREEN)

        elif self.state == STATE_RANK:
            self._draw_overlay()
            title = "RANKING: ARCADE" if "arcade" in self.ranking.current_file else "RANKING: TIME"
            self._draw_text_centered(title, 40, self.assets.get_font('big'), GOLD)
            for b in self.btns_rank: b.draw(self.screen)
            self.btn_back.draw(self.screen)

            scores = self.ranking.get_top_scores()
            f_small = self.assets.get_font('small')
            for i, (name, sc) in enumerate(scores):
                col = GOLD if i == 0 else (SILVER if i == 1 else (BRONZE if i == 2 else WHITE))
                y = 150 + i * 70
                txt_name = f_small.render(f"{i + 1}. {name}", True, col)
                txt_sc = f_small.render(str(sc), True, col)
                self.screen.blit(txt_name, (WINDOW_WIDTH // 2 - 200, y))
                self.screen.blit(txt_sc, (WINDOW_WIDTH // 2 + 150, y))

        if landmarks:
            num_hands = len(landmarks) // HAND_LANDMARKS_COUNT
            for i in range(num_hands):
                idx = i * HAND_LANDMARKS_COUNT + INDEX_FINGER_TIP
                if idx < len(landmarks):
                    pt = landmarks[idx]
                    pygame.draw.circle(self.screen, GREEN, pt, CURSOR_VISUAL_SIZE_INNER)
                    pygame.draw.circle(self.screen, WHITE, pt, CURSOR_VISUAL_SIZE_OUTER, 2)

        pygame.display.flip()

    def _draw_hud(self):
        # Left HUD (Score)
        pygame.draw.rect(self.screen, HUD_BG_COLOR, (HUD_MARGIN, HUD_MARGIN, HUD_WIDTH, HUD_HEIGHT),
                         border_radius=HUD_RADIUS)
        f_med = self.assets.get_font('medium')
        f_tiny = self.assets.get_font('tiny')
        self.screen.blit(f_tiny.render("SCORE", True, GRAY), (HUD_MARGIN + 15, HUD_MARGIN + 2))
        self.screen.blit(f_med.render(str(self.score), True, GOLD), (HUD_MARGIN + 15, HUD_MARGIN + 20))

        # Right HUD (Lives/Time)
        rx = WINDOW_WIDTH - HUD_WIDTH - HUD_MARGIN
        pygame.draw.rect(self.screen, HUD_BG_COLOR, (rx, HUD_MARGIN, HUD_WIDTH, HUD_HEIGHT), border_radius=HUD_RADIUS)

        if self.mode == "arcade":
            for i in range(MAX_LIVES):
                col = RED if i < self.lives else DARK_GREY
                self.screen.blit(f_med.render("X", True, col), (rx + 20 + i * 70, 15))
        else:
            col = RED if self.time_left < 10 else WHITE
            self.screen.blit(f_tiny.render("TIME", True, GRAY), (rx + 15, 12))
            self.screen.blit(f_med.render(str(int(self.time_left)), True, col), (rx + 15, 30))

    def _draw_overlay(self):
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.set_alpha(220)
        s.fill(DARK_BG)
        self.screen.blit(s, (0, 0))

    def _draw_text_centered(self, text, y, font, color):
        shad = font.render(text, True, BLACK)
        txt = font.render(text, True, color)
        cx = WINDOW_WIDTH // 2
        self.screen.blit(shad, (cx - txt.get_width() // 2 + 4, y + 4))
        self.screen.blit(txt, (cx - txt.get_width() // 2, y))

    def _update_trails_logic(self, landmarks):
        if not landmarks:
            self.hand_trails = {}
            return

        num_hands = len(landmarks) // HAND_LANDMARKS_COUNT
        current_hands = set()

        for i in range(num_hands):
            idx = i * HAND_LANDMARKS_COUNT + INDEX_FINGER_TIP
            if idx >= len(landmarks): continue
            pt = landmarks[idx]

            if i not in self.hand_trails: self.hand_trails[i] = []

            if self.hand_trails[i]:
                last = self.hand_trails[i][-1]
                if ((pt[0] - last[0]) ** 2 + (pt[1] - last[1]) ** 2) ** 0.5 > TRAIL_MAX_DIST:
                    self.hand_trails[i] = []

            self.hand_trails[i].append(pt)
            if len(self.hand_trails[i]) > TRAIL_LENGTH: self.hand_trails[i].pop(0)
            current_hands.add(i)

        for k in list(self.hand_trails.keys()):
            if k not in current_hands: del self.hand_trails[k]

    def _draw_trails(self):
        ts = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for pts in self.hand_trails.values():
            if len(pts) < 2: continue
            for i in range(len(pts) - 1):
                prog = i / len(pts)
                alpha = int(255 * prog)
                thick = int(10 * prog) + 2
                pygame.draw.line(ts, (255, 255, 255, alpha), pts[i], pts[i + 1], thick)
        self.screen.blit(ts, (0, 0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_MENU:
                        self.running = False
                    else:
                        self.switch_state(STATE_MENU)

                if self.state == STATE_OVER:
                    if event.key == pygame.K_RETURN:
                        n = self.player_name if self.player_name else "Anonim"
                        self.ranking.add_score(n, self.score)
                        self.switch_state(STATE_RANK)
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 12 and event.unicode.isalnum():
                        self.player_name += event.unicode.upper()

    def run(self):
        while self.running:
            self.handle_input()
            success, raw = self.cap.read()
            if not success: continue

            frame = cv2.flip(raw, 1)
            gf = np.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (1, 0, 2))
            bg = pygame.surfarray.make_surface(gf)

            lms = self.tracker.process_frame(frame)
            self.update(lms)
            self.draw(bg, lms)
            self.clock.tick(FPS)

        self.cap.release()
        pygame.quit()