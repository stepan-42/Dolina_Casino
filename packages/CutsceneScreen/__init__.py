from GameState import game_state
import arcade
import Character


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


class CutsceneScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.character = Character.Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.texts = [
            arcade.Text("Здесь должна была быть катсцена", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60,
                        arcade.color.GOLD, 36, anchor_x="center"),
            arcade.Text("Нажмите ПРОБЕЛ чтобы начать новую игру",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120,
                        arcade.color.WHITE, 20, anchor_x="center"),
            arcade.Text("Нажмите ESC для выхода в меню",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150,
                        arcade.color.WHITE, 20, anchor_x="center")
        ]

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        for text in self.texts:
            text.draw()

    def on_key_press(self, key, _):
        if key == arcade.key.SPACE:
            game_state.balance = 1000
            game_state.current_bet = 100
            game_state.unlocked_screens = [1]
            game_state.current_screen = 1
            self.window.show_view(BareScreen.Screen1())
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen.MainMenuScreen())