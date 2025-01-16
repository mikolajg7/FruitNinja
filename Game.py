import cv2
import Fruit
import FruitSlice



class Game:
    def __init__(self, width, height):
        self.width = width  # Szerokość okna gry
        self.height = height  # Wysokość okna gry
        self.fruits = []  # Lista aktywnych owoców
        self.slices = []  # Lista aktywnych połówek owoców
        self.score = 0  # Wynik gracza
        self.running = True  # Flaga działania gry

    def spawn_fruit(self):
        fruit = Fruit.Fruit(width=self.width, height=self.height)
        self.fruits.append(fruit)

    # Update stanuy gry
    def update(self):
        for fruit in self.fruits[:]:
            fruit.move()
            if fruit.y > self.height:  # Usuń owoc, jeśli spadnie poza ekran
                self.fruits.remove(fruit)

        for slice_ in self.slices[:]:
            slice_.move()
            if slice_.y > self.height:  # Usuń połówki, jeśli spadną poza ekran
                self.slices.remove(slice_)

    # Sprawdzanie kolizji z dłonią
    def check_collision(self, hand_landmarks):
        for fruit in self.fruits[:]:
            if fruit.check_collision(hand_landmarks):
                self.fruits.remove(fruit)
                self.score += 1
                # Tworzymy dwie połówki owocu
                self.slices.append(FruitSlice.FruitSlice(fruit.x, fruit.y, fruit.radius, fruit.color, -3, -5))
                self.slices.append(FruitSlice.FruitSlice(fruit.x, fruit.y, fruit.radius, fruit.color, 3, -5))

    # Renderowanie gry
    def render(self, frame):
        for fruit in self.fruits:
            fruit.draw(frame)
        for slice_ in self.slices:
            slice_.draw(frame)
        cv2.putText(frame, f"Score: {self.score}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)