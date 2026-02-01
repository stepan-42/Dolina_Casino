import json
import os

SAVE_DIR = "saves"


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