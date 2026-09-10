import pygame

from config import BOTS_DATA, CARD_BORDER, CYAN, GOLD, GREEN, MUTED_COLOR, TEXT_COLOR, UPGRADES_DATA
from ui import draw_cyber_card, draw_cyber_icon, format_num, render_wrapped_text


class CyberScrollMenu:
    """Widget scrollable pour l'onglet BOTS (production automatique de crédits)."""

    def __init__(self):
        self.scroll_y = 0
        self.max_scroll = 0
        self.item_height = 125
        self.spacing = 10
        self.content_height = len(BOTS_DATA) * (self.item_height + self.spacing)

    def handle_wheel(self, event, rect):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 35
            self.clamp_scroll(rect)

    def clamp_scroll(self, rect):
        max_limit = self.content_height - rect.height + 10
        self.max_scroll = max(0, max_limit)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _buy_button_rect(self, card_w, card_y):
        btn_w = int(card_w * 0.22)
        return pygame.Rect(card_w - btn_w - 5, card_y + 80, btn_w, 40)

    def get_click_action(self, mouse_pos, rect, game):
        """Retourne ('buy', bot, cout), ('open_modal', bot, None) ou None."""
        if not rect.collidepoint(mouse_pos):
            return None

        rel_x = mouse_pos[0] - rect.x
        rel_y = mouse_pos[1] - rect.y + self.scroll_y
        card_w = rect.width - 15

        for i, b in enumerate(BOTS_DATA):
            card_y = i * (self.item_height + self.spacing)
            card_rect = pygame.Rect(5, card_y, card_w, self.item_height)
            if not card_rect.collidepoint(rel_x, rel_y):
                continue

            btn_buy = self._buy_button_rect(card_w, card_y)
            if btn_buy.collidepoint(rel_x, rel_y):
                cost = int(b["cost"] * (1.15 ** game.bots.get(b["id"], 0)))
                return ("buy", b, cost)
            return ("open_modal", b, None)
        return None

    def draw(self, surface, rect, mouse_pos, game, fonts):
        list_w = rect.width - 15
        content_surface = pygame.Surface(
            (list_w, max(self.content_height, rect.height)), pygame.SRCALPHA
        )
        rel_mouse = (mouse_pos[0] - rect.x, mouse_pos[1] - rect.y + self.scroll_y)
        card_w = list_w - 15
        now = pygame.time.get_ticks() / 1000.0

        for i, b in enumerate(BOTS_DATA):
            card_y = i * (self.item_height + self.spacing)
            if card_y - self.scroll_y > rect.height or card_y + self.item_height - self.scroll_y < 0:
                continue

            item_rect = pygame.Rect(5, card_y, card_w, self.item_height)
            is_hov = item_rect.collidepoint(rel_mouse)
            count = game.bots.get(b["id"], 0)
            cost = int(b["cost"] * (1.15 ** count))
            can_afford = game.money >= cost

            draw_cyber_card(
                content_surface, item_rect, b["color"] if is_hov else CARD_BORDER,
                is_hovered=is_hov, bg_color=(14, 18, 32, 210),
            )
            draw_cyber_icon(content_surface, b["icon"], item_rect.x + 10, item_rect.y + 25, b["color"], now)

            txt_title = fonts["med"].render(f"{b['name']}  [x{count}]", True, TEXT_COLOR)
            content_surface.blit(txt_title, (item_rect.x + 80, item_rect.y + 10))

            render_wrapped_text(
                content_surface, f"PROD: +{format_num(b['cps'])} EC/s", fonts["small"], GOLD,
                pygame.Rect(item_rect.x + 80, item_rect.y + 32, card_w - 90, 20),
            )
            render_wrapped_text(
                content_surface, b["desc"], fonts["small"], MUTED_COLOR,
                pygame.Rect(item_rect.x + 80, item_rect.y + 54, card_w - 90, 65),
            )

            btn_buy = self._buy_button_rect(card_w, card_y)
            btn_hov = btn_buy.collidepoint(rel_mouse)
            draw_cyber_card(
                content_surface, btn_buy, b["color"] if can_afford else CARD_BORDER,
                is_hovered=btn_hov,
                bg_color=(25, 35, 60, 200) if btn_hov and can_afford else (15, 20, 35, 170),
            )
            p_color = GOLD if can_afford else MUTED_COLOR
            txt_p = fonts["small"].render("ACHETER", True, p_color)
            txt_val = fonts["small"].render(f"{format_num(cost)} EC", True, p_color)
            content_surface.blit(txt_p, (btn_buy.x + (btn_buy.width - txt_p.get_width()) // 2, btn_buy.y + 6))
            content_surface.blit(txt_val, (btn_buy.x + (btn_buy.width - txt_val.get_width()) // 2, btn_buy.y + 20))

        surface.blit(content_surface, (rect.x, rect.y), (0, self.scroll_y, rect.width, rect.height))

        if self.max_scroll > 0:
            bar_h = max(30, int(rect.height * (rect.height / self.content_height)))
            bar_y = rect.y + int((self.scroll_y / self.max_scroll) * (rect.height - bar_h))
            pygame.draw.rect(surface, (30, 40, 70), (rect.right - 8, rect.y, 5, rect.height))
            pygame.draw.rect(surface, CYAN, (rect.right - 8, bar_y, 5, bar_h))


class CyberUpgradesMenu:
    """Widget scrollable pour l'onglet AMÉLIO (améliorations de puissance de clic)."""

    def __init__(self):
        self.scroll_y = 0
        self.max_scroll = 0
        self.item_height = 125
        self.spacing = 10
        self.content_height = len(UPGRADES_DATA) * (self.item_height + self.spacing)

    def handle_wheel(self, event, rect):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 35
            self.clamp_scroll(rect)

    def clamp_scroll(self, rect):
        max_limit = self.content_height - rect.height + 10
        self.max_scroll = max(0, max_limit)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _buy_button_rect(self, card_w, card_y):
        btn_w = int(card_w * 0.22)
        return pygame.Rect(card_w - btn_w - 5, card_y + 80, btn_w, 40)

    def get_click_action(self, mouse_pos, rect, game):
        """Retourne ('buy', upgrade, cout), ('open_modal', upgrade, None) ou None."""
        if not rect.collidepoint(mouse_pos):
            return None

        rel_x = mouse_pos[0] - rect.x
        rel_y = mouse_pos[1] - rect.y + self.scroll_y
        card_w = rect.width - 15

        for i, u in enumerate(UPGRADES_DATA):
            card_y = i * (self.item_height + self.spacing)
            card_rect = pygame.Rect(5, card_y, card_w, self.item_height)
            if not card_rect.collidepoint(rel_x, rel_y):
                continue

            btn_buy = self._buy_button_rect(card_w, card_y)
            if btn_buy.collidepoint(rel_x, rel_y):
                return ("buy", u, u["cost"])
            return ("open_modal", u, None)
        return None

    def draw(self, surface, rect, mouse_pos, game, fonts):
        list_w = rect.width - 15
        content_surface = pygame.Surface(
            (list_w, max(self.content_height, rect.height)), pygame.SRCALPHA
        )
        rel_mouse = (mouse_pos[0] - rect.x, mouse_pos[1] - rect.y + self.scroll_y)
        card_w = list_w - 15
        now = pygame.time.get_ticks() / 1000.0

        for i, u in enumerate(UPGRADES_DATA):
            card_y = i * (self.item_height + self.spacing)
            if card_y - self.scroll_y > rect.height or card_y + self.item_height - self.scroll_y < 0:
                continue

            item_rect = pygame.Rect(5, card_y, card_w, self.item_height)
            is_hov = item_rect.collidepoint(rel_mouse)
            bought = game.upgrades.get(u["id"], False)
            can_afford = game.money >= u["cost"] and not bought

            draw_cyber_card(
                content_surface, item_rect,
                GREEN if bought else (GOLD if is_hov else CARD_BORDER),
                is_hovered=is_hov, bg_color=(14, 18, 32, 210),
            )
            draw_cyber_icon(content_surface, u["icon"], item_rect.x + 10, item_rect.y + 25, GOLD, now)

            txt_title = fonts["med"].render(u["name"], True, TEXT_COLOR)
            content_surface.blit(txt_title, (item_rect.x + 80, item_rect.y + 10))

            render_wrapped_text(
                content_surface, f"COÛT: {format_num(u['cost'])} EC", fonts["small"], GOLD,
                pygame.Rect(item_rect.x + 80, item_rect.y + 32, card_w - 90, 20),
            )
            render_wrapped_text(
                content_surface, u["desc"], fonts["small"], MUTED_COLOR,
                pygame.Rect(item_rect.x + 80, item_rect.y + 54, card_w - 90, 65),
            )

            btn_buy = self._buy_button_rect(card_w, card_y)
            btn_hov = btn_buy.collidepoint(rel_mouse)
            draw_cyber_card(
                content_surface, btn_buy,
                GREEN if bought else (GOLD if can_afford else CARD_BORDER),
                is_hovered=btn_hov,
                bg_color=(25, 35, 60, 200) if btn_hov and can_afford else (15, 20, 35, 170),
            )

            if bought:
                txt_st = fonts["small"].render("ACQUIS", True, GREEN)
                content_surface.blit(txt_st, (btn_buy.x + (btn_buy.width - txt_st.get_width()) // 2, btn_buy.y + 12))
            else:
                p_color = GOLD if can_afford else MUTED_COLOR
                txt_p = fonts["small"].render("ACHETER", True, p_color)
                txt_val = fonts["small"].render(f"{format_num(u['cost'])} EC", True, p_color)
                content_surface.blit(txt_p, (btn_buy.x + (btn_buy.width - txt_p.get_width()) // 2, btn_buy.y + 6))
                content_surface.blit(txt_val, (btn_buy.x + (btn_buy.width - txt_val.get_width()) // 2, btn_buy.y + 20))

        surface.blit(content_surface, (rect.x, rect.y), (0, self.scroll_y, rect.width, rect.height))

        if self.max_scroll > 0:
            bar_h = max(30, int(rect.height * (rect.height / self.content_height)))
            bar_y = rect.y + int((self.scroll_y / self.max_scroll) * (rect.height - bar_h))
            pygame.draw.rect(surface, (30, 40, 70), (rect.right - 8, rect.y, 5, rect.height))
            pygame.draw.rect(surface, CYAN, (rect.right - 8, bar_y, 5, bar_h))
