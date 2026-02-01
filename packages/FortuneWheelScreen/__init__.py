import arcade
import math
from GameState import game_state
import BetScreen
import random
import BareScreen
import MainMenuScreen
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5



class FortuneWheelScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.wheel_center_x = SCREEN_WIDTH // 2
        self.wheel_center_y = SCREEN_HEIGHT // 2
        self.radius = 200
        self.angle = 0
        self.spinning = False
        self.spin_speed = 0
        self.target_speed = 0
        self.result = None
        self.game_over = False
        self.win_amount = 0
        self.spin_direction = 1
        self.arrow_angle = 90

        multipliers = [50, 20, 10, 5, 3, 2, 1.5, 0]
        colors = [
            arcade.color.RED,
            arcade.color.ORANGE,
            arcade.color.YELLOW,
            arcade.color.GREEN,
            arcade.color.BLUE,
            arcade.color.PURPLE,
            arcade.color.PINK,
            arcade.color.GRAY
        ]

        total_inverse = sum(1 / (m + 1) for m in multipliers)
        self.sectors = []
        current_angle = 0

        for i in range(8):
            multiplier = multipliers[i]
            weight = 1 / (multiplier + 1)
            sector_angle = (weight / total_inverse) * 360

            self.sectors.append({
                "color": colors[i],
                "multiplier": multiplier,
                "text": f"x{multiplier}" if multiplier > 0 else "0",
                "base_start_angle": current_angle,
                "base_end_angle": current_angle + sector_angle,
                "angle_range": sector_angle
            })

            current_angle += sector_angle

        self.title = arcade.Text("КОЛЕСО ФОРТУНЫ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
                                 arcade.color.GOLD, 36, anchor_x="center")
        self.balance_text = arcade.Text("", SCREEN_WIDTH - 10, SCREEN_HEIGHT - 80,
                                        arcade.color.YELLOW, 24, anchor_x="right")
        self.bet_text = arcade.Text("", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
                                    arcade.color.YELLOW, 24, anchor_x="center")
        self.instruction = arcade.Text("Нажмите ЛКМ чтобы крутить колесо", SCREEN_WIDTH // 2, 50,
                                       arcade.color.WHITE, 20, anchor_x="center")
        self.result_text = arcade.Text("", SCREEN_WIDTH // 2, 100,
                                       arcade.color.WHITE, 28, anchor_x="center")
        self.exit_hint = arcade.Text("Нажмите E чтобы вернуться", SCREEN_WIDTH // 2, 20,
                                     arcade.color.YELLOW, 18, anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        for sector in self.sectors:
            start_angle = self.angle + sector["base_start_angle"]
            end_angle = self.angle + sector["base_end_angle"]

            arcade.draw_arc_filled(self.wheel_center_x, self.wheel_center_y, self.radius, self.radius,
                                   sector["color"], start_angle, end_angle)

            arcade.draw_arc_outline(self.wheel_center_x, self.wheel_center_y, self.radius, self.radius,
                                    arcade.color.BLACK, start_angle, end_angle, 3)

            sector_center_angle = start_angle + sector["angle_range"] / 2

            text_angle_rad = math.radians(sector_center_angle)
            text_x = self.wheel_center_x + (self.radius * 0.65) * math.cos(text_angle_rad)
            text_y = self.wheel_center_y + (self.radius * 0.65) * math.sin(text_angle_rad)

            arcade.draw_text(sector["text"], text_x, text_y,
                             arcade.color.WHITE,
                             20, anchor_x="center", anchor_y="center", bold=True,
                             rotation=-sector_center_angle)

        arcade.draw_circle_filled(self.wheel_center_x, self.wheel_center_y, 25, arcade.color.WHITE)
        arcade.draw_circle_outline(self.wheel_center_x, self.wheel_center_y, 25, arcade.color.BLACK, 3)

        arrow_x, arrow_y = self.wheel_center_x, self.wheel_center_y + self.radius + 30

        arrow_angle_rad = math.radians(self.arrow_angle)
        arrow_tip_x = self.wheel_center_x + (self.radius - 60) * math.cos(arrow_angle_rad)
        arrow_tip_y = self.wheel_center_y + (self.radius - 60) * math.sin(arrow_angle_rad)

        arrow_left_angle = math.radians(self.arrow_angle - 15)
        arrow_left_x = self.wheel_center_x + (self.radius * 0.9) * math.cos(arrow_left_angle)
        arrow_left_y = self.wheel_center_y + (self.radius * 0.9) * math.sin(arrow_left_angle)

        arrow_right_angle = math.radians(self.arrow_angle + 15)
        arrow_right_x = self.wheel_center_x + (self.radius * 0.9) * math.cos(arrow_right_angle)
        arrow_right_y = self.wheel_center_y + (self.radius * 0.9) * math.sin(arrow_right_angle)

        arcade.draw_triangle_filled(
            arrow_tip_x, arrow_tip_y,
            arrow_left_x, arrow_left_y,
            arrow_right_x, arrow_right_y,
            arcade.color.RED
        )

        self.title.draw()
        self.balance_text.text = f"Баланс: {game_state.balance:,}"
        self.balance_text.draw()
        self.bet_text.text = f"Ставка: {game_state.current_bet:,}"
        self.bet_text.draw()
        self.instruction.draw()

        if self.game_over:
            self.result_text.draw()

        self.exit_hint.draw()

    def on_mouse_press(self, x, y, button, _):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.game_over:
            self.window.show_view(BetScreen.BetScreen(True, "fortune"))
            return

        if not self.spinning:
            self.spinning = True
            self.spin_direction = random.choice([-1, 1])
            self.target_speed = random.uniform(20, 35) * self.spin_direction
            self.spin_speed = self.target_speed
            self.result = None
            self.game_over = False

    def on_update(self, delta_time):
        if self.spinning:
            self.angle += self.spin_speed

            if abs(self.spin_speed) > 0.3:
                self.spin_speed *= 0.994
            else:
                self.spin_speed = 0
                self.spinning = False
                self.game_over = True
                self.calculate_result()

    def calculate_result(self):
        normalized_angle = (self.angle % 360)

        selected_sector = None

        for sector in self.sectors:
            start_angle = (sector["base_start_angle"] + normalized_angle) % 360
            end_angle = (sector["base_end_angle"] + normalized_angle) % 360

            arrow_point_angle = self.arrow_angle % 360

            if start_angle <= end_angle:
                if start_angle <= arrow_point_angle < end_angle:
                    selected_sector = sector
                    break
            else:
                if arrow_point_angle >= start_angle or arrow_point_angle < end_angle:
                    selected_sector = sector
                    break

        if selected_sector:
            multiplier = selected_sector["multiplier"]
            self.win_amount = int(game_state.current_bet * multiplier)
            game_state.balance += self.win_amount

            if multiplier == 0:
                self.result_text.text = f"Вы проиграли! Выигрыш: 0"
                self.result_text.color = arcade.color.RED
            else:
                self.result_text.text = f"Вы выиграли {self.win_amount:,}! Множитель: x{multiplier}"
                self.result_text.color = arcade.color.GREEN
        else:
            self.result_text.text = "Ошибка определения результата!"
            self.result_text.color = arcade.color.ORANGE

    def on_key_press(self, key, _):
        if key == arcade.key.E:
            self.window.show_view(BareScreen.Screen3())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen.BetScreen(True, "fortune"))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen.MainMenuScreen())