import arcade
import random
import time

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


class GameState:
    def __init__(self):
        self.balance, self.current_bet, self.selected_game = 1000, 100, None


game_state = GameState()


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


class BaseScreen(arcade.View):
    COLORS = [None, arcade.color.GREEN, arcade.color.BLUE, arcade.color.YELLOW]

    def __init__(self, screen_num):
        super().__init__()
        self.screen_num = screen_num
        self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.near_rect = self.near_exit = self.show_exit_prompt = False
        self.exit_side = None

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT - RECT_HEIGHT // 2 - 50
        self.rect = {
            'left': cx - RECT_WIDTH // 2,
            'bottom': cy - RECT_HEIGHT // 2,
            'right': cx + RECT_WIDTH // 2,
            'top': cy + RECT_HEIGHT // 2,
            'width': RECT_WIDTH,
            'height': RECT_HEIGHT,
            'color': self.COLORS[screen_num]
        }

        self.title = arcade.Text(
            f"игральный зал {screen_num}",
            cx, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 30,
            anchor_x="center"
        )
        self.balance_text = arcade.Text(
            "", SCREEN_WIDTH - 10, SCREEN_HEIGHT - 30,
            arcade.color.GOLD, 24,
            anchor_x="right"
        )
        self.interaction_hint = arcade.Text(
            "Нажми E у прямоугольника", cx, 50,
            arcade.color.YELLOW, 20,
            anchor_x="center"
        ) if screen_num in (1, 2) else None
        self.exit_hint = arcade.Text(
            "Подойдите ближе к выходу", cx, 80,
            arcade.color.YELLOW, 20,
            anchor_x="center"
        )
        self.prompt = arcade.Text(
            "Выйти?", cx, SCREEN_HEIGHT // 2 + 50,
            arcade.color.WHITE, 28,
            anchor_x="center"
        )
        self.yes_text = arcade.Text(
            "ДА", cx - 75, SCREEN_HEIGHT // 2 - 45,
            arcade.color.WHITE, 22,
            anchor_x="center"
        )
        self.no_text = arcade.Text(
            "НЕТ", cx + 75, SCREEN_HEIGHT // 2 - 45,
            arcade.color.WHITE, 22,
            anchor_x="center"
        )

    def check_collision(self):
        c, r = self.character, self.rect
        if (c.right > r['left'] and c.left < r['right'] and
                c.top > r['bottom'] and c.bottom < r['top']):
            overlaps = [
                c.right - r['left'],
                r['right'] - c.left,
                c.top - r['bottom'],
                r['top'] - c.bottom
            ]
            min_idx = overlaps.index(min(overlaps))
            if min_idx == 0:
                c.center_x -= overlaps[0]
            elif min_idx == 1:
                c.center_x += overlaps[1]
            elif min_idx == 2:
                c.center_y -= overlaps[2]
            else:
                c.center_y += overlaps[3]

    def check_near_rect(self):
        c, r, p = self.character, self.rect, 50
        self.near_rect = (
                c.right > r['left'] - p and c.left < r['right'] + p and
                c.top > r['bottom'] - p and c.bottom < r['top'] + p
        )

    def check_near_exit(self):
        ez = 30
        if self.character.right >= SCREEN_WIDTH - ez:
            self.near_exit, self.exit_side = True, "right"
        elif self.character.left <= ez:
            self.near_exit, self.exit_side = True, "left"
        else:
            self.near_exit = False

    def draw_exit_prompt(self):
        if not self.show_exit_prompt:
            return
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        arcade.draw_lbwh_rectangle_filled(cx - 175, cy - 90, 350, 180, arcade.color.DARK_GRAY)
        arcade.draw_lbwh_rectangle_outline(cx - 175, cy - 90, 350, 180, arcade.color.WHITE, 3)
        arcade.draw_lbwh_rectangle_filled(cx - 125, cy - 65, 110, 55, arcade.color.GREEN)
        arcade.draw_lbwh_rectangle_outline(cx - 125, cy - 65, 110, 55, arcade.color.WHITE, 2)
        arcade.draw_lbwh_rectangle_filled(cx + 20, cy - 65, 110, 55, arcade.color.RED)
        arcade.draw_lbwh_rectangle_outline(cx + 20, cy - 65, 110, 55, arcade.color.WHITE, 2)
        self.prompt.draw()
        self.yes_text.draw()
        self.no_text.draw()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.title.draw()
        self.balance_text.text = f"Баланс: {game_state.balance}"
        self.balance_text.draw()

        if self.screen_num in (1, 2) and self.near_rect and self.interaction_hint:
            self.interaction_hint.draw()
        if self.near_exit and not self.show_exit_prompt:
            self.exit_hint.draw()

        arcade.draw_lbwh_rectangle_outline(
            self.rect['left'], self.rect['bottom'],
            self.rect['width'], self.rect['height'],
            self.rect['color'], 3
        )
        self.character.draw()
        self.draw_exit_prompt()

    def on_key_press(self, key, _):
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
        elif key == arcade.key.E and self.near_rect and self.screen_num in (1, 2):
            game = "clicker" if self.screen_num == 1 else "slots"
            self.window.show_view(BetScreen(True, game))

    def perform_exit(self):
        if self.exit_side == "right":
            next_cls = {1: Screen2, 2: Screen3, 3: CutsceneScreen}.get(self.screen_num)
        else:
            next_cls = {2: Screen1, 3: Screen2}.get(self.screen_num)

        if next_cls:
            nxt = next_cls()
            if self.exit_side == "right":
                nxt.character.center_x = self.character.size // 2 + 50
            else:
                nxt.character.center_x = SCREEN_WIDTH - self.character.size // 2 - 50
            nxt.character.center_y = self.character.center_y
            self.window.show_view(nxt)

    def on_mouse_press(self, x, y, button, _):
        if not (self.show_exit_prompt and button == arcade.MOUSE_BUTTON_LEFT):
            return

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        yes_left, yes_right = cx - 125, cx - 15
        no_left, no_right = cx + 20, cx + 130
        btn_bottom, btn_top = cy - 65, cy - 10

        if yes_left <= x <= yes_right and btn_bottom <= y <= btn_top:
            self.perform_exit()
        elif no_left <= x <= no_right and btn_bottom <= y <= btn_top:
            self.show_exit_prompt = False
            self.character.center_x = 60 if self.exit_side == "left" else SCREEN_WIDTH - 60

    def on_key_release(self, key, _):
        if self.show_exit_prompt:
            return
        if key in (arcade.key.A, arcade.key.D):
            self.character.change_x = 0
        elif key in (arcade.key.W, arcade.key.S):
            self.character.change_y = 0

    def on_update(self, _):
        if self.show_exit_prompt:
            return

        self.character.update()
        self.check_collision()
        self.check_near_rect()
        self.check_near_exit()

        if self.near_exit:
            et = 5
            if (self.exit_side == "right" and self.character.right >= SCREEN_WIDTH - et) or \
                    (self.exit_side == "left" and self.character.left <= et):
                self.show_exit_prompt = True
                self.character.change_x = 0
                self.character.change_y = 0


class Screen1(BaseScreen):
    def __init__(self): super().__init__(1)


class Screen2(BaseScreen):
    def __init__(self): super().__init__(2)


class Screen3(BaseScreen):
    def __init__(self): super().__init__(3)


class Ball:
    def __init__(self, x, y, color):
        self.center_x, self.center_y, self.color, self.size = x, y, color, 60

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.size // 2, self.color)
        arcade.draw_circle_filled(self.center_x, self.center_y, self.size // 4, arcade.color.WHITE)

    def move_forward(self, d):
        self.center_x += d


class ClickerGameScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_ball = Ball(150, SCREEN_HEIGHT // 2, arcade.color.GREEN)
        self.ai_ball_top = Ball(150, SCREEN_HEIGHT // 2 + 100, arcade.color.RED)
        self.ai_ball_bottom = Ball(150, SCREEN_HEIGHT // 2 - 100, arcade.color.RED)
        self.finish_line = SCREEN_WIDTH - 150
        self.game_over = False
        self.last_ai_move = time.time()
        self.ai_interval = 0.25

        cx = SCREEN_WIDTH // 2
        self.title = arcade.Text("иподром", cx, SCREEN_HEIGHT - 40, arcade.color.YELLOW, 30, anchor_x="center")
        self.instruction = arcade.Text("Кликай в ЛЮБОЙ части экрана!", cx, SCREEN_HEIGHT - 80, arcade.color.WHITE, 20,
                                       anchor_x="center")
        self.bet_text = arcade.Text("", cx, 50, arcade.color.GOLD, 24, anchor_x="center")
        self.result_title = arcade.Text("", cx, SCREEN_HEIGHT // 2 + 50, arcade.color.WHITE, 36, anchor_x="center")
        self.result_amount = arcade.Text("", cx, SCREEN_HEIGHT // 2, arcade.color.WHITE, 28, anchor_x="center")
        self.exit_hint = arcade.Text("Нажмите любую клавишу или кнопку мыши", cx, SCREEN_HEIGHT // 2 - 80,
                                     arcade.color.WHITE, 20, anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE)
        self.title.draw()
        self.instruction.draw()
        self.bet_text.text = f"Ставка: {game_state.current_bet}"
        self.bet_text.draw()

        for y in [self.player_ball.center_y, self.ai_ball_top.center_y, self.ai_ball_bottom.center_y]:
            arcade.draw_line(100, y, SCREEN_WIDTH - 100, y, arcade.color.WHITE, 10)
        arcade.draw_line(self.finish_line, 100, self.finish_line, SCREEN_HEIGHT - 100, arcade.color.RED, 5)

        self.player_ball.draw()
        self.ai_ball_top.draw()
        self.ai_ball_bottom.draw()

        if self.game_over:
            cx = SCREEN_WIDTH // 2
            arcade.draw_lbwh_rectangle_filled(cx - 200, SCREEN_HEIGHT // 2 - 100, 400, 200, arcade.color.DARK_GRAY)
            arcade.draw_lbwh_rectangle_outline(cx - 200, SCREEN_HEIGHT // 2 - 100, 400, 200, arcade.color.WHITE, 3)
            self.result_title.draw()
            self.result_amount.draw()
            self.exit_hint.draw()

    def on_mouse_press(self, x, y, button, _):
        if self.game_over:
            self.window.show_view(BetScreen(True, "clicker"))
            return
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player_ball.move_forward(15)
            self.check_winner()

    def on_update(self, _):
        if self.game_over:
            return

        ct = time.time()
        if ct - self.last_ai_move >= self.ai_interval:
            self.ai_ball_top.move_forward(random.randint(5, 25))
            self.ai_ball_bottom.move_forward(random.randint(5, 25))
            self.last_ai_move = ct
            self.ai_interval = random.uniform(0.2, 0.3)
            self.check_winner()

    def check_winner(self):
        if self.player_ball.center_x >= self.finish_line:
            self.game_over = True
            game_state.balance += game_state.current_bet * 2
            self.result_title.text, self.result_title.color = "ПОБЕДА!", arcade.color.GREEN
            self.result_amount.text, self.result_amount.color = f"+{game_state.current_bet * 2}", arcade.color.GOLD
        elif self.ai_ball_top.center_x >= self.finish_line or self.ai_ball_bottom.center_x >= self.finish_line:
            self.game_over = True
            self.result_title.text, self.result_title.color = "ПРОИГРЫШ", arcade.color.RED
            self.result_amount.text, self.result_amount.color = f"-{game_state.current_bet}", arcade.color.RED

    def on_key_press(self, key, _):
        if self.game_over:
            self.window.show_view(BetScreen(True, "clicker"))


class TextureScreen(arcade.View):
    def __init__(self):
        super().__init__()
        cx = SCREEN_WIDTH // 2
        self.balance_text = arcade.Text("", SCREEN_WIDTH - 10, SCREEN_HEIGHT - 30, arcade.color.GOLD, 24,
                                        anchor_x="right")
        self.bet_text = arcade.Text("", cx, SCREEN_HEIGHT // 2 + 60, arcade.color.GOLD, 28, anchor_x="center")
        self.text = arcade.Text("текстура аркады 1", cx, SCREEN_HEIGHT // 2 + 100, arcade.color.WHITE, 30,
                                anchor_x="center")
        self.coeff = arcade.Text("Коэффициент: x25", cx, SCREEN_HEIGHT // 2 + 20, arcade.color.YELLOW, 24,
                                 anchor_x="center")
        self.change_hint = arcade.Text("B - изменить ставку", cx, SCREEN_HEIGHT // 2 - 30, arcade.color.YELLOW, 20,
                                       anchor_x="center")
        self.exit_hint = arcade.Text("E - выход | ЛКМ - крутить", cx, SCREEN_HEIGHT // 2 - 60, arcade.color.YELLOW, 20,
                                     anchor_x="center")
        self.message = None

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.balance_text.text = f"Баланс: {game_state.balance}"
        self.balance_text.draw()
        self.bet_text.text = f"Ставка: {game_state.current_bet}"
        self.bet_text.draw()
        self.text.draw()
        self.coeff.draw()
        self.change_hint.draw()
        self.exit_hint.draw()
        if self.message:
            self.message.draw()

    def on_mouse_press(self, x, y, button, _):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if game_state.current_bet <= game_state.balance:
            self.window.show_view(AnimationScreen())
        else:
            self.message = arcade.Text("Недостаточно средств!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                                       arcade.color.RED, 24, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.E:
            self.window.show_view(Screen2())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen(False, "slots"))


class BetScreen(arcade.View):
    def __init__(self, show_back, game_type):
        super().__init__()
        self.show_back = show_back
        self.game_type = game_type
        self.bet_amount = str(game_state.current_bet)
        self.message = None
        cx = SCREEN_WIDTH // 2

        self.title = arcade.Text("Установите ставку", cx, SCREEN_HEIGHT // 2 + 120, arcade.color.WHITE, 30,
                                 anchor_x="center")
        self.balance = arcade.Text("", cx, SCREEN_HEIGHT // 2 + 80, arcade.color.YELLOW, 24, anchor_x="center")
        self.bet_display = arcade.Text("", cx, SCREEN_HEIGHT // 2 + 20, arcade.color.WHITE, 50, anchor_x="center")
        self.start = arcade.Text("НАЧАТЬ ИГРУ", cx, SCREEN_HEIGHT // 2 - 50, arcade.color.GREEN, 28, anchor_x="center")
        self.back = arcade.Text("НАЗАД", cx, SCREEN_HEIGHT // 2 - 125, arcade.color.RED, 24,
                                anchor_x="center") if show_back else None
        self.hint = arcade.Text("Введите сумму ставки", cx, SCREEN_HEIGHT // 2 - 180, arcade.color.YELLOW, 20,
                                anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_GRAY)
        cx = SCREEN_WIDTH // 2
        arcade.draw_lbwh_rectangle_filled(cx - 225, SCREEN_HEIGHT // 2 - 150, 450, 350, arcade.color.BLACK)
        arcade.draw_lbwh_rectangle_outline(cx - 225, SCREEN_HEIGHT // 2 - 150, 450, 350, arcade.color.WHITE, 3)

        self.title.draw()
        self.balance.text = f"Ваш баланс: {game_state.balance}"
        self.balance.draw()
        self.bet_display.text = self.bet_amount or "0"
        self.bet_display.draw()

        arcade.draw_lbwh_rectangle_filled(cx - 120, SCREEN_HEIGHT // 2 - 70, 240, 60, arcade.color.DARK_GREEN)
        arcade.draw_lbwh_rectangle_outline(cx - 120, SCREEN_HEIGHT // 2 - 70, 240, 60, arcade.color.WHITE, 3)
        self.start.draw()

        if self.back:
            arcade.draw_lbwh_rectangle_filled(cx - 100, SCREEN_HEIGHT // 2 - 140, 200, 50, arcade.color.DARK_RED)
            arcade.draw_lbwh_rectangle_outline(cx - 100, SCREEN_HEIGHT // 2 - 140, 200, 50, arcade.color.WHITE, 3)
            self.back.draw()

        self.hint.draw()
        if self.message:
            self.message.draw()

    def on_mouse_press(self, x, y, button, _):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        cx = SCREEN_WIDTH // 2

        if cx - 120 <= x <= cx + 120 and SCREEN_HEIGHT // 2 - 70 <= y <= SCREEN_HEIGHT // 2 - 10:
            self.start_game()
        elif self.back and cx - 100 <= x <= cx + 100 and SCREEN_HEIGHT // 2 - 120 <= y <= SCREEN_HEIGHT // 2 - 70:
            if self.show_back:
                target = Screen1() if self.game_type == "clicker" else Screen2()
            else:
                target = TextureScreen()
            self.window.show_view(target)

    def start_game(self):
        try:
            bet = int(self.bet_amount)
            if bet <= 0:
                msg = "Ставка должна быть больше 0"
            elif bet > game_state.balance:
                msg = "Недостаточно средств"
            else:
                game_state.current_bet = bet
                game_state.selected_game = self.game_type

                if self.game_type == "clicker":
                    game_state.balance -= bet
                    self.window.show_view(ClickerGameScreen())
                else:
                    self.window.show_view(AnimationScreen())
                return
        except ValueError:
            msg = "Введите корректное число"

        self.message = arcade.Text(msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180,
                                   arcade.color.RED, 20, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.ENTER:
            self.start_game()
        elif key == arcade.key.ESCAPE:
            if self.show_back:
                target = Screen1() if self.game_type == "clicker" else Screen2()
            else:
                target = TextureScreen()
            self.window.show_view(target)
        elif key == arcade.key.BACKSPACE:
            self.bet_amount = self.bet_amount[:-1] if self.bet_amount else ""
        elif arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            if len(self.bet_amount) < 6:
                self.bet_amount += chr(key)


class AnimationScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = arcade.Text("анимация кручения", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                arcade.color.WHITE, 30, anchor_x="center")
        self.balance = arcade.Text("", SCREEN_WIDTH - 10, SCREEN_HEIGHT - 30, arcade.color.GOLD, 24, anchor_x="right")
        self.start_time = time.time()
        self.duration = 3.0

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.balance.text = f"Баланс: {game_state.balance}"
        self.balance.draw()
        self.text.draw()

    def on_update(self, _):
        if time.time() - self.start_time >= self.duration:
            self.window.show_view(NumbersScreen())


class NumbersScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.numbers = [random.randint(0, 3) for _ in range(3)]
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        self.number_texts = [
            arcade.Text(str(n), cx - 80 + i * 80, cy - 20, arcade.color.WHITE, 50, anchor_x="center")
            for i, n in enumerate(self.numbers)
        ]

        self.balance = arcade.Text("", SCREEN_WIDTH - 10, SCREEN_HEIGHT - 30, arcade.color.GOLD, 24, anchor_x="right")
        self.exit_hint = arcade.Text(
            "E - выход | B - изменить ставку\nЛКМ - крутить снова",
            cx, 50, arcade.color.YELLOW, 20, anchor_x="center"
        )
        self.check_win()

    def check_win(self):
        cx = SCREEN_WIDTH // 2
        if self.numbers[0] == self.numbers[1] == self.numbers[2]:
            win = game_state.current_bet * 25
            game_state.balance += win
            self.result = arcade.Text(f"Вы выиграли {win}!", cx, SCREEN_HEIGHT // 2 + 100,
                                      arcade.color.GREEN, 24, anchor_x="center")
        else:
            game_state.balance -= game_state.current_bet
            self.result = arcade.Text(f"Вы проиграли {game_state.current_bet}!", cx, SCREEN_HEIGHT // 2 + 100,
                                      arcade.color.RED, 24, anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.balance.text = f"Баланс: {game_state.balance}"
        self.balance.draw()

        for i in range(3):
            left = SCREEN_WIDTH // 2 - 80 + i * 80 - 30
            arcade.draw_lbwh_rectangle_outline(left, SCREEN_HEIGHT // 2 - 40, 60, 80, arcade.color.WHITE, 2)
            self.number_texts[i].draw()

        self.result.draw()
        self.exit_hint.draw()

    def on_mouse_press(self, x, y, button, _):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if game_state.current_bet <= game_state.balance:
                self.window.show_view(AnimationScreen())
            else:
                self.result = arcade.Text("Недостаточно средств для ставки!", SCREEN_WIDTH // 2,
                                          SCREEN_HEIGHT // 2 + 100,
                                          arcade.color.RED, 24, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.E:
            self.window.show_view(Screen2())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen(False, "slots"))


class CutsceneScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = arcade.Text("тут будет катсцена", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                arcade.color.WHITE, 30, anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.text.draw()

    def on_key_press(self, key, _):
        if key == arcade.key.ESCAPE:
            s = Screen1()
            s.character.center_x = SCREEN_WIDTH // 2
            s.character.center_y = SCREEN_HEIGHT // 2
            self.window.show_view(s)


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "казино ларисы долиной")
        self.show_view(Screen1())


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()