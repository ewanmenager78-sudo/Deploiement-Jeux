import pygame

from config import BOTS_DATA, ITEMS_DATA, STORY_CHAPTERS, UPGRADES_DATA
from ui import format_num


class GameState:
    """État complet de la partie en cours : monnaie, bots, améliorations,
    objets, histoire débloquée et progression de l'autoclick."""

    def __init__(self):
        self.money = 0.0
        self.total_money_earned = 0.0
        self.click_power = 1.0

        self.bots = {b["id"]: 0 for b in BOTS_DATA}
        self.upgrades = {u["id"]: False for u in UPGRADES_DATA}
        self.items = {it["id"]: False for it in ITEMS_DATA}

        self.unlocked_story = set()
        self.notifications = []

        self.active_tab = "bots"
        self.scroll_offsets = {"bots": 0, "upgrades": 0, "items": 0, "story": 0}

        self.relic_clicks = 0
        self.current_slot = 1

        self.autoclick_enabled = False
        self.autoclick_level = 0
        self.last_autoclick_time = 0

        self.controls = {
            "Pause / Menu": pygame.K_e,
            "Toggle Autoclick": pygame.K_a,
        }

        self.check_story_unlocks()

    def reset(self):
        self.__init__()

    def get_autoclick_cost(self):
        return int(500 * (3.8 ** self.autoclick_level))

    def get_autoclick_interval(self):
        return max(30, int(1000 / (1 + self.autoclick_level * 0.75)))

    def get_cps(self):
        base_cps = sum(self.bots.get(b["id"], 0) * b["cps"] for b in BOTS_DATA)
        mult = 1.0
        if self.upgrades.get("reactor", False):
            mult *= 1.5
        if self.upgrades.get("synapse_link", False):
            mult *= 2.0
        if self.items.get("sun", False):
            mult += 0.25
        if self.items.get("neural_deck", False):
            mult += 0.30
        if self.items.get("ai_fragment", False):
            mult *= 2.5
        return base_cps * mult

    def get_click_power(self):
        cp = self.click_power
        if self.upgrades.get("finger", False):
            cp += 2
        if self.upgrades.get("overclock", False):
            cp += 5
        if self.upgrades.get("nanites", False):
            cp += 50
        if self.upgrades.get("hyper_thread", False):
            cp += 500
        if self.items.get("ticket", False):
            cp += 1
        if self.items.get("relic_core", False):
            cp += 20
        if self.items.get("neural_deck", False):
            cp += 150
        return cp

    def add_money(self, amount):
        self.money += amount
        self.total_money_earned += amount
        self.check_story_unlocks()

    def check_story_unlocks(self):
        for req, line, item_id in STORY_CHAPTERS:
            if req not in self.unlocked_story and self.total_money_earned >= req:
                self.unlocked_story.add(req)
                self.add_notification(
                    "ARCHIVE DÉCRYPTÉE",
                    f"Nouvel enregistrement de David Martinez [{format_num(req)} EC]",
                )

    def add_notification(self, title, text):
        self.notifications.append({
            "title": title,
            "text": text,
            "time": pygame.time.get_ticks(),
        })
