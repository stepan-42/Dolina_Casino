import arcade
import json
import os
import random
import time
import math


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5
SAVE_DIR = "saves"


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
        self.window.show_view(AnimationScreen())

    def on_key_press(self, key, _):
        if key == arcade.key.E:
            self.window.show_view(Screen2())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen(False, "slots"))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen())


class SaveSelectScreen(arcade.View):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.slots_info = []
        cx = SCREEN_WIDTH // 2

        for i in range(1, 4):
            path = os.path.join(SAVE_DIR, f"slot{i}.json")
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        balance = data.get('balance', 0)
                        mtime = os.path.getmtime(path)
                        timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
                        self.slots_info.append((i, True, balance, timestamp))
                except:
                    self.slots_info.append((i, False, 0, ""))
            else:
                self.slots_info.append((i, False, 0, ""))

        title_text = "ЗАГРУЗИТЬ ИГРУ" if mode == "load" else "СОХРАНИТЬ ИГРУ"
        self.title = arcade.Text(title_text, cx, SCREEN_HEIGHT - 60,
                                 arcade.color.GOLD, 36, anchor_x="center", bold=True)
        self.slot_texts = []
        y_start = SCREEN_HEIGHT - 150
        for i, (slot_num, exists, balance, timestamp) in enumerate(self.slots_info):
            y = y_start - i * 100
            if exists:
                text = f"Слот {slot_num}: {balance:,} монет ({timestamp})"
                color = arcade.color.WHITE
            else:
                text = f"Слот {slot_num}: пустой"
                color = arcade.color.GRAY
            self.slot_texts.append(arcade.Text(text, cx, y, color, 24, anchor_x="center"))

        self.back_text = arcade.Text("НАЗАД", cx, 80, arcade.color.RED, 28, anchor_x="center")
        self.message = None
        self.message_timer = 0

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.title.draw()
        for text in self.slot_texts:
            text.draw()
        self.back_text.draw()
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
        y_start = SCREEN_HEIGHT - 150

        for i, (slot_num, exists, balance, timestamp) in enumerate(self.slots_info):
            text_y = y_start - i * 100
            text_width = len(self.slot_texts[i].text) * 14
            left = cx - text_width // 2 - 20
            right = cx + text_width // 2 + 20
            top = text_y + 20
            bottom = text_y - 20

            if left <= x <= right and bottom <= y <= top:
                if self.mode == "load":
                    if exists:
                        if game_state.load_from_slot(slot_num):
                            if game_state.current_screen == 1:
                                view = Screen1()
                            elif game_state.current_screen == 2:
                                view = Screen2()
                            elif game_state.current_screen == 3:
                                view = Screen3()
                            else:
                                view = CutsceneScreen()
                            view.character.center_x = SCREEN_WIDTH // 2
                            view.character.center_y = SCREEN_HEIGHT // 2
                            self.window.show_view(view)
                            return
                        else:
                            self.show_message("Ошибка загрузки!", arcade.color.RED)
                    else:
                        self.show_message("Слот пустой!", arcade.color.RED)
                else:
                    game_state.save_to_slot(slot_num)
                    self.show_message(f"Сохранено в слот {slot_num}!", arcade.color.GREEN)
                    return

        back_width = len(self.back_text.text) * 18
        back_left = cx - back_width // 2 - 20
        back_right = cx + back_width // 2 + 20
        back_top = 100
        back_bottom = 60

        if back_left <= x <= back_right and back_bottom <= y <= back_top:
            self.window.show_view(MainMenuScreen())

    def show_message(self, text, color):
        self.message = arcade.Text(text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150,
                                   color, 24, anchor_x="center")
        self.message_timer = 3.0


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
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen())


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
                    self.window.show_view(Screen1())
                elif i == 1:
                    self.window.show_view(SaveSelectScreen("load"))
                elif i == 2:
                    self.window.show_view(SaveSelectScreen("save"))
                elif i == 3:
                    self.window.close()
                break

    def on_key_press(self, key, _):
        if key == arcade.key.ENTER:
            game_state.balance = 1000
            game_state.current_bet = 100
            game_state.unlocked_screens = [1]
            game_state.current_screen = 1
            self.window.show_view(Screen1())
        elif key == arcade.key.ESCAPE:
            self.window.close()


class BaseScreen(arcade.View):
    COLORS = [None, arcade.color.GREEN, arcade.color.BLUE, arcade.color.YELLOW]
    UNLOCK_COSTS = {1: 5000, 2: 25000, 3: 100000}

    def __init__(self, screen_num):
        super().__init__()
        self.screen_num = screen_num
        game_state.current_screen = screen_num

        self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
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
                    self.window.show_view(BetScreen(True, "clicker"))
                elif self.screen_num == 2:
                    self.window.show_view(BetScreen(True, "slots"))
                elif self.screen_num == 3:
                    self.window.show_view(BetScreen(True, "fortune"))
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
            self.window.show_view(MainMenuScreen())

    def perform_exit(self):
        if self.exit_side == "right":
            if self.screen_num == 1:
                next_cls = Screen2
                next_screen_num = 2
            elif self.screen_num == 2:
                next_cls = Screen3
                next_screen_num = 3
            elif self.screen_num == 3:
                next_cls = CutsceneScreen
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
                    target = Screen1()
                elif self.game_type == "slots":
                    target = Screen2()
                elif self.game_type == "fortune":
                    target = Screen3()
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
                game_state.balance -= bet
                if self.game_type == "clicker":
                    self.window.show_view(ClickerGameScreen())
                elif self.game_type == "slots":
                    self.window.show_view(AnimationScreen())
                elif self.game_type == "fortune":
                    self.window.show_view(FortuneWheelScreen())
                return
        except ValueError:
            msg = "Введите корректное число"

        self.message = arcade.Text(msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 210,
                                   arcade.color.RED, 20, anchor_x="center")
        self.message_timer = 3.0

    def on_key_press(self, key, _):
        global target
        if key == arcade.key.ENTER:
            self.start_game()
        elif key == arcade.key.ESCAPE:
            if self.show_back:
                if self.game_type == "clicker":
                    target = Screen1()
                elif self.game_type == "slots":
                    target = Screen2()
                elif self.game_type == "fortune":
                    target = Screen3()
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
        self.balance.text = f"Баланс: {game_state.balance:,}"
        self.balance.draw()
        self.text.draw()

    def on_update(self, _):
        if time.time() - self.start_time >= self.duration:
            self.window.show_view(NumbersScreen())


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
            self.result_amount.text = f"+{game_state.current_bet * 2:,}"
            self.result_amount.color = arcade.color.GOLD
        elif self.ai_ball_top.center_x >= self.finish_line or self.ai_ball_bottom.center_x >= self.finish_line:
            self.game_over = True
            self.result_title.text, self.result_title.color = "ПРОИГРЫШ", arcade.color.RED
            self.result_amount.text = f"-{game_state.current_bet:,}"
            self.result_amount.color = arcade.color.RED

    def on_key_press(self, key, _):
        if self.game_over:
            self.window.show_view(BetScreen(True, "clicker"))


class CutsceneScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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
            self.window.show_view(Screen1())
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen())


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
            self.window.show_view(BetScreen(True, "fortune"))
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
            self.window.show_view(Screen3())
        elif key == arcade.key.B:
            self.window.show_view(BetScreen(True, "fortune"))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MainMenuScreen())


class GameState:
    def __init__(self):
        self.balance = 1000
        self.current_bet = 100
        self.selected_game = None
        self.unlocked_screens = [1]
        self.current_screen = 1

    def save_to_slot(self, slot_num):
        os.makedirs(SAVE_DIR, exist_ok=True)
        path = os.path.join(SAVE_DIR, f"slot{slot_num}.json")
        data = {
            "balance": self.balance,
            "current_bet": self.current_bet,
            "unlocked_screens": self.unlocked_screens,
            "current_screen": self.current_screen
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_slot(self, slot_num):
        path = os.path.join(SAVE_DIR, f"slot{slot_num}.json")
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.balance = data["balance"]
            self.current_bet = data["current_bet"]
            self.unlocked_screens = data["unlocked_screens"]
            self.current_screen = data["current_screen"]
            return True
        except Exception:
            return False

    def unlock_screen(self, screen_num, cost):
        if screen_num in self.unlocked_screens:
            return True
        if self.balance >= cost:
            self.balance -= cost
            if screen_num not in self.unlocked_screens:
                self.unlocked_screens.append(screen_num)
            return True
        return False

game_state = GameState()


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "казино ларисы долиной")
        self.show_view(MainMenuScreen())

    def on_close(self):
        super().on_close()


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()