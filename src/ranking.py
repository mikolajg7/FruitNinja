import csv
import os
from .config import *


class RankingManager:
    def __init__(self):
        self.current_file = RANKING_FILE_ARCADE

        if not os.path.exists(RANKING_DIR):
            os.makedirs(RANKING_DIR)

        self.scores = []
        self.load_scores()

    def set_mode(self, mode_name):
        if mode_name == "arcade":
            self.current_file = RANKING_FILE_ARCADE
        else:
            self.current_file = RANKING_FILE_TIME
        self.load_scores()

    def load_scores(self):
        self.scores = []
        if os.path.exists(self.current_file):
            with open(self.current_file, "r") as f:
                reader = csv.reader(f)
                try:
                    self.scores = [(row[0], int(row[1])) for row in reader if row]
                    self.scores.sort(key=lambda x: x[1], reverse=True)
                except ValueError:
                    pass

    def add_score(self, name, score):
        self.scores.append((name, score))
        self.scores.sort(key=lambda x: x[1], reverse=True)
        self.scores = self.scores[:10]
        self.save_scores()

    def save_scores(self):
        with open(self.current_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.scores)

    def get_top_scores(self, limit=5):
        return self.scores[:limit]