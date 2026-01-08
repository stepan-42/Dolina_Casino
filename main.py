import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Три экрана"
CHARACTER_SIZE = 40
RECT_WIDTH = 200
RECT_HEIGHT = 100
MOVEMENT_SPEED = 5


class Character:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.size = CHARACTER_SIZE
        self.color = arcade.color.RED
        self.change_x = 0
        self.change_y = 0

    def draw(self):
        left = self.center_x - self.size // 2
        bottom = self.center_y - self.size // 2
        arcade.draw_lbwh_rectangle_filled(left, bottom, self.size, self.size, self.color)

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        self.center_x = max(self.size // 2, min(SCREEN_WIDTH - self.size // 2, self.center_x))
        self.center_y = max(self.size // 2, min(SCREEN_HEIGHT - self.size // 2, self.center_y))


class BaseScreen(arcade.View):
    def __init__(self, screen_number):
        super().__init__()
        self.screen_number = screen_number
        self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.rect = None
        self.title_text = None
        self.setup_rect()
        self.setup_text()

    def setup_rect(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT - RECT_HEIGHT // 2 - 50

        left = center_x - RECT_WIDTH // 2
        bottom = center_y - RECT_HEIGHT // 2

        if self.screen_number == 1:
            color = arcade.color.BLUE
        elif self.screen_number == 2:
            color = arcade.color.GREEN
        else:
            color = arcade.color.YELLOW

        self.rect = {
            'left': left,
            'bottom': bottom,
            'width': RECT_WIDTH,
            'height': RECT_HEIGHT,
            'color': color
        }

    def setup_text(self):
        self.title_text = arcade.Text(
            f"Экран {self.screen_number}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            30,
            anchor_x="center"
        )

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.title_text.draw()

        arcade.draw_lbwh_rectangle_outline(
            self.rect['left'],
            self.rect['bottom'],
            self.rect['width'],
            self.rect['height'],
            self.rect['color'],
            3
        )

        self.character.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.character.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.character.change_x = MOVEMENT_SPEED
        elif key == arcade.key.UP:
            self.character.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.character.change_y = -MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.character.change_x = 0
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.character.change_y = 0

    def on_update(self, delta_time):
        self.character.update()

        if self.character.center_x >= SCREEN_WIDTH - self.character.size // 2:
            if self.screen_number == 1:
                next_screen = Screen2()
                next_screen.character.center_x = self.character.size // 2
                next_screen.character.center_y = self.character.center_y
                self.window.show_view(next_screen)
            elif self.screen_number == 2:
                next_screen = Screen3()
                next_screen.character.center_x = self.character.size // 2
                next_screen.character.center_y = self.character.center_y
                self.window.show_view(next_screen)
            elif self.screen_number == 3:
                cutscene = CutsceneScreen()
                self.window.show_view(cutscene)


class Screen1(BaseScreen):
    def __init__(self):
        super().__init__(1)


class Screen2(BaseScreen):
    def __init__(self):
        super().__init__(2)


class Screen3(BaseScreen):
    def __init__(self):
        super().__init__(3)


class CutsceneScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = arcade.Text(
            "тут будет катсцена",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            40,
            anchor_x="center",
            anchor_y="center"
        )

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            start_screen = Screen1()
            start_screen.character.center_x = SCREEN_WIDTH // 2
            start_screen.character.center_y = SCREEN_HEIGHT // 2
            self.window.show_view(start_screen)


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        start_screen = Screen1()
        self.show_view(start_screen)


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()