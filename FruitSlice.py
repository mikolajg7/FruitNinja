import cv2
import numpy as np


class FruitSlice:
    def __init__(self, x, y, image_path, vx, vy, width, height):
        """
        image_path - ścieżka do gotowego pliku połówki owocu
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = 0.5

        # Wczytaj obrazek połówki owocu
        self.image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if self.image is None:
            raise ValueError(f"Nie udało się załadować obrazka: {image_path}")


        if self.image.shape[2] == 3:  # Jeśli obrazek nie ma kanału alfa, konwertujemy go
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2BGRA)

        # 2. Zmniejszamy obrazek do rozsądnych rozmiarów (np. 60x60 px)
        scale = int(min(width, height) * 0.08)
        self.image = cv2.resize(self.image, (scale, scale))

        h, w, _ = self.image.shape
        self.radius = w // 2  # Promień kolizji

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

    def draw(self, frame):
        h, w, _ = self.image.shape
        x1, y1 = int(self.x - w // 2), int(self.y - h // 2)
        x2, y2 = x1 + w, y1 + h


        # Sprawdzamy, czy obrazek mieści się na ekranie
        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
            return

        # Obsługa przezroczystości (kanał alfa)
        if self.image.shape[2] == 4:
            overlay = self.image[:, :, :3]  # Kanały RGB
            mask = self.image[:, :, 3] / 255.0  # Kanał alfa (0-1)

            for c in range(3):  # Dla każdego kanału (R, G, B)
                frame[y1:y2, x1:x2, c] = (1 - mask) * frame[y1:y2, x1:x2, c] + mask * overlay[:, :, c]
        else:
            frame[y1:y2, x1:x2] = self.image  # Jeśli obrazek nie ma kanału alfa, nakładamy go bez zmian
