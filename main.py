import cv2
import random
import time
import csv
from Game import Game
from HandTracker import HandTracker


class Main:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Kamera
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Szerokość kamery
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Wysokość kamery

        self.game = Game(self.width, self.height)  # Obiekt gry
        self.hand_tracker = HandTracker()  # Śledzenie dłoni
        self.running = True  # Flaga działania gry
        self.state = "enter_name"  # Stan gry: 'enter_name', 'start', 'playing', 'ranking'

        # Dane dla przycisków
        self.buttons = {
            "start": {"x": 100, "y": 200, "w": 200, "h": 100},
            "ranking": {"x": 400, "y": 200, "w": 200, "h": 100},
        }
        self.start_timer = None  # Licznik czasu dla przycisku "Start"
        self.ranking_timer = None  # Licznik czasu dla przycisku "Ranking"
        self.player_name = ""  # Nick gracza
        self.file_name = "ranking.csv"  # Plik z rankingiem
        self.user_exists = False  # Flaga: czy użytkownik istnieje w bazie

    def read_ranking(self):
        try:
            with open(self.file_name, mode="r", newline="") as file:
                reader = csv.reader(file)
                ranking = sorted([row for row in reader if len(row) == 2], key=lambda x: int(x[1]), reverse=True) # Sortowanie po wynikach omijając puste wiersze
                return ranking
        except FileNotFoundError:
            return [["Brak danych"]]
    def check_user_exists(self):
        try:
            with open(self.file_name, mode="r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0].strip().lower() == self.player_name.strip().lower():
                        return True
        except FileNotFoundError:
            # Plik nie istnieje, więc użytkownik nie może być w bazie
            pass
        return False

    def render_enter_name_screen(self, frame):
        # Tworzenie półprzezroczystego czarnego tła
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)  # Czarne tło
        alpha = 0.6  # Przezroczystość tła
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # Renderowanie tekstu na ekranie
        text = "Podaj nick: " + self.player_name
        cv2.putText(frame, text, (50, self.height // 2 - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.putText(frame, "ENTER aby zatwierdzic", (50, self.height // 2 + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)

        # Jeśli użytkownik istnieje, wyświetl komunikat
        if self.user_exists:
            cv2.putText(frame, "Nick zajety", (50, self.height // 2 + 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        return frame

    def render_ranking_screen(self, frame):
        # Rozmycie tła
        blurred_frame = cv2.GaussianBlur(frame, (25, 25), 10)  # Rozmycie tła

        # Wyświetlenie rankingu
        ranking= self.read_ranking()
        start_y= 100
        center_x = self.width // 2
        for i, row in enumerate(ranking):
            text = f"{i + 1}. {row[0]} - {row[1]}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1, 5)[0]
            text_x = center_x - 400 # Wyśrodkowanie tekstu

            cv2.putText(blurred_frame, text, (text_x, start_y + i * 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 10)

        #Przycisk Back
        back_btn = {"x": 50, "y": 50, "w": 200, "h": 100}
        cv2.rectangle(blurred_frame, (back_btn["x"], back_btn["y"]), (back_btn["x"] + back_btn["w"], back_btn["y"] + back_btn["h"]), (0, 255, 0), -1)
        cv2.putText(blurred_frame, "Back", (back_btn["x"] + 10, back_btn["y"] + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return blurred_frame

    def handle_enter_name(self):
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter
            if self.player_name.strip():  # Sprawdza, czy nick nie jest pusty
                self.user_exists = self.check_user_exists()
                if self.user_exists:
                    print("Nick zajęty")
                else:
                    self.game.reset() # Reset gry
                    self.state = "start"  # Przejście do ekranu startowego
            else:
                print("Nick nie może być pusty")
        elif key in (8,127):  # Backspace
            self.player_name = self.player_name[:-1]  # Usuń ostatni znak
        elif key != 255:  # Inne klawisze (uniknięcie błędów z "no key")
            self.player_name += chr(key)  # Dodaj znak do nicku

    def is_hand_in_button(self, hand_landmarks, button):
        if not hand_landmarks:
            return False
        x, y, w, h = button["x"], button["y"], button["w"], button["h"]
        for lm in hand_landmarks:
            if x <= lm[0] <= x + w and y <= lm[1] <= y + h:
                return True
        return False

    def render_start_screen(self, frame):
        for label, button in self.buttons.items():
            x, y, w, h = button["x"], button["y"], button["w"], button["h"]

            # Podstawowy kolor przycisku
            base_color = (255, 255, 0) if label == "ranking" else (0, 255, 0)

            # Wypełnienie postępu
            if label == "start" and self.start_timer is not None:
                # Obliczenie proporcji wypełnienia
                elapsed_time = time.time() - self.start_timer
                progress = min(elapsed_time / 3.0, 1.0)  # Ograniczenie progresu do 1.0 (100%)
                progress_width = int(w * progress)

                # Rysowanie wypełnienia przycisku
                cv2.rectangle(frame, (x, y), (x + progress_width, y + h), (0, 200, 0), -1)

            if label == "ranking" and self.ranking_timer is not None:
                # Obliczenie proporcji wypełnienia
                elapsed_time = time.time() - self.ranking_timer
                progress = min(elapsed_time / 3.0, 1.0)
                progress_width = int(w * progress)

                # Rysowanie wypełnienia przycisku
                cv2.rectangle(frame, (x, y), (x + progress_width, y + h), (200, 200, 0), -1)  # Kolor dla ranking



            # Tekst na przycisku
            cv2.putText(frame, label.capitalize(), (x + 20, y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)


            # Rysowanie ramki przycisku
            cv2.rectangle(frame, (x, y), (x + w, y + h), base_color, 2)

            # Tekst na przycisku
            cv2.putText(frame, label.capitalize(), (x + 20, y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    def handle_start_screen(self, hand_landmarks):
        start_button = self.buttons["start"]
        ranking_button = self.buttons["ranking"]

        if self.is_hand_in_button(hand_landmarks, start_button):
            if self.start_timer is None:
                self.start_timer = time.time()  # Start liczenia czasu
            elif time.time() - self.start_timer >= 3:  # Po 3 sekundach
                self.state = "playing"  # Przejście do gry
                self.game.start_time = time.time()  # Start czasu gry
                self.start_timer = None  # Reset licznika
        else:
            self.start_timer = None  # Reset czasu, jeśli dłoń opuści przycisk

        if self.is_hand_in_button(hand_landmarks, ranking_button):
            if self.ranking_timer is None:
                self.ranking_timer = time.time()
            elif time.time() - self.ranking_timer >= 3:
                self.state = "ranking"
                self.ranking_timer = None
        else:
            self.ranking_timer = None

    def handle_ranking_screen(self, hand_landmarks):
        back_btn = {"x": 50, "y": 50, "w": 200, "h": 100}
        if self.is_hand_in_button(hand_landmarks, back_btn):
            self.state = "start"

    def render_end_screen(self, frame):
        blurred_frame = cv2.GaussianBlur(frame, (25, 25), 10)  # Rozmycie tła

        text1 = f"Congratulations {self.player_name}!"
        text2 = f"Your score is: {self.game.score}"

        font = cv2.FONT_HERSHEY_TRIPLEX
        font_scale = 5
        thickness = 10
        color = (0, 0, 255)

        (text1_width, text1_height), baseline = cv2.getTextSize(text1, font, font_scale, thickness)
        (text2_width, text2_height), baseline2 = cv2.getTextSize(text2, font, font_scale, thickness)

        if text1_width > self.width: # Skalowanie tekstu, jeśli jest za długi
            scale_factor = self.width / text1_width
            font_scale *= scale_factor
            (text1_width, text1_height), baseline = cv2.getTextSize(text1, font, font_scale, thickness)

        text1_x = (self.width - text1_width) // 2
        text_y = (self.height - text1_height - text2_height - 20) // 2

        text2_x = (self.width - text2_width) // 2
        text2_y = text_y + text1_height + 25  # Dodanie odstępu między liniami

        line1_position = (text1_x, text_y)
        line2_position = (text2_x, text2_y)

        # Rysowanie obu linii
        cv2.putText(blurred_frame, text1, line1_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(blurred_frame, text2, line2_position, font, font_scale, color, thickness, cv2.LINE_AA)

        # Przycisk Back
        back_btn = {"x": 50, "y": 50, "w": 200, "h": 100}
        cv2.rectangle(blurred_frame, (back_btn["x"], back_btn["y"]),
                      (back_btn["x"] + back_btn["w"], back_btn["y"] + back_btn["h"]), (0, 255, 0), -1)
        cv2.putText(blurred_frame, "Back", (back_btn["x"] + 10, back_btn["y"] + 35), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2)

        return blurred_frame

    def handle_end_screen(self, hand_landmarks):
        back_btn = {"x": 50, "y": 50, "w": 200, "h": 100}
        if self.is_hand_in_button(hand_landmarks, back_btn):
            self.state = "enter_name"

    def game_loop(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            # Lustrzane odbicie
            frame = cv2.flip(frame, 1)

            # Śledzenie dłoni
            hand_landmarks = self.hand_tracker.process_frame(frame)

            # Obsługa stanów gry
            if self.state == "enter_name":
                frame = self.render_enter_name_screen(frame)
                self.handle_enter_name()
            elif self.state == "start":
                self.render_start_screen(frame)
                self.handle_start_screen(hand_landmarks)
            elif self.state == "ranking":
                frame = self.render_ranking_screen(frame)
                self.handle_ranking_screen(hand_landmarks)
            elif self.state == "end":
                frame = self.render_end_screen(frame)
                self.handle_end_screen(hand_landmarks)
            elif self.state == "playing":
                # Logika gry
                if random.randint(1, 6) == 1:  # Losowe generowanie owoców, ~ co 6 klatek
                    self.game.spawn_fruit()

                if random.randint(1, 60) == 1: # Losowe generowanie bomb, ~ co 60 klatek
                    self.game.spawn_bomb()

                self.game.update()
                if self.game.running==False:
                    app.game.save_score(app.player_name)
                    self.state = "end"
                self.game.check_collision(hand_landmarks)
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
    try:
        app.game_loop()
    finally:
        # Zapisz wynik gracza przed zakończeniem gry
        if app.state == "playing" and app.player_name.strip():
            app.game.save_score(app.player_name)

