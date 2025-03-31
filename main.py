import cv2
import random
import time
import csv
from Game import Game
from HandTracker import HandTracker

class Main:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.game = Game(self.width, self.height)
        self.hand_tracker = HandTracker()
        self.running = True
        self.state = "enter_name"

        self.font_scale = self.width / 1000

        # Definicje przycisków w formacie zależnym od rozmiaru ekranu
        self.button_definitions = {
            "start": {"x_factor": 0.05, "y_factor": 0.3, "w_factor": 0.15, "h_factor": 0.12},
            "ranking": {"x_factor": 0.25, "y_factor": 0.3, "w_factor": 0.15, "h_factor": 0.12},
            "back": {"x_factor": 0.05, "y_factor": 0.05, "w_factor": 0.15, "h_factor": 0.12}
        }

        self.previous_state = None
        self.start_timer = None
        self.ranking_timer = None
        self.back_timer = None
        self.player_name = ""
        self.file_name = "ranking.csv"
        self.user_exists = False
        self.user_empty = False

    def get_button_rect(self, name):
        if name not in self.button_definitions:
            raise ValueError(f"Brak definicji przycisku '{name}'")
        b = self.button_definitions[name]
        return {
            "x": int(b["x_factor"] * self.width),
            "y": int(b["y_factor"] * self.height),
            "w": int(b["w_factor"] * self.width),
            "h": int(b["h_factor"] * self.height)
        }

    def render_button(self, frame, label, button, timer, fill_color, border_color):
        x, y, w, h = button["x"], button["y"], button["w"], button["h"]
        if timer is not None:
            elapsed_time = time.time() - timer
            progress = min(elapsed_time / 3.0, 1.0)
            progress_width = int(w * progress)
            cv2.rectangle(frame, (x, y), (x + progress_width, y + h), fill_color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), border_color, 2)
        cv2.putText(frame, label.capitalize(), (x + int(w * 0.1), y + int(h * 0.6)),
                    cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, (0, 0, 0), 2)

    def read_ranking(self):
        try:
            with open(self.file_name, mode="r", newline="") as file:
                reader = csv.reader(file)
                ranking = [row for row in reader if len(row) == 2]
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
            pass
        return False

    def render_start_screen(self, frame):
        for label in ["start", "ranking"]:
            button = self.get_button_rect(label)
            timer = self.start_timer if label == "start" else self.ranking_timer
            fill_color = (0, 200, 0) if label == "start" else (200, 200, 0)
            border_color = (0, 255, 0) if label == "start" else (255, 255, 0)
            self.render_button(frame, label, button, timer, fill_color, border_color)

    def render_enter_name_screen(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

        button = self.get_button_rect("ranking")
        self.render_button(frame, "Ranking", button, self.ranking_timer, (255, 255, 0), (255, 255, 0))

        cv2.putText(frame, "Podaj nick: " + self.player_name, (int(self.width * 0.05), int(self.height * 0.5)),
                    cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, (255, 255, 255), 2)
        cv2.putText(frame, "ENTER aby zatwierdzic", (int(self.width * 0.05), int(self.height * 0.5 + 50)),
                    cv2.FONT_HERSHEY_SIMPLEX, self.font_scale * 0.8, (200, 200, 200), 1)

        if self.user_exists:
            cv2.putText(frame, "Nick zajety", (int(self.width * 0.05), int(self.height * 0.5 + 100)),
                        cv2.FONT_HERSHEY_SIMPLEX, self.font_scale * 0.8, (0, 0, 255), 2)
        elif self.user_empty:
            cv2.putText(frame, "Nick nie moze byc pusty", (int(self.width * 0.05), int(self.height * 0.5 + 100)),
                        cv2.FONT_HERSHEY_SIMPLEX, self.font_scale * 0.8, (0, 0, 255), 2)
        return frame

    def render_ranking_screen(self, frame):
        blurred = cv2.GaussianBlur(frame, (25, 25), 10)
        ranking = self.read_ranking()
        center_x = self.width // 2
        header = "Ranking"
        size = cv2.getTextSize(header, cv2.FONT_HERSHEY_DUPLEX, self.font_scale * 2, 3)[0]
        cv2.putText(blurred, header, (center_x - size[0] // 2, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, self.font_scale * 2, (255, 255, 255), 3)

        start_y = int(self.height * 0.15)
        spacing = int(self.height * 0.06)
        for i, row in enumerate(ranking):
            text = f"{i + 1}. {row[0]} - {row[1]}"
            size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            cv2.putText(blurred, text, (center_x - size[0] // 2, start_y + i * spacing),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        back_btn = self.get_button_rect("back")
        self.render_button(blurred, "Back", back_btn, self.back_timer, (0, 255, 0), (0, 255, 0))
        return blurred

    def render_end_screen(self, frame):
        text1 = f"Congratulations {self.player_name}!"
        text2 = f"Your score is: {self.game.score}"
        scale = self.font_scale * 1.5
        t1_size = cv2.getTextSize(text1, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)[0]
        t2_size = cv2.getTextSize(text2, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)[0]
        y = self.height // 3
        cv2.putText(frame, text1, ((self.width - t1_size[0]) // 2, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 255, 255), 2)
        cv2.putText(frame, text2, ((self.width - t2_size[0]) // 2, y + 60), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 255, 255), 2)

        for name in ["back", "ranking"]:
            btn = self.get_button_rect(name)
            color = (0, 255, 0) if name == "back" else (255, 255, 0)
            timer = self.back_timer if name == "back" else self.ranking_timer
            self.render_button(frame, name, btn, timer, color, color)
        return frame

    def is_hand_in_button(self, hand_landmarks, button):
        if not hand_landmarks:
            return False
        x, y, w, h = button["x"], button["y"], button["w"], button["h"]
        return any(x <= lm[0] <= x + w and y <= lm[1] <= y + h for lm in hand_landmarks)

    def handle_start_screen(self, hand_landmarks):
        start_btn = self.get_button_rect("start")
        rank_btn = self.get_button_rect("ranking")
        if self.is_hand_in_button(hand_landmarks, start_btn):
            self.start_timer = self.start_timer or time.time()
            if time.time() - self.start_timer >= 3:
                self.state = "playing"
                self.game.start_time = time.time()
                self.start_timer = None
        else:
            self.start_timer = None

        if self.is_hand_in_button(hand_landmarks, rank_btn):
            self.ranking_timer = self.ranking_timer or time.time()
            if time.time() - self.ranking_timer >= 3:
                self.previous_state = self.state
                self.state = "ranking"
                self.ranking_timer = None
        else:
            self.ranking_timer = None

    def handle_ranking_screen(self, hand_landmarks):
        btn = self.get_button_rect("back")
        if self.is_hand_in_button(hand_landmarks, btn):
            self.back_timer = self.back_timer or time.time()
            if time.time() - self.back_timer >= 3:
                self.state = self.previous_state or "enter_name"
                self.back_timer = None
        else:
            self.back_timer = None

    def handle_end_screen(self, hand_landmarks):
        for name in ["back", "ranking"]:
            btn = self.get_button_rect(name)
            timer_attr = "back_timer" if name == "back" else "ranking_timer"
            if self.is_hand_in_button(hand_landmarks, btn):
                if getattr(self, timer_attr) is None:
                    setattr(self, timer_attr, time.time())
                elif time.time() - getattr(self, timer_attr) >= 3:
                    if name == "back":
                        self.state = "enter_name"
                    else:
                        self.previous_state = self.state
                        self.state = "ranking"
                    setattr(self, timer_attr, None)
            else:
                setattr(self, timer_attr, None)

    def handle_enter_name(self, hand_landmarks):
        key = cv2.waitKey(1) & 0xFF
        if key == 13:
            if self.player_name.strip():
                self.user_exists = self.check_user_exists()
                if not self.user_exists:
                    self.game.reset()
                    self.state = "start"
                else:
                    print("Nick zajęty")
            else:
                self.user_empty = True
        elif key in (8, 127):
            self.player_name = self.player_name[:-1]
        elif key != 255:
            self.player_name += chr(key)

        btn = self.get_button_rect("ranking")
        if self.is_hand_in_button(hand_landmarks, btn):
            self.ranking_timer = self.ranking_timer or time.time()
            if time.time() - self.ranking_timer >= 3:
                self.previous_state = self.state
                self.state = "ranking"
                self.ranking_timer = None
        else:
            self.ranking_timer = None

    def game_loop(self):
        cv2.namedWindow("Fruit Ninja", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Fruit Ninja", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            hand_landmarks = self.hand_tracker.process_frame(frame)

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
                if random.randint(1, 6) == 1:
                    self.game.spawn_fruit()
                if random.randint(1, 60) == 1:
                    self.game.spawn_bomb()
                self.game.update()
                if not self.game.running:
                    self.game.save_score(self.player_name)
                    self.state = "end"
                self.game.check_collision(hand_landmarks)
                self.game.render(frame)

            cv2.imshow("Fruit Ninja", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                self.running = False

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = Main()
    try:
        app.game_loop()
    finally:
        if app.state == "playing" and app.player_name.strip():
            app.game.save_score(app.player_name)