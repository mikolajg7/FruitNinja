import random
from .config import *
from .entities import Fruit, Bomb


class Spawner:
    def __init__(self, fruit_group, bomb_group):
        self.fruits = fruit_group
        self.bombs = bomb_group
        self.timer = 0
        self.elapsed_frames = 0
        self.current_difficulty = 0.0

    def reset(self):
        self.elapsed_frames = 0
        self.current_difficulty = 0.0
        self.timer = 0

    def update(self):
        # 1. Aktualizacja trudności (0.0 -> 1.0 w czasie)
        self.elapsed_frames += 1
        ramp_frames = DIFFICULTY_RAMP_SECONDS * FPS
        self.current_difficulty = min(self.elapsed_frames / ramp_frames, 1.0)

        # 2. Obliczanie czasu do następnego spawnu
        # Interpolacja: Start (wolno) -> End (szybko)
        current_spawn_rate = SPAWN_RATE_START + (SPAWN_RATE_END - SPAWN_RATE_START) * self.current_difficulty

        self.timer += 1
        if self.timer > current_spawn_rate:
            self.timer = 0
            self.spawn_wave()

    def spawn_wave(self):
        # 1. Obliczanie wielkości fali (Burst)
        current_burst_chance = BURST_CHANCE_START + (BURST_CHANCE_END - BURST_CHANCE_START) * self.current_difficulty

        count = 1
        if random.random() < current_burst_chance:
            # Na trudnym poziomie (difficulty > 0.6) rzucamy 2-4 obiekty
            if self.current_difficulty > 0.6:
                count = random.choice([2, 3, 4])
            else:
                count = random.choice([2, 3])

        # 2. Mnożnik prędkości (żeby owoce latały szybciej pod koniec)
        speed_mult = 1.0 + (MAX_SPEED_MULTIPLIER - 1.0) * self.current_difficulty

        # 3. Szansa na bombę dla tej fali
        current_bomb_chance = BOMB_CHANCE_START + (BOMB_CHANCE_END - BOMB_CHANCE_START) * self.current_difficulty

        for _ in range(count):
            if random.random() < current_bomb_chance:
                # Ogranicznik: 50% szans, że faktycznie zrespimy bombę,
                if random.random() < 0.5:
                    self._spawn_object("bomb", speed_mult)
                else:
                    self._spawn_object("fruit", speed_mult)
            else:
                self._spawn_object("fruit", speed_mult)

    def _spawn_object(self, obj_type, speed_mult):
        # Chaos Mode: Decyzja skąd wyleci obiekt
        # Wagi zmieniają się wraz z trudnością (na początku głównie dół)

        w_bottom = 0.8 - (0.3 * self.current_difficulty)
        w_top = 0.05 + (0.15 * self.current_difficulty)
        w_side = 0.075 + (0.075 * self.current_difficulty)

        weights = [w_bottom, w_top, w_side, w_side]
        side = random.choices(["bottom", "top", "left", "right"], weights=weights)[0]

        x, y, vx, vy = 0, 0, 0, 0

        if side == "bottom":
            # Wylot z dołu
            x = random.randint(SPAWN_OFFSET_X, WINDOW_WIDTH - SPAWN_OFFSET_X)
            y = WINDOW_HEIGHT + SPAWN_OFFSET_Y_BOTTOM
            vx = random.randint(*THROW_VEL_X_BOTTOM)
            vy = random.randint(*THROW_VEL_Y_BOTTOM)

        elif side == "top":
            # Spadek z góry
            x = random.randint(SPAWN_OFFSET_X, WINDOW_WIDTH - SPAWN_OFFSET_X)
            y = SPAWN_OFFSET_Y_TOP
            vx = random.randint(*THROW_VEL_X_TOP)
            vy = random.randint(*THROW_VEL_Y_TOP)

        elif side == "left":
            # Wylot z lewej
            x = -SPAWN_OFFSET_X
            y = random.randint(200, WINDOW_HEIGHT - 200)
            vx = random.randint(*THROW_VEL_X_SIDE)
            vy = random.randint(*THROW_VEL_Y_SIDE)

        elif side == "right":
            # Wylot z prawej (odwracamy X i prędkość X)
            x = WINDOW_WIDTH + SPAWN_OFFSET_X
            y = random.randint(200, WINDOW_HEIGHT - 200)
            vx = random.randint(*THROW_VEL_X_SIDE) * -1
            vy = random.randint(*THROW_VEL_Y_SIDE)

        if obj_type == "fruit":
            ftype = random.choice(FRUIT_TYPES)
            self.fruits.add(Fruit(x, y, vx, vy, ftype, speed_mult))
        else:
            self.bombs.add(Bomb(x, y, vx, vy, speed_mult))