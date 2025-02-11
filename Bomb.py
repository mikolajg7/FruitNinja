import cv2
import math
import random


class Bomb:
    def __init__(self, width, height):
        edge = random.choice([0, 1, 2, 3])

        if edge == 0:  # Wylot z góry
            self.x = random.randint(0, width)
            self.y = -60  # Poza ekranem (góra)
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(20, 25)
        elif edge == 1:  # Wylot z dołu
            self.x = random.randint(0, width)
            self.y = height   # Poza ekranem (dół)
            self.vx = random.uniform(-4, 4)
            self.vy = -random.uniform(20, 25)
        elif edge == 2:  # Wylot z lewej
            self.x = -60  # Poza ekranem (lewa strona)
            self.y = random.randint(0, height)
            self.vx = random.uniform(20, 25)
            self.vy = random.uniform(-8, 8)
        else:  # Wylot z prawej
            self.x = width + 60 # Poza ekranem (prawa strona)
            self.y = random.randint(0, height)
            self.vx = -random.uniform(20, 25)
            self.vy = random.uniform(-8, 8)

        self.gravity = 0.5  # Grawitacja
        self.radius = 60  # Promień bomby
        self.color = (0,0,0) # Kolor czarny

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Grawitacja

    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.radius, self.color, -1)
        # Przygotowanie parametrów tekstu
        text = "B"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        # Obliczenie rozmiaru tekstu, aby wycentrować literę w bombie
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_width, text_height = text_size

        # Ustawienie pozycji tekstu - wycentrowanie względem środka bomby
        text_x = int(self.x - text_width / 2)
        text_y = int(self.y + text_height / 2)

        # Rysowanie litery B
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

    def check_collision(self, hand_landmarks):
        """Sprawdza, czy bomba została "przecięta" przez dłoń."""
        for landmark in hand_landmarks:
            hand_x, hand_y = landmark[0], landmark[1]
            distance = math.sqrt((self.x - hand_x) ** 2 + (self.y - hand_y) ** 2)
            if distance < self.radius:
                return True
        return False


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 10

    def update(self):
        """Zmniejsza czas życia efektu."""
        self.life -= 1

    def draw(self, frame):
        """Rysuje efekt eksplozji na ekranie."""
        if self.life > 0:
            cv2.putText(frame, "BOOM!", (int(self.x), int(self.y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)