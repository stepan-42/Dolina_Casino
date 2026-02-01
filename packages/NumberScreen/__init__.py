import arcade
import random
from GameState import game_state
import BareScreen
import BetScreen
import MainMenuScreen


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


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
            "E - выход | B - изменить ставку | ЛКМ - крутить снова",
            cx, 50, arcade.color.YELLOW, 20, anchor_x="center"
        )
        self.check_win()
    def check_win(self):
        cx = SCREEN_WIDTH // 2
        if self.numbers[0] == self.numbers[1] == self.numbers[2]:
            win = game_state.current_bet * 25
            game_state.balance += win
            self.result = arcade.Text(f"Вы выиграли {win:,}!", cx, SCREEN_HEIGHT // 2 + 100,
                                      arcade.color.GREEN, 24, anchor_x="center")
        else:
            self.result = arcade.Text(f"Вы проиграли {game_state.current_bet:,}!", cx, SCREEN_HEIGHT // 2 + 100,
                                      arcade.color.RED, 24, anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.balance.text = f"Баланс: {game_state.balance:,}"
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
                game_state.balance -= game_state.current_bet
                self.window.show_view(BetScreen.AnimationScreen())
            else:
                self.result = arcade.Text("Недостаточно средств для ставки!", SCREEN_WIDTH // 2,
                                          SCREEN_HEIGHT // 2 + 100,
                                          arcade.color.RED, 24, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.E:
            self.window.show_view(BareScreen.Screen2())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen.BetScreen(False, "slots"))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen.MainMenuScreen())
