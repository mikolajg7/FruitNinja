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
        self.state = "enter_name"  # Stan gry: 'enter_name', 'start', 'playing', 'ranking', 'end'

        # Dane dla przycisków
        self.buttons = {
            "start": {"x": 100, "y": 200, "w": 200, "h": 100},
            "ranking": {"x": 400, "y": 200, "w": 200, "h": 100},
        }
        self.previous_state = None  # Przechowywanie poprzedniego stanu (dla przycisku Back)
        self.start_timer = None  # Licznik czasu dla przycisku "Start"
        self.ranking_timer = None  # Licznik czasu dla przycisku "Ranking"
        self.back_timer = None  # Licznik czasu dla przycisku "Back"
        self.player_name = ""  # Nick gracza
        self.file_name = "ranking.csv"  # Plik z rankingiem
        self.user_exists = False  # Flaga: czy użytkownik istnieje w bazie
        self.user_empty = False  # Flaga: czy pusty login

    def render_button(self, frame, label, button, timer, fill_color, border_color):
        x, y, w, h = button["x"], button["y"], button["w"], button["h"]
        if timer is not None:
            elapsed_time = time.time() - timer
            progress = min(elapsed_time / 3.0, 1.0)
            progress_width = int(w * progress)
            cv2.rectangle(frame, (x, y), (x + progress_width, y + h), fill_color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), border_color, 2)
        cv2.putText(frame, label.capitalize(), (x + 20, y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    def read_ranking(self):
        try:
            with open(self.file_name, mode="r", newline="") as file:
                reader = csv.reader(file)
                # Wczytujemy wiersze z wynikami (sprawdzając, czy wiersz ma dokładnie 2 elementy)
                ranking = [row for row in reader if len(row) == 2]
                # Sortowanie malejąco według wyniku i ograniczenie do 10 najlepszych
                ranking = sorted(ranking, key=lambda x: int(x[1]), reverse=True)[:10]
                return ranking
        except FileNotFoundError:
            return [["Brak danych", "0"]]

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
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        alpha = 0.6  # Przezroczystość tła
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        #Ranking
        ranking_button = {"x": 50, "y": 50, "w": 200, "h": 100}
        self.render_button(frame, "Ranking", ranking_button, self.ranking_timer, (255, 255, 0), (255, 255, 0))

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
        elif self.user_empty:
            cv2.putText(frame, "Nick nie moze byc pusty", (50, self.height // 2 + 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        return frame

    def render_ranking_screen(self, frame):
        blurred_frame = cv2.GaussianBlur(frame, (25, 25), 10)
        ranking = self.read_ranking()
        center_x = self.width // 2
        # Dodajemy nagłówek "Ranking"
        header = "Ranking"
        header_size = cv2.getTextSize(header, cv2.FONT_HERSHEY_DUPLEX, 2, 3)[0]
        header_x = center_x - header_size[0] // 2
        cv2.putText(blurred_frame, header, (header_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)

        # Wyświetlamy ranking zaczynając poniżej nagłówka
        start_y = 100
        line_spacing = 40
        for i, row in enumerate(ranking):
            text = f"{i + 1}. {row[0]} - {row[1]}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1.2, 2)[0]
            text_x = center_x - text_size[0] // 2
            text_y = start_y + i * line_spacing
            cv2.putText(blurred_frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

        back_button = {"x": 50, "y": 50, "w": 200, "h": 100}
        self.render_button(blurred_frame, "Back", back_button, self.back_timer, (0, 255, 0), (0, 255, 0))
        return blurred_frame

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
                elapsed_time = time.time() - self.start_timer
                progress = min(elapsed_time / 3.0, 1.0)
                progress_width = int(w * progress)
                cv2.rectangle(frame, (x, y), (x + progress_width, y + h), (0, 200, 0), -1)

            if label == "ranking" and self.ranking_timer is not None:
                elapsed_time = time.time() - self.ranking_timer
                progress = min(elapsed_time / 3.0, 1.0)
                progress_width = int(w * progress)
                cv2.rectangle(frame, (x, y), (x + progress_width, y + h), (200, 200, 0), -1)

            # Rysowanie ramki przycisku oraz tekstu
            cv2.rectangle(frame, (x, y), (x + w, y + h), base_color, 2)
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
            self.start_timer = None

        if self.is_hand_in_button(hand_landmarks, ranking_button):
            if self.ranking_timer is None:
                self.ranking_timer = time.time()
            elif time.time() - self.ranking_timer >= 3:
                self.previous_state = self.state
                self.state = "ranking"
                self.ranking_timer = None
        else:
            self.ranking_timer = None

    def handle_ranking_screen(self, hand_landmarks):
        back_button = {"x": 50, "y": 50, "w": 200, "h": 100}
        if self.is_hand_in_button(hand_landmarks, back_button):
            if self.back_timer is None:
                self.back_timer = time.time()
            elif time.time() - self.back_timer >= 3:
                self.state = self.previous_state if self.previous_state else "enter_name"
                self.back_timer = None
        else:
            self.back_timer = None

    def render_end_screen(self, frame):
        # Dodajemy półprzezroczyste tło, aby napisy były bardziej czytelne
        # overlay = frame.copy()
        # cv2.rectangle(overlay, (0, self.height//3 - 50), (self.width, self.height//3 + 200), (0, 0, 0), -1)
        # alpha = 0.7
        # frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        text1 = f"Congratulations {self.player_name}!"
        text2 = f"Your score is: {self.game.score}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        color = (0, 255, 255)
        (text1_width, _), _ = cv2.getTextSize(text1, font, font_scale, thickness)
        (text2_width, _), _ = cv2.getTextSize(text2, font, font_scale, thickness)
        text1_x = (self.width - text1_width) // 2
        text2_x = (self.width - text2_width) // 2
        text_y = self.height // 3
        cv2.putText(frame, text1, (text1_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(frame, text2, (text2_x, text_y + 50), font, font_scale, color, thickness, cv2.LINE_AA)

        buttons = {
            "back": {"x": 50, "y": 50, "w": 200, "h": 100},
            "ranking": {"x": 300, "y": 50, "w": 200, "h": 100}
        }
        self.render_button(frame, "Back", buttons["back"], self.back_timer, (0, 255, 0), (0, 255, 0))
        self.render_button(frame, "Ranking", buttons["ranking"], self.ranking_timer, (255, 255, 0), (255, 255, 0))
        return frame

    def handle_end_screen(self, hand_landmarks):
        buttons = {
            "back": {"x": 50, "y": 50, "w": 200, "h": 100},
            "ranking": {"x": 300, "y": 50, "w": 200, "h": 100}
        }
        if self.is_hand_in_button(hand_landmarks, buttons["back"]):
            if self.back_timer is None:
                self.back_timer = time.time()
            elif time.time() - self.back_timer >= 3:
                self.state = "enter_name"
                self.back_timer = None
        else:
            self.back_timer = None

        if self.is_hand_in_button(hand_landmarks, buttons["ranking"]):
            if self.ranking_timer is None:
                self.ranking_timer = time.time()
            elif time.time() - self.ranking_timer >= 3:
                self.previous_state = self.state
                self.state = "ranking"
                self.ranking_timer = None
        else:
            self.ranking_timer = None

    def handle_enter_name(self, hand_landmarks):
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter
            if self.player_name.strip():  # Sprawdza, czy nick nie jest pusty
                self.user_exists = self.check_user_exists()
                if self.user_exists:
                    print("Nick zajęty")
                else:
                    self.game.reset()  # Reset gry
                    self.state = "start"  # Przejście do ekranu startowego
            else:
                self.user_empty = True
                print("Nick nie może być pusty")
        elif key in (8, 127):  # Backspace
            self.player_name = self.player_name[:-1]  # Usuń ostatni znak
        elif key != 255:  # Inne klawisze (uniknięcie błędów z "no key")
            self.player_name += chr(key)  # Dodaj znak do nicku

        # ranking
        # Obsługa przycisku "Ranking"
        ranking_button = {"x": 50, "y": 50, "w": 200, "h": 100}
        self.ranking_btn_enter = ranking_button  # zapamiętanie przycisku (jeśli nie ustawione wcześniej)

        if self.is_hand_in_button(hand_landmarks, ranking_button):
            if self.ranking_timer is None:
                self.ranking_timer = time.time()
            elif time.time() - self.ranking_timer >= 3:
                self.previous_state = self.state
                self.state = "ranking"
                self.ranking_timer = None
        else:
            self.ranking_timer = None

    def game_loop(self):
        # Ustawienie okna na pełny ekran
        cv2.namedWindow("Fruit Ninja", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Fruit Ninja", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

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
                self.handle_enter_name(hand_landmarks)
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

                if random.randint(1, 60) == 1:  # Losowe generowanie bomb, ~ co 60 klatek
                    self.game.spawn_bomb()

                self.game.update()
                if self.game.running == False:
                    self.game.save_score(self.player_name)
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
