import cv2
import random
import os
import numpy as np


class Fruit:
    def __init__(self, width, height, image_folder):
        self.image_path = random.choice(
            [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png") and "sliced" not in img])
        self.image = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)  # Wczytaj obraz z kanałem alfa
        if self.image is None:
            raise ValueError(f"Nie udało się załadować obrazu: {self.image_path}")

        self.image = cv2.resize(self.image, (120, 120))  # Skalowanie obrazu
        self.radius = 30  # Promień dla kolizji

        edge = random.choice([0, 1, 2, 3])

        if edge == 0:  # Wylot z góry
            self.x = random.randint(0, width)
            self.y = -60  # Poza ekranem (góra)
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(20, 25)
        elif edge == 1:  # Wylot z dołu
            self.x = random.randint(0, width)
            self.y = height  # Poza ekranem (dół)
            self.vx = random.uniform(-4, 4)
            self.vy = -random.uniform(20, 25)
        elif edge == 2:  # Wylot z lewej
            self.x = -60  # Poza ekranem (lewa strona)
            self.y = random.randint(0, height)
            self.vx = random.uniform(20, 25)
            self.vy = random.uniform(-8, 8)
        else:  # Wylot z prawej
            self.x = width + 60  # Poza ekranem (prawa strona)
            self.y = random.randint(0, height)
            self.vx = -random.uniform(20, 25)
            self.vy = random.uniform(-8, 8)

        self.gravity = 0.5  # Grawitacja

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Grawitacja

    def draw(self, frame):
        h, w, _ = self.image.shape
        x1, y1 = int(self.x - w // 2), int(self.y - h // 2)
        x2, y2 = x1 + w, y1 + h

        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
            return

        if self.image.shape[2] == 4:  # Sprawdzenie, czy obraz ma kanał alfa (RGBA)
            overlay = self.image[:, :, :3]  # Kanały RGB
            mask = self.image[:, :, 3] / 255.0  # Kanał alfa (0-1)

            for c in range(3):  # Dla każdego kanału (R, G, B)
                frame[y1:y2, x1:x2, c] = (1 - mask) * frame[y1:y2, x1:x2, c] + mask * overlay[:, :, c]
        else:
            frame[y1:y2, x1:x2] = self.image  # Jeśli obrazek nie ma kanału alfa, nakładamy go bez zmian

    def check_collision(self, hand_landmarks):
        for landmark in hand_landmarks:
            if abs(self.x - landmark[0]) < self.radius and abs(self.y - landmark[1]) < self.radius:
                return True
        return False
