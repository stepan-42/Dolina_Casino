import arcade
import random
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "аркады Ларисы Долиной"
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

    @property
    def left(self):
        return self.center_x - self.size // 2

    @property
    def right(self):
        return self.center_x + self.size // 2

    @property
    def bottom(self):
        return self.center_y - self.size // 2

    @property
    def top(self):
        return self.center_y + self.size // 2

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(self.left, self.bottom, self.size, self.size, self.color)

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
        self.interaction_hint = None
        self.exit_hint_text = None
        self.prompt_text = None
        self.yes_text = None
        self.no_text = None
        self.near_rect = False
        self.near_exit = False
        self.show_exit_prompt = False
        self.setup_rect()
        self.setup_texts()

    def setup_rect(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT - RECT_HEIGHT // 2 - 50

        left = center_x - RECT_WIDTH // 2
        bottom = center_y - RECT_HEIGHT // 2

        if self.screen_number == 1:
            color = arcade.color.GREEN
        elif self.screen_number == 2:
            color = arcade.color.BLUE
        else:
            color = arcade.color.YELLOW

        self.rect = {
            'left': left,
            'bottom': bottom,
            'right': left + RECT_WIDTH,
            'top': bottom + RECT_HEIGHT,
            'width': RECT_WIDTH,
            'height': RECT_HEIGHT,
            'color': color
        }

    def setup_texts(self):
        self.title_text = arcade.Text(
            f"Экран {self.screen_number}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            30,
            anchor_x="center"
        )

        if self.screen_number == 2:
            self.interaction_hint = arcade.Text(
                "Нажми E у прямоугольника",
                SCREEN_WIDTH // 2,
                50,
                arcade.color.YELLOW,
                20,
                anchor_x="center"
            )

        self.exit_hint_text = arcade.Text(
            "Подойдите ближе к выходу",
            SCREEN_WIDTH // 2,
            80,
            arcade.color.YELLOW,
            20,
            anchor_x="center"
        )

        self.prompt_text = arcade.Text(
            "Выйти?",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            anchor_y="center"
        )

        self.yes_text = arcade.Text(
            "ДА",
            SCREEN_WIDTH // 2 - 75,
            SCREEN_HEIGHT // 2 - 40,
            arcade.color.WHITE,
            22,
            anchor_x="center",
            anchor_y="center"
        )

        self.no_text = arcade.Text(
            "НЕТ",
            SCREEN_WIDTH // 2 + 75,
            SCREEN_HEIGHT // 2 - 40,
            arcade.color.WHITE,
            22,
            anchor_x="center",
            anchor_y="center"
        )

    def check_collision(self):
        char = self.character
        rect = self.rect

        if (char.right > rect['left'] and char.left < rect['right'] and
                char.top > rect['bottom'] and char.bottom < rect['top']):

            overlap_left = char.right - rect['left']
            overlap_right = rect['right'] - char.left
            overlap_bottom = char.top - rect['bottom']
            overlap_top = rect['top'] - char.bottom

            min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

            if min_overlap == overlap_left:
                char.center_x -= overlap_left
            elif min_overlap == overlap_right:
                char.center_x += overlap_right
            elif min_overlap == overlap_bottom:
                char.center_y -= overlap_bottom
            elif min_overlap == overlap_top:
                char.center_y += overlap_top

    def check_near_rect(self):
        char = self.character
        rect = self.rect

        padding = 50
        near_left = rect['left'] - padding
        near_right = rect['right'] + padding
        near_bottom = rect['bottom'] - padding
        near_top = rect['top'] + padding

        self.near_rect = (char.right > near_left and char.left < near_right and
                          char.top > near_bottom and char.bottom < near_top)

    def check_near_exit(self):
        exit_zone_width = 30

        if self.character.right >= SCREEN_WIDTH - exit_zone_width:
            self.near_exit = True
            self.exit_side = "right"
        elif self.character.left <= exit_zone_width:
            self.near_exit = True
            self.exit_side = "left"
        else:
            self.near_exit = False

    def draw_exit_prompt(self):
        if not self.show_exit_prompt:
            return

        box_width = 350
        box_height = 180
        box_left = SCREEN_WIDTH // 2 - box_width // 2
        box_bottom = SCREEN_HEIGHT // 2 - box_height // 2

        arcade.draw_lbwh_rectangle_filled(
            box_left,
            box_bottom,
            box_width,
            box_height,
            arcade.color.DARK_GRAY
        )
        arcade.draw_lbwh_rectangle_outline(
            box_left,
            box_bottom,
            box_width,
            box_height,
            arcade.color.WHITE,
            3
        )

        button_width = 110
        button_height = 55
        yes_button_left = SCREEN_WIDTH // 2 - button_width - 20
        yes_button_bottom = SCREEN_HEIGHT // 2 - button_height // 2 - 40
        no_button_left = SCREEN_WIDTH // 2 + 20
        no_button_bottom = yes_button_bottom

        arcade.draw_lbwh_rectangle_filled(
            yes_button_left,
            yes_button_bottom,
            button_width,
            button_height,
            arcade.color.GREEN
        )
        arcade.draw_lbwh_rectangle_outline(
            yes_button_left,
            yes_button_bottom,
            button_width,
            button_height,
            arcade.color.WHITE,
            2
        )

        arcade.draw_lbwh_rectangle_filled(
            no_button_left,
            no_button_bottom,
            button_width,
            button_height,
            arcade.color.RED
        )
        arcade.draw_lbwh_rectangle_outline(
            no_button_left,
            no_button_bottom,
            button_width,
            button_height,
            arcade.color.WHITE,
            2
        )

        self.prompt_text.draw()
        self.yes_text.draw()
        self.no_text.draw()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.title_text.draw()

        if self.screen_number == 2 and self.near_rect and self.interaction_hint:
            self.interaction_hint.draw()

        if self.near_exit and not self.show_exit_prompt:
            self.exit_hint_text.draw()

        arcade.draw_lbwh_rectangle_outline(
            self.rect['left'],
            self.rect['bottom'],
            self.rect['width'],
            self.rect['height'],
            self.rect['color'],
            3
        )

        self.character.draw()
        self.draw_exit_prompt()

    def on_key_press(self, key, modifiers):
        if self.show_exit_prompt:
            return

        if key == arcade.key.A:
            self.character.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.character.change_x = MOVEMENT_SPEED
        elif key == arcade.key.W:
            self.character.change_y = MOVEMENT_SPEED
        elif key == arcade.key.S:
            self.character.change_y = -MOVEMENT_SPEED

        if self.screen_number == 2 and key == arcade.key.E and self.near_rect:
            texture_screen = TextureScreen()
            self.window.show_view(texture_screen)

    def perform_exit(self):
        if self.exit_side == "right":
            if self.screen_number == 1:
                next_screen = Screen2()
                next_screen.character.center_x = self.character.size // 2 + 50
                next_screen.character.center_y = self.character.center_y
                self.window.show_view(next_screen)
            elif self.screen_number == 2:
                next_screen = Screen3()
                next_screen.character.center_x = self.character.size // 2 + 50
                next_screen.character.center_y = self.character.center_y
                self.window.show_view(next_screen)
            elif self.screen_number == 3:
                cutscene = CutsceneScreen()
                self.window.show_view(cutscene)
        else:
            if self.screen_number == 2:
                prev_screen = Screen1()
                prev_screen.character.center_x = SCREEN_WIDTH - self.character.size // 2 - 50
                prev_screen.character.center_y = self.character.center_y
                self.window.show_view(prev_screen)
            elif self.screen_number == 3:
                prev_screen = Screen2()
                prev_screen.character.center_x = SCREEN_WIDTH - self.character.size // 2 - 50
                prev_screen.character.center_y = self.character.center_y
                self.window.show_view(prev_screen)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_exit_prompt and button == arcade.MOUSE_BUTTON_LEFT:
            button_width = 110
            button_height = 55
            yes_button_left = SCREEN_WIDTH // 2 - button_width - 20
            yes_button_right = yes_button_left + button_width
            yes_button_bottom = SCREEN_HEIGHT // 2 - button_height // 2 - 40
            yes_button_top = yes_button_bottom + button_height

            no_button_left = SCREEN_WIDTH // 2 + 20
            no_button_right = no_button_left + button_width
            no_button_bottom = yes_button_bottom
            no_button_top = yes_button_top

            if (yes_button_left <= x <= yes_button_right and
                    yes_button_bottom <= y <= yes_button_top):
                self.perform_exit()

            elif (no_button_left <= x <= no_button_right and
                  no_button_bottom <= y <= no_button_top):
                self.show_exit_prompt = False
                if self.exit_side == "right":
                    self.character.center_x = SCREEN_WIDTH - 60
                else:
                    self.character.center_x = 60

    def on_key_release(self, key, modifiers):
        if self.show_exit_prompt:
            return

        if key == arcade.key.A or key == arcade.key.D:
            self.character.change_x = 0
        elif key == arcade.key.W or key == arcade.key.S:
            self.character.change_y = 0

    def on_update(self, delta_time):
        if self.show_exit_prompt:
            return

        self.character.update()
        self.check_collision()
        self.check_near_rect()
        self.check_near_exit()

        if self.near_exit:
            exit_threshold = 5
            if self.exit_side == "right" and self.character.right >= SCREEN_WIDTH - exit_threshold:
                self.show_exit_prompt = True
                self.character.change_x = 0
                self.character.change_y = 0
            elif self.exit_side == "left" and self.character.left <= exit_threshold:
                self.show_exit_prompt = True
                self.character.change_x = 0
                self.character.change_y = 0


class TextureScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = arcade.Text(
            "текстура аркады 1",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
            anchor_y="center"
        )
        self.exit_hint = arcade.Text(
            "Нажми E для выхода",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 80,
            arcade.color.YELLOW,
            20,
            anchor_x="center",
            anchor_y="center"
        )
        self.click_hint = arcade.Text(
            "ЛКМ для кручения",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 110,
            arcade.color.YELLOW,
            20,
            anchor_x="center",
            anchor_y="center"
        )

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.text.draw()
        self.exit_hint.draw()
        self.click_hint.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            animation_screen = AnimationScreen()
            self.window.show_view(animation_screen)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.E:
            start_screen = Screen2()
            self.window.show_view(start_screen)


class AnimationScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = arcade.Text(
            "анимация кручения",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
            anchor_y="center"
        )
        self.start_time = time.time()
        self.duration = 3.0

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.text.draw()

    def on_update(self, delta_time):
        current_time = time.time()
        if current_time - self.start_time >= self.duration:
            numbers_screen = NumbersScreen()
            self.window.show_view(numbers_screen)


class NumbersScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.numbers = [random.randint(0, 3) for _ in range(3)]
        self.number_texts = []
        self.setup_texts()
        self.exit_hint = arcade.Text(
            "Нажми E для выхода",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 120,
            arcade.color.YELLOW,
            20,
            anchor_x="center",
            anchor_y="center"
        )
        self.reroll_hint = arcade.Text(
            "ЛКМ для повторного кручения",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 150,
            arcade.color.YELLOW,
            20,
            anchor_x="center",
            anchor_y="center"
        )

    def setup_texts(self):
        spacing = 80
        start_x = SCREEN_WIDTH // 2 - spacing
        center_y = SCREEN_HEIGHT // 2

        for i, number in enumerate(self.numbers):
            text = arcade.Text(
                str(number),
                start_x + i * spacing,
                center_y,
                arcade.color.WHITE,
                50,
                anchor_x="center",
                anchor_y="center"
            )
            self.number_texts.append(text)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        num_width = 60
        num_height = 80
        spacing = 80
        start_x = SCREEN_WIDTH // 2 - spacing
        center_y = SCREEN_HEIGHT // 2

        for i in range(3):
            left = start_x + i * spacing - num_width // 2
            bottom = center_y - num_height // 2
            arcade.draw_lbwh_rectangle_outline(
                left,
                bottom,
                num_width,
                num_height,
                arcade.color.WHITE,
                2
            )

            self.number_texts[i].draw()

        self.exit_hint.draw()
        self.reroll_hint.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            animation_screen = AnimationScreen()
            self.window.show_view(animation_screen)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.E:
            start_screen = Screen2()
            self.window.show_view(start_screen)


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
            30,
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