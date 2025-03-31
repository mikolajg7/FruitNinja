import cv2
import Fruit
import FruitSlice
import csv
import time
from Bomb import Bomb, Explosion
import os

class Game:
    def __init__(self, width, height, file_name="ranking.csv"):
        self.width = width  # Szerokość okna gry
        self.height = height  # Wysokość okna gry
        self.fruits = []  # Lista aktywnych owoców
        self.slices = []  # Lista aktywnych połówek owoców
        self.bombs = []  # Lista aktywnych bomb
        self.explosions = [] # Lista aktywnych efektów eksplozji
        self.score = 0  # Wynik gracza
        self.running = True  # Flaga działania gry
        self.file_name = file_name  # Nazwa pliku z rankingiem
        self.total_time = 61  # Całkowity czas gry (60 sekund + 2 sekundy na rozpoczęcie gry)
        self.start_time = None  # Czas rozpoczęcia gry
        self.remaining_time = self.total_time

    def spawn_fruit(self):
        # # Obliczanie trudności - rośnie co sekundę o 0.033 do maksymalnie 2.5x
        # elapsed_time = time.time() - self.start_time if self.start_time else 0
        # difficulty = 1 + min(elapsed_time / 30, 1.5)  # plynny wzrost

        # Obliaczanie trudności - rośnie co 10 sekund o 0.2 do maksymalnie 2.5x
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        difficulty = 1 + min((elapsed_time // 10) * 0.2, 1.5)  # skokowy wzrost

        fruit = Fruit.Fruit(width=self.width, height=self.height, image_folder="images", difficulty=difficulty)
        print(f"[DEBUG] Fruit difficulty multiplier: {difficulty:.2f}")
        self.fruits.append(fruit)

    def spawn_bomb(self):
        # Obliczanie trudności - rośnie co sekundę o 0.033 do maksymalnie 2.5x
        # elapsed_time = time.time() - self.start_time if self.start_time else 0
        # difficulty = 1 + min(elapsed_time / 30, 1.5)  # plynny wzrost

        # Obliaczanie trudności - rośnie co 10 sekund o 0.2 do maksymalnie 2.5x
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        difficulty = 1 + min((elapsed_time // 10) * 0.2, 1.5)  # skokowy wzrost

        bomb = Bomb(width=self.width, height=self.height, image_path="bomb.png", difficulty=difficulty)
        self.bombs.append(bomb)

    # Aktualizacja stanu gry
    def update(self):
        current_time = time.time()
        self.remaining_time = max(0, int(self.total_time - (current_time - self.start_time)))
        if self.remaining_time == 0:
            self.running = False

        for fruit in self.fruits[:]:
            fruit.move()
            if fruit.y > self.height:  # Usuń owoc, jeśli spadnie poza ekran
                self.fruits.remove(fruit)

        for slice_ in self.slices[:]:
            slice_.move()
            if slice_.y > self.height:  # Usuń połówki, jeśli spadną poza ekran
                self.slices.remove(slice_)

        for bomb in self.bombs[:]:
            bomb.move()
            if bomb.y > self.height:  # Usuń bombę, jeśli spadnie poza ekran
                self.bombs.remove(bomb)

        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.life <= 0:
                self.explosions.remove(explosion)

    # Sprawdzanie kolizji z dłonią
    def check_collision(self, hand_landmarks):
        for fruit in self.fruits[:]:
            if fruit.check_collision(hand_landmarks):
                self.fruits.remove(fruit)
                self.score += 1

                # Tworzymy połówki owocu na podstawie plików graficznych
                slice_path = fruit.image_path.replace(".png", "-sliced.png")

                self.slices.append(
                    FruitSlice.FruitSlice(fruit.x - 20, fruit.y, slice_path, -3, -5, self.width, self.height))
                self.slices.append(
                    FruitSlice.FruitSlice(fruit.x + 20, fruit.y, slice_path, 3, -5, self.width, self.height))

        for bomb in self.bombs[:]:
            if bomb.check_collision(hand_landmarks):
                self.bombs.remove(bomb)
                self.score -= 5
                self.explosions.append(Explosion(bomb.x, bomb.y))

    # Zapis wyniku do pliku CSV
    def save_score(self, player_name):
        try:
            with open(self.file_name, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([player_name, self.score])  # Zapisujemy nick i wynik gracza
        except Exception as e:
            print(f"Nie udało się zapisać wyniku: {e}")

    def render(self, frame):
        for fruit in self.fruits:
            fruit.draw(frame)
        for slice_ in self.slices:
            slice_.draw(frame)

        for bomb in self.bombs:
            bomb.draw(frame)
        for explosion in self.explosions:
            explosion.draw(frame)

        # Ustawienia dla tła tekstu
        overlay = frame.copy()
        alpha = 0.5  # Przezroczystość (0 = całkowicie przezroczyste, 1 = pełne krycie)

        # Wymiary prostokątów dla tekstu
        score_box = (10, 10, 200, 60)  # (x, y, szerokość, wysokość)
        time_box = (self.width - 210, 10, 200, 60)

        # Rysowanie półprzezroczystych prostokątów
        cv2.rectangle(overlay, (score_box[0], score_box[1]), 
                    (score_box[0] + score_box[2], score_box[1] + score_box[3]), 
                    (0, 0, 0), -1)
        cv2.rectangle(overlay, (time_box[0], time_box[1]), 
                    (time_box[0] + time_box[2], time_box[1] + time_box[3]), 
                    (0, 0, 0), -1)

        # Nakładanie półprzezroczystego tła na oryginalną klatkę
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Dodanie tekstu na tło
        cv2.putText(frame, f"Score: {self.score}", (20, 45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {self.remaining_time}", (self.width - 200, 45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


    def reset(self):
        self.fruits = []
        self.slices = []
        self.bombs = []
        self.explosions = []
        self.score = 0
        self.running = True
        self.total_time = 61
        self.start_time = None
        self.remaining_time = self.total_time
