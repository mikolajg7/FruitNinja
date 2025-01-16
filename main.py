import cv2
import random
from Game import Game
from HandTracker import HandTracker


class Main:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Kamera
        # Pobranie szerokości i wysokości z kamery
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.game = Game(self.width, self.height)  # Obiekt gry
        self.hand_tracker = HandTracker()  # Śledzenie dłoni
        self.running = True  # Flaga działania gry

    # Główna pętla gry
    def game_loop(self):
        while self.running and self.cap.isOpened():
            # Pobranie klatki obrazu
            ret, frame = self.cap.read()
            if not ret:
                break

            # Lustrzane odbicie
            frame = cv2.flip(frame, 1)

            # Śledzenie dłoni
            hand_landmarks = self.hand_tracker.process_frame(frame)

            # Generowanie owoców
            if random.randint(1, 6) == 1:  # Losowe generowanie owoców, ~ co 6 klatek
                self.game.spawn_fruit()

            #  Aktualizacja gry
            self.game.update()
            self.game.check_collision(hand_landmarks)

            #  Renderowanie obrazu
            self.game.render(frame)

            # Wyświetlenie obrazu
            cv2.imshow("Fruit Ninja", frame)

            # Obsługa wyjścia
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                self.running = False

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = Main()
    app.game_loop()