import arcade
import GameState
import MainMenuScreen


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5
SAVE_DIR = "saves"


game_state = GameState.GameState()


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "казино ларисы долиной")
        self.show_view(MainMenuScreen.MainMenuScreen())

    def on_close(self):
        super().on_close()


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()