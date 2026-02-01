import arcade
from GameState import game_state
import BareScreen
import BetScreen
import MainMenuScreen

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5



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
        self.message_timer = 0

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.balance_text.text = f"Баланс: {game_state.balance:,}"
        self.balance_text.draw()
        self.bet_text.text = f"Ставка: {game_state.current_bet:,}"
        self.bet_text.draw()
        self.text.draw()
        self.coeff.draw()
        self.change_hint.draw()
        self.exit_hint.draw()
        if self.message and self.message_timer > 0:
            self.message.draw()

    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = None

    def on_mouse_press(self, x, y, button, _):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        self.window.show_view(BetScreen.AnimationScreen())

    def on_key_press(self, key, _):
        if key == arcade.key.E:
            self.window.show_view(BareScreen.Screen2())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen.BetScreen(False, "slots"))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen.MainMenuScreen())