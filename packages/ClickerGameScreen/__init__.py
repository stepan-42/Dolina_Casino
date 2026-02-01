import arcade
import time
from GameState import game_state
import random
import BetScreen

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


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
        arcade.set_background_color(arcade.color.BLACK)
        self.title.draw()
        self.instruction.draw()
        self.bet_text.text = f"Ставка: {game_state.current_bet:,}"
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
            self.window.show_view(BetScreen.BetScreen(True, "clicker"))
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
            self.result_amount.text = f"+{game_state.current_bet * 2:,}"
            self.result_amount.color = arcade.color.GOLD
        elif self.ai_ball_top.center_x >= self.finish_line or self.ai_ball_bottom.center_x >= self.finish_line:
            self.game_over = True
            self.result_title.text, self.result_title.color = "ПРОИГРЫШ", arcade.color.RED
            self.result_amount.text = f"-{game_state.current_bet:,}"
            self.result_amount.color = arcade.color.RED

    def on_key_press(self, key, _):
        if self.game_over:
            self.window.show_view(BetScreen.BetScreen(True, "clicker"))