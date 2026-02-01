import arcade
from GameState import game_state
import Character
import BetScreen
import MainMenuScreen
import CutsceneScreen

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5


class BaseScreen(arcade.View):
    COLORS = [None, arcade.color.GREEN, arcade.color.BLUE, arcade.color.YELLOW]
    UNLOCK_COSTS = {1: 5000, 2: 25000, 3: 100000}

    def __init__(self, screen_num):
        super().__init__()
        self.screen_num = screen_num
        game_state.current_screen = screen_num

        self.character = Character.Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.near_rect = self.near_exit = self.show_exit_prompt = False
        self.exit_side = None
        self.purchase_prompt = False
        self.purchase_cost = 0
        self.purchase_target = None
        self.purchase_error = False

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
            "Нажми E возле аркады", cx, 50,
            arcade.color.YELLOW, 20,
            anchor_x="center"
        ) if screen_num in (1, 2, 3) else None
        self.exit_hint = arcade.Text(
            "", cx, 80,
            arcade.color.YELLOW, 20,
            anchor_x="center"
        )
        self.locked_hint = arcade.Text(
            "", cx, 110,
            arcade.color.RED, 22,
            anchor_x="center"
        )
        self.prompt = arcade.Text(
            "", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
            arcade.color.WHITE, 28,
            anchor_x="center"
        )
        self.yes_text = arcade.Text(
            "ДА", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 45,
            arcade.color.WHITE, 22,
            anchor_x="center"
        )
        self.no_text = arcade.Text(
            "НЕТ", SCREEN_WIDTH // 2 + 75, SCREEN_HEIGHT // 2 - 45,
            arcade.color.WHITE, 22,
            anchor_x="center"
        )
        self.purchase_error_text = arcade.Text(
            "Недостаточно средств!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
            arcade.color.RED, 20,
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

    def get_next_screen_info(self):
        if self.exit_side == "right":
            if self.screen_num == 1:
                return 2, self.UNLOCK_COSTS[1]
            elif self.screen_num == 2:
                return 3, self.UNLOCK_COSTS[2]
            elif self.screen_num == 3:
                return 4, self.UNLOCK_COSTS[3]
        elif self.exit_side == "left":
            if self.screen_num == 2:
                return 1, 0
            elif self.screen_num == 3:
                return 2, 0
        return None, 0

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

        if self.purchase_prompt:
            if self.purchase_error:
                self.prompt.text = "Недостаточно средств!"
                self.prompt.color = arcade.color.RED
            else:
                self.prompt.text = f"Купить проход за {self.purchase_cost:,}?"
                self.prompt.color = arcade.color.YELLOW
        else:
            self.prompt.text = "Выйти?"
            self.prompt.color = arcade.color.WHITE

        self.prompt.draw()
        self.yes_text.draw()
        self.no_text.draw()

        if self.purchase_error:
            self.purchase_error_text.draw()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.title.draw()
        self.balance_text.text = f"Баланс: {game_state.balance:,}"
        self.balance_text.draw()

        next_screen, cost = self.get_next_screen_info()
        if self.near_exit:
            if next_screen is not None and next_screen not in game_state.unlocked_screens:
                self.locked_hint.text = f"ЗАКРЫТО! Купить за {cost:,} (E)"
                self.locked_hint.draw()
            elif self.exit_side == "right":
                self.exit_hint.text = "Выход вправо (подойдите ближе)"
                self.exit_hint.draw()
            else:
                self.exit_hint.text = "Выход влево (подойдите ближе)"
                self.exit_hint.draw()
        elif self.screen_num in (1, 2, 3) and self.near_rect and self.interaction_hint:
            self.interaction_hint.draw()

        arcade.draw_lbwh_rectangle_outline(
            self.rect['left'], self.rect['bottom'],
            self.rect['width'], self.rect['height'],
            self.rect['color'], 3
        )
        self.character.draw()
        self.draw_exit_prompt()

    def on_key_press(self, key, _):
        if self.show_exit_prompt:
            if key == arcade.key.ESCAPE:
                self.show_exit_prompt = False
                self.purchase_prompt = False
                self.purchase_error = False
                if self.exit_side == "left":
                    self.character.center_x = 60
                else:
                    self.character.center_x = SCREEN_WIDTH - 60
            return

        if key == arcade.key.A:
            self.character.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.character.change_x = MOVEMENT_SPEED
        elif key == arcade.key.W:
            self.character.change_y = MOVEMENT_SPEED
        elif key == arcade.key.S:
            self.character.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.E:
            if self.near_rect and self.screen_num in (1, 2, 3):
                if self.screen_num == 1:
                    self.window.show_view(BetScreen.BetScreen(True, "clicker"))
                elif self.screen_num == 2:
                    self.window.show_view(BetScreen.BetScreen(True, "slots"))
                elif self.screen_num == 3:
                    self.window.show_view(BetScreen.BetScreen(True, "fortune"))
            elif self.near_exit:
                next_screen, cost = self.get_next_screen_info()
                if next_screen is not None and next_screen not in game_state.unlocked_screens:
                    if game_state.unlock_screen(next_screen, cost):
                        self.perform_exit()
                    else:
                        self.show_exit_prompt = True
                        self.purchase_prompt = True
                        self.purchase_cost = cost
                        self.purchase_target = next_screen
                        self.purchase_error = True
                        self.character.change_x = 0
                        self.character.change_y = 0
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen.MainMenuScreen())

    def perform_exit(self):
        if self.exit_side == "right":
            if self.screen_num == 1:
                next_cls = Screen2
                next_screen_num = 2
            elif self.screen_num == 2:
                next_cls = Screen3
                next_screen_num = 3
            elif self.screen_num == 3:
                next_cls = CutsceneScreen.CutsceneScreen
                next_screen_num = 4
            else:
                return
        else:
            if self.screen_num == 2:
                next_cls = Screen1
                next_screen_num = 1
            elif self.screen_num == 3:
                next_cls = Screen2
                next_screen_num = 2
            else:
                return

        if next_screen_num not in game_state.unlocked_screens and next_screen_num != 4:
            return

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
            if self.purchase_prompt:
                if game_state.unlock_screen(self.purchase_target, self.purchase_cost):
                    self.perform_exit()
                else:
                    self.purchase_error = True
            else:
                self.perform_exit()
        elif no_left <= x <= no_right and btn_bottom <= y <= btn_top:
            self.show_exit_prompt = False
            self.purchase_prompt = False
            self.purchase_error = False
            if self.exit_side == "left":
                self.character.center_x = 60
            else:
                self.character.center_x = SCREEN_WIDTH - 60

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
            touching_edge = (
                    (self.exit_side == "right" and self.character.right >= SCREEN_WIDTH - et) or
                    (self.exit_side == "left" and self.character.left <= et)
            )

            if touching_edge:
                next_screen, cost = self.get_next_screen_info()
                if next_screen is None:
                    return

                if next_screen in game_state.unlocked_screens:
                    self.show_exit_prompt = True
                    self.purchase_prompt = False
                    self.purchase_error = False
                elif cost > 0:
                    self.show_exit_prompt = True
                    self.purchase_prompt = True
                    self.purchase_cost = cost
                    self.purchase_target = next_screen
                    self.purchase_error = False

                self.character.change_x = 0
                self.character.change_y = 0


class Screen1(BaseScreen):
    def __init__(self): super().__init__(1)


class Screen2(BaseScreen):
    def __init__(self): super().__init__(2)


class Screen3(BaseScreen):
    def __init__(self): super().__init__(3)
