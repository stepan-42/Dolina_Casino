import arcade
import time
from GameState import game_state
import BareScreen
import ClickerGameScreen
import TextureScreen
import FortuneWheelScreen
import NumberScreen

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


class BetScreen(arcade.View):
    def __init__(self, show_back, game_type):
        super().__init__()
        self.show_back = show_back
        self.game_type = game_type
        self.bet_amount = str(game_state.current_bet)
        self.message = None
        self.message_timer = 0
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
        self.balance.text = f"Ваш баланс: {game_state.balance:,}"
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
        if self.message and self.message_timer > 0:
            self.message.draw()

    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = None

    def on_mouse_press(self, x, y, button, _):
        global target
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        cx = SCREEN_WIDTH // 2

        if cx - 120 <= x <= cx + 120 and SCREEN_HEIGHT // 2 - 70 <= y <= SCREEN_HEIGHT // 2 - 10:
            self.start_game()
        elif self.back and cx - 100 <= x <= cx + 100 and SCREEN_HEIGHT // 2 - 140 <= y <= SCREEN_HEIGHT // 2 - 90:
            if self.show_back:
                if self.game_type == "clicker":
                    target = BareScreen.Screen1()
                elif self.game_type == "slots":
                    target = BareScreen.Screen2()
                elif self.game_type == "fortune":
                    target = BareScreen.Screen3
            else:
                target = TextureScreen.TextureScreen()
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
                game_state.balance -= bet
                if self.game_type == "clicker":
                    self.window.show_view(ClickerGameScreen.ClickerGameScreen())
                elif self.game_type == "slots":
                    self.window.show_view(AnimationScreen())
                elif self.game_type == "fortune":
                    self.window.show_view(FortuneWheelScreen.FortuneWheelScreen())
                return
        except ValueError:
            msg = "Введите корректное число"

        self.message = arcade.Text(msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 210,
                                   arcade.color.RED, 20, anchor_x="center")
        self.message_timer = 3.0

    def on_key_press(self, key, _):
        if key == arcade.key.ENTER:
            self.start_game()
        elif key == arcade.key.ESCAPE:
            if self.show_back:
                if self.game_type == "clicker":
                    target = BareScreen.Screen1()
                elif self.game_type == "slots":
                    target = BareScreen.Screen2()
                elif self.game_type == "fortune":
                    target = BareScreen.Screen3()
            else:
                target = TextureScreen.TextureScreen()
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
        self.balance.text = f"Баланс: {game_state.balance:,}"
        self.balance.draw()
        self.text.draw()

    def on_update(self, _):
        if time.time() - self.start_time >= self.duration:
            self.window.show_view(NumberScreen.NumbersScreen())


