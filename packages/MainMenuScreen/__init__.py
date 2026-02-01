from GameState import game_state
import arcade
import BareScreen
import SaveScreen

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5



class MainMenuScreen(arcade.View):
    def __init__(self):
        super().__init__()
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.title = arcade.Text("КАЗИНО ЛАРИСЫ ДОЛИНОЙ", cx, SCREEN_HEIGHT - 80,
                                 arcade.color.GOLD, 42, anchor_x="center", bold=True)
        self.options = [
            arcade.Text("НОВАЯ ИГРА", cx, cy + 90, arcade.color.WHITE, 32, anchor_x="center"),
            arcade.Text("ЗАГРУЗИТЬ ИГРУ", cx, cy + 30, arcade.color.WHITE, 32, anchor_x="center"),
            arcade.Text("СОХРАНИТЬ ИГРУ", cx, cy - 30, arcade.color.WHITE, 32, anchor_x="center"),
            arcade.Text("ВЫХОД", cx, cy - 90, arcade.color.WHITE, 32, anchor_x="center")
        ]
        self.message = None
        self.message_timer = 0

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.title.draw()
        for option in self.options:
            option.draw()
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

        cx = SCREEN_WIDTH // 2
        for i, option in enumerate(self.options):
            text_width = len(option.text) * 18
            left = cx - text_width // 2 - 20
            right = cx + text_width // 2 + 20
            top = option.y + 30
            bottom = option.y - 5

            if left <= x <= right and bottom <= y <= top:
                if i == 0:
                    game_state.balance = 1000
                    game_state.current_bet = 100
                    game_state.unlocked_screens = [1]
                    game_state.current_screen = 1
                    self.window.show_view(BareScreen.Screen1())
                elif i == 1:
                    self.window.show_view(SaveScreen.SaveSelectScreen("load"))
                elif i == 2:
                    self.window.show_view(SaveScreen.SaveSelectScreen("save"))
                elif i == 3:
                    self.window.close()
                break

    def on_key_press(self, key, _):
        if key == arcade.key.ENTER:
            game_state.balance = 1000
            game_state.current_bet = 100
            game_state.unlocked_screens = [1]
            game_state.current_screen = 1
            self.window.show_view(BareScreen.Screen1())
        elif key == arcade.key.ESCAPE:
            self.window.close()
