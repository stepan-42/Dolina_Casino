import arcade
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


class Character:
    def __init__(self, x, y):
        self.center_x, self.center_y = x, y
        self.size, self.color = CHARACTER_SIZE, arcade.color.RED
        self.change_x = self.change_y = 0

    @property
    def left(self): return self.center_x - self.size // 2

    @property
    def right(self): return self.center_x + self.size // 2

    @property
    def bottom(self): return self.center_y - self.size // 2

    @property
    def top(self): return self.center_y + self.size // 2

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(self.left, self.bottom, self.size, self.size, self.color)

    def update(self):
        self.center_x = max(self.size // 2, min(SCREEN_WIDTH - self.size // 2, self.center_x + self.change_x))
        self.center_y = max(self.size // 2, min(SCREEN_HEIGHT - self.size // 2, self.center_y + self.change_y))
