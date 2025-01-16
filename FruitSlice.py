import cv2
class FruitSlice:
    def __init__(self, x, y, radius, color, vx, vy):
        self.x = x
        self.y = y
        self.radius = radius // 2  # Połówka owocu
        self.color = color
        self.vx = vx
        self.vy = vy
        self.gravity = 0.5

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

    def draw(self, frame):
        cv2.ellipse(frame, (int(self.x), int(self.y)), (self.radius, self.radius // 2),
                    0, 0, 360, self.color, -1)