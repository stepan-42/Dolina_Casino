import arcade
import os
import json
import time

import CutsceneScreen
from GameState import game_state
import BareScreen
import MainMenuScreen

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_SIZE, RECT_WIDTH, RECT_HEIGHT = 40, 200, 100
MOVEMENT_SPEED = 5
SAVE_DIR = "saves"


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
                                view = BareScreen.Screen1()
                            elif game_state.current_screen == 2:
                                view = BareScreen.Screen2()
                            elif game_state.current_screen == 3:
                                view = BareScreen.Screen3()
                            else:
                                view = CutsceneScreen.CutsceneScreen()
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
            self.window.show_view(MainMenuScreen.MainMenuScreen())

    def show_message(self, text, color):
        self.message = arcade.Text(text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150,
                                   color, 24, anchor_x="center")
        self.message_timer = 3.0