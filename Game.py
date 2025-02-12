import cv2
import Fruit
import FruitSlice
import csv
import time
from Bomb import Bomb, Explosion


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
        fruit = Fruit.Fruit(width=self.width, height=self.height)
        self.fruits.append(fruit)

    def spawn_bomb(self):
        bomb = Bomb(width=self.width, height=self.height)
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
                # Tworzymy dwie połówki owocu
                self.slices.append(FruitSlice.FruitSlice(fruit.x, fruit.y, fruit.radius, fruit.color, -3, -5))
                self.slices.append(FruitSlice.FruitSlice(fruit.x, fruit.y, fruit.radius, fruit.color, 3, -5))

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

    # Renderowanie gry
    def render(self, frame):
        for fruit in self.fruits:
            fruit.draw(frame)
        for slice_ in self.slices:
            slice_.draw(frame)
        for bomb in self.bombs:
            bomb.draw(frame)
        for explosion in self.explosions:
            explosion.draw(frame)
        cv2.putText(frame, f"Score: {self.score}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {self.remaining_time}", (self.width-200,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

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
