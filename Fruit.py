import cv2
import random


class Fruit:
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
        self.radius = 60  # Promień owocu
        self.color = (
            random.randint(0, 255),  # R
            random.randint(0, 255),  # G
            random.randint(0, 255)  #  B
        )

# Metoda poruszania owocem
    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Grawitacja

# Rysowanie owocu na ekranie
    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.radius, self.color, -1)

# Sprawdzanie kolizji owocu z dłonią
    def check_collision(self, hand_landmarks):
        for landmark in hand_landmarks:
            # jesli odległość między owocem a punktem dłoni na osi X i osi Y jest mniejsza niż promień owocu
            if abs(self.x - landmark[0]) < self.radius and abs(self.y - landmark[1]) < self.radius:
                return True
        return False