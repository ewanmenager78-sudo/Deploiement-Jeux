import math
import os
import random
import sys
import pygame

from config import (
    CARD_BG,
    CARD_BORDER,
    CYAN,
    GOLD,
    GREEN,
    ITEMS_DATA,
    MUTED_COLOR,
    PANEL_BG,
    PANEL_BORDER,
    PINK,
    RED,
    RESOLUTIONS_LIST,
    STORY_CHAPTERS,
    TEXT_COLOR,
    get_fonts,
)
from background import CyberpunkCityBackground
from game_state import GameState
from save_system import delete_save, get_slot_info, load_game, save_game
from ui import (
    draw_cyber_card,
    draw_cyber_icon,
    draw_notifications,
    format_num,
    render_wrapped_text,
)
from upgrades_menu import CyberScrollMenu, CyberUpgradesMenu


def apply_display_mode(res_size, fullscreen):
    pygame.display.quit()
    pygame.display.init()
    
    if fullscreen:
        return pygame.display.set_mode(res_size, pygame.FULLSCREEN)
    else:
        return pygame.display.set_mode(res_size, pygame.RESIZABLE)


def main():
    pygame.init()
    pygame.font.init()

    res_index = 0
    info = pygame.display.Info()
    for idx, res in enumerate(RESOLUTIONS_LIST):
        if res[0] <= info.current_w and res[1] <= info.current_h:
            res_index = idx

    FPS_LIST = [1, 30, 60, 120, 144, 165]
    fps_index = 2

    is_paused = True
    menu_state = "main"
    resolution_dropdown_open = False  
    active_modal = None
    confirmation_modal = None
    waiting_for_key_action = None

    is_fullscreen = True

    screen = apply_display_mode(RESOLUTIONS_LIST[res_index], fullscreen=is_fullscreen)
    pygame.display.set_caption("CYBER-CLICKER // NIGHT CITY NATIVE")

    game = GameState()

    W, H = screen.get_size()
    fonts = get_fonts(H)
    bg_animation = CyberpunkCityBackground(W, H)

    bots_menu = CyberScrollMenu()
    upgrades_menu_widget = CyberUpgradesMenu()

    clock = pygame.time.Clock()
    relic_scale = 1.0

    click_particles = []
    floating_texts = []

    AUTO_SAVE_INTERVAL = 180000  
    last_auto_save = pygame.time.get_ticks()

    running = True
    while running:
        raw_dt = clock.tick(FPS_LIST[fps_index]) / 1000.0
        dt = min(raw_dt, 0.1)
        now = pygame.time.get_ticks()

        W, H = screen.get_size()
        relic_center = (int(W * 0.22), int(H * 0.53))
        relic_radius = int(H * 0.14)
        list_clip_rect = pygame.Rect(
            int(W * 0.54), int(H * 0.11), int(W * 0.43), int(H * 0.85)
        )

        if now - last_auto_save > AUTO_SAVE_INTERVAL:
            save_game(game)
            game.add_notification("AUTO-SAVE", f"Slot {game.current_slot} sauvegardé.")
            last_auto_save = now

        if not is_paused and not active_modal and not confirmation_modal:
            cps = game.get_cps()
            if cps > 0:
                game.add_money(cps * dt)

            if game.autoclick_enabled and game.autoclick_level > 0:
                interval = game.get_autoclick_interval()
                if now - game.last_autoclick_time >= interval:
                    game.last_autoclick_time = now
                    power = game.get_click_power()
                    game.add_money(power)
                    game.relic_clicks += 1
                    relic_scale = 1.08

                    ang = random.uniform(0, math.pi * 2)
                    click_particles.append({
                        "x": relic_center[0] + math.cos(ang) * (relic_radius * 0.4),
                        "y": relic_center[1] + math.sin(ang) * (relic_radius * 0.4),
                        "vx": math.cos(ang) * 120,
                        "vy": math.sin(ang) * 120,
                        "life": 0.3,
                        "color": CYAN if game.relic_clicks % 2 == 0 else PINK,
                    })

        game.notifications = [
            n for n in game.notifications if pygame.time.get_ticks() - n["time"] < 4000
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                confirmation_modal = ("quit", None)

            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    screen = pygame.display.set_mode(
                        (max(1024, event.w), max(576, event.h)), pygame.RESIZABLE
                    )
                    W, H = screen.get_size()
                    fonts = get_fonts(H)
                    bg_animation.resize(W, H)

            elif event.type == pygame.KEYDOWN:
                if waiting_for_key_action:
                    game.controls[waiting_for_key_action] = event.key
                    waiting_for_key_action = None
                    continue

                if event.key == game.controls.get("Pause / Menu", pygame.K_ESCAPE):
                    if confirmation_modal:
                        confirmation_modal = None
                    elif active_modal:
                        active_modal = None
                    elif resolution_dropdown_open:
                        resolution_dropdown_open = False
                    elif menu_state in ["saves", "settings", "controls"]:
                        menu_state = "main"
                    else:
                        is_paused = not is_paused

                elif event.key == game.controls.get("Toggle Autoclick", pygame.K_a):
                    if not is_paused and not active_modal and not confirmation_modal:
                        if game.autoclick_level > 0:
                            game.autoclick_enabled = not game.autoclick_enabled
                            state_str = "ACTIVÉ" if game.autoclick_enabled else "DÉSACTIVÉ"
                            game.add_notification("AUTOCLICK", f"Module {state_str}")
                        else:
                            game.add_notification("VERROUILLÉ", "Améliorez le module pour l'activer.")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos

                    if confirmation_modal:
                        c_rect = pygame.Rect(0, 0, W, H)
                        btn_w_mod = int(W * 0.22)
                        btn_h_mod = int(H * 0.08)
                        btn_yes = pygame.Rect(W // 2 - btn_w_mod - int(W * 0.03), c_rect.y + int(H * 0.55), btn_w_mod, btn_h_mod)
                        btn_no = pygame.Rect(W // 2 + int(W * 0.03), c_rect.y + int(H * 0.55), btn_w_mod, btn_h_mod)

                        if btn_yes.collidepoint((mx, my)):
                            action, data = confirmation_modal
                            if action == "quit":
                                save_game(game)
                                running = False
                            elif action == "restart":
                                game.reset()
                                is_paused = True
                                menu_state = "main"
                                confirmation_modal = None
                            elif action == "delete_save":
                                slot_to_del = data
                                if delete_save(slot_to_del):
                                    game.add_notification("SYSTÈME", f"Slot {slot_to_del} effacé.")
                                confirmation_modal = None
                        elif btn_no.collidepoint((mx, my)):
                            confirmation_modal = None
                        continue

                    if active_modal:
                        modal_w, modal_h = int(W * 0.5), int(H * 0.6)
                        modal_rect = pygame.Rect(
                            (W - modal_w) // 2, (H - modal_h) // 2, modal_w, modal_h
                        )
                        btn_close = pygame.Rect(
                            modal_rect.right - 40, modal_rect.y + 10, 30, 30
                        )

                        if btn_close.collidepoint((mx, my)) or not modal_rect.collidepoint((mx, my)):
                            active_modal = None
                        
                        if active_modal and active_modal[0] == "story":
                            req, text, item_id = active_modal[1]
                            if item_id:
                                btn_item = pygame.Rect(
                                    modal_rect.x + 30, modal_rect.bottom - 60, modal_rect.width - 60, 40
                                )
                                if btn_item.collidepoint((mx, my)):
                                    if not game.items.get(item_id, False):
                                        game.items[item_id] = True
                                        item_obj = next(it for it in ITEMS_DATA if it["id"] == item_id)
                                        game.add_notification(
                                            "RELIQUE RÉCUPÉRÉE",
                                            f"Vous avez réclamé : {item_obj['name']}",
                                        )
                        continue

                    if is_paused:
                        btn_w, btn_h = int(W * 0.25), int(H * 0.065)
                        cx = W // 2 - btn_w // 2

                        if menu_state == "main":
                            if pygame.Rect(
                                cx, int(H * 0.26), btn_w, btn_h
                            ).collidepoint((mx, my)):
                                is_paused = False
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075), btn_w, btn_h
                            ).collidepoint((mx, my)):
                                confirmation_modal = ("restart", None)
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075) * 2, btn_w, btn_h
                            ).collidepoint((mx, my)):
                                menu_state = "saves"
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075) * 3, btn_w, btn_h
                            ).collidepoint((mx, my)):
                                menu_state = "settings"
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075) * 4, btn_w, btn_h
                            ).collidepoint((mx, my)):
                                confirmation_modal = ("quit", None)

                        elif menu_state == "settings":
                            if resolution_dropdown_open:
                                res_btn_rect = pygame.Rect(cx, int(H * 0.26), btn_w, btn_h)
                                clicked_in_dropdown = False
                                for r_idx, res in enumerate(RESOLUTIONS_LIST):
                                    item_rect = pygame.Rect(cx, res_btn_rect.bottom + r_idx * btn_h, btn_w, btn_h)
                                    if item_rect.collidepoint((mx, my)):
                                        res_index = r_idx
                                        screen = apply_display_mode(RESOLUTIONS_LIST[res_index], fullscreen=is_fullscreen)
                                        W, H = screen.get_size()
                                        fonts = get_fonts(H)
                                        bg_animation.resize(W, H)
                                        resolution_dropdown_open = False
                                        clicked_in_dropdown = True
                                        break
                                if not clicked_in_dropdown and not res_btn_rect.collidepoint((mx, my)):
                                    resolution_dropdown_open = False
                                if clicked_in_dropdown:
                                    continue

                            if pygame.Rect(
                                cx, int(H * 0.26), btn_w, btn_h
                            ).collidepoint((mx, my)):
                                resolution_dropdown_open = not resolution_dropdown_open
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075), btn_w, btn_h
                            ).collidepoint((mx, my)):
                                is_fullscreen = not is_fullscreen
                                screen = apply_display_mode(RESOLUTIONS_LIST[res_index], fullscreen=is_fullscreen)
                                W, H = screen.get_size()
                                fonts = get_fonts(H)
                                bg_animation.resize(W, H)
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075) * 2, btn_w, btn_h
                            ).collidepoint((mx, my)):
                                fps_index = (fps_index + 1) % len(FPS_LIST)
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075) * 3, btn_w, btn_h
                            ).collidepoint((mx, my)):
                                menu_state = "controls"
                            elif pygame.Rect(
                                cx, int(H * 0.26) + int(H * 0.075) * 4, btn_w, btn_h
                            ).collidepoint((mx, my)):
                                menu_state = "main"

                        elif menu_state == "controls":
                            actions_list = list(game.controls.keys())
                            for idx, act in enumerate(actions_list):
                                b_rect = pygame.Rect(cx + int(btn_w * 0.6), int(H * 0.26) + idx * int(H * 0.08), int(btn_w * 0.4), btn_h)
                                if b_rect.collidepoint((mx, my)):
                                    waiting_for_key_action = act
                                    break
                            
                            btn_back_ctrl = pygame.Rect(cx, int(H * 0.75), btn_w, btn_h)
                            if btn_back_ctrl.collidepoint((mx, my)):
                                menu_state = "settings"

                        elif menu_state == "saves":
                            if pygame.Rect(
                                cx, int(H * 0.78), btn_w, btn_h
                            ).collidepoint((mx, my)):
                                menu_state = "main"

                            for slot in range(1, 4):
                                slot_y = int(H * 0.26) + (slot - 1) * int(H * 0.16)
                                btn_load = pygame.Rect(
                                    int(W * 0.5), slot_y + 35, int(W * 0.07), 35
                                )
                                btn_save = pygame.Rect(
                                    int(W * 0.58), slot_y + 35, int(W * 0.07), 35
                                )
                                btn_del = pygame.Rect(
                                    int(W * 0.66), slot_y + 35, 35, 35
                                )

                                if btn_load.collidepoint((mx, my)):
                                    if load_game(game, slot):
                                        game.add_notification(
                                            "SYSTÈME", f"Slot {slot} chargé."
                                        )
                                        is_paused = False
                                        menu_state = "main"
                                elif btn_save.collidepoint((mx, my)):
                                    save_game(game, slot)
                                    game.add_notification(
                                        "SYSTÈME", f"Sauvegardé sur Slot {slot}."
                                    )
                                elif btn_del.collidepoint((mx, my)):
                                    info = get_slot_info(slot)
                                    if info:
                                        confirmation_modal = ("delete_save", slot)
                        
                        continue

                    if pygame.Rect(
                        int(W * 0.02), int(H * 0.03), int(W * 0.08), int(H * 0.045)
                    ).collidepoint((mx, my)):
                        is_paused = True
                        menu_state = "main"

                    if pygame.Rect(
                        int(W * 0.11), int(H * 0.03), int(W * 0.13), int(H * 0.045)
                    ).collidepoint((mx, my)):
                        if game.autoclick_level > 0:
                            game.autoclick_enabled = not game.autoclick_enabled
                        else:
                            game.add_notification(
                                "VERROUILLÉ", "Améliorez le module pour l'activer."
                            )

                    if pygame.Rect(
                        int(W * 0.25), int(H * 0.03), int(W * 0.15), int(H * 0.045)
                    ).collidepoint((mx, my)):
                        cost = game.get_autoclick_cost()
                        if game.money >= cost:
                            game.money -= cost
                            game.autoclick_level += 1
                            game.autoclick_enabled = True

                    if (
                        math.hypot(mx - relic_center[0], my - relic_center[1])
                        <= relic_radius
                    ):
                        power = game.get_click_power()
                        game.add_money(power)
                        game.relic_clicks += 1
                        relic_scale = 1.15

                        for _ in range(10):
                            ang = random.uniform(0, math.pi * 2)
                            click_particles.append({
                                "x": mx,
                                "y": my,
                                "vx": math.cos(ang) * random.randint(100, 220),
                                "vy": math.sin(ang) * random.randint(100, 220),
                                "life": 0.45,
                                "color": CYAN if game.relic_clicks % 2 == 0 else PINK,
                            })

                        floating_texts.append({
                            "x": mx,
                            "y": my - 15,
                            "text": f"+{format_num(power)}",
                            "life": 0.8,
                            "color": GOLD,
                        })

                    tabs = [
                        ("bots", "BOTS"),
                        ("upgrades", "AMÉLIO"),
                        ("items", "OBJETS"),
                        ("story", "HISTOIRE"),
                    ]
                    for i, (tab_id, _) in enumerate(tabs):
                        t_rect = pygame.Rect(
                            int(W * 0.54) + i * int(W * 0.105),
                            int(H * 0.03),
                            int(W * 0.10),
                            int(H * 0.055),
                        )
                        if t_rect.collidepoint((mx, my)):
                            game.active_tab = tab_id

                    if game.active_tab == "bots":
                        action = bots_menu.get_click_action(
                            (mx, my), list_clip_rect, game
                        )
                        if action:
                            kind, b, cost = action
                            if kind == "buy":
                                if game.money >= cost:
                                    game.money -= cost
                                    game.bots[b["id"]] = game.bots.get(b["id"], 0) + 1
                            elif kind == "open_modal":
                                active_modal = ("bot", b)

                    elif game.active_tab == "upgrades":
                        action = upgrades_menu_widget.get_click_action(
                            (mx, my), list_clip_rect, game
                        )
                        if action:
                            kind, u, cost = action
                            if kind == "buy":
                                if not game.upgrades.get(u["id"], False) and game.money >= cost:
                                    game.money -= cost
                                    game.upgrades[u["id"]] = True
                            elif kind == "open_modal":
                                active_modal = ("upgrade", u)

                    elif list_clip_rect.collidepoint((mx, my)):
                        rel_y = (
                            my - list_clip_rect.y + game.scroll_offsets[game.active_tab]
                        )
                        card_w = list_clip_rect.width - 15

                        if game.active_tab == "items":
                            for i, it in enumerate(ITEMS_DATA):
                                card_y = i * 135
                                card_rect = pygame.Rect(5, card_y, card_w, 125)
                                btn_buy = pygame.Rect(
                                    card_w - int(W * 0.1),
                                    card_y + 80,
                                    int(W * 0.095),
                                    40,
                                )
                                if btn_buy.collidepoint((mx - list_clip_rect.x, rel_y)):
                                    if not game.items.get(it["id"], False):
                                        game.add_notification(
                                            "VERROUILLÉ",
                                            "Lisez le chapitre d'histoire pour débloquer cet objet !",
                                        )
                                elif card_rect.collidepoint((mx - list_clip_rect.x, rel_y)):
                                    active_modal = ("item", it)

                        elif game.active_tab == "story":
                            for i, (req, text, item_id) in enumerate(STORY_CHAPTERS):
                                if req in game.unlocked_story:
                                    card_y = i * 155
                                    card_rect = pygame.Rect(5, card_y, card_w, 145)
                                    if card_rect.collidepoint((mx - list_clip_rect.x, rel_y)):
                                        active_modal = ("story", (req, text, item_id))

            elif event.type == pygame.MOUSEWHEEL and not is_paused:
                if pygame.mouse.get_pos()[0] > W * 0.5:
                    if game.active_tab == "bots":
                        bots_menu.handle_wheel(event, list_clip_rect)
                    elif game.active_tab == "upgrades":
                        upgrades_menu_widget.handle_wheel(event, list_clip_rect)
                    else:
                        game.scroll_offsets[game.active_tab] = max(
                            0, game.scroll_offsets[game.active_tab] - event.y * 35
                        )

        relic_scale += (1.0 - relic_scale) * 12 * dt

        for p in click_particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                click_particles.remove(p)

        for ft in floating_texts[:]:
            ft["y"] -= 45 * dt
            ft["life"] -= dt
            if ft["life"] <= 0:
                floating_texts.remove(ft)

        bg_animation.update_and_draw(screen, dt, now, fonts)
        mouse_pos = pygame.mouse.get_pos()

        pulse = math.sin(now * 0.005) * 6
        current_r = int((relic_radius * relic_scale) + pulse)
        
        ring_angle = now * 0.001
        pygame.draw.circle(screen, (20, 40, 60), relic_center, current_r + 18, 1)
        
        arc_rect = pygame.Rect(relic_center[0] - (current_r + 28), relic_center[1] - (current_r + 28), (current_r + 28) * 2, (current_r + 28) * 2)
        
        rgb_hue = (now * 0.2) % 360
        rgb_color_1 = pygame.Color(0)
        rgb_color_1.hsva = (rgb_hue % 360, 100, 100, 100)
        rgb_color_2 = pygame.Color(0)
        rgb_color_2.hsva = ((rgb_hue + 180) % 360, 100, 100, 100)

        pygame.draw.arc(screen, rgb_color_1, arc_rect, ring_angle, ring_angle + 1.5, 2)
        pygame.draw.arc(screen, rgb_color_2, arc_rect, ring_angle + 3.14, ring_angle + 4.64, 2)

        main_color = PINK if game.relic_clicks % 2 == 0 else CYAN
        pygame.draw.circle(screen, (10, 14, 26), relic_center, current_r)
        pygame.draw.circle(screen, rgb_color_1, relic_center, current_r, 3)
        pygame.draw.circle(screen, (30, 40, 60), relic_center, int(current_r * 0.75), 1)

        bar_count = 5
        bar_width = 6
        total_w = bar_count * bar_width + (bar_count - 1) * 3
        start_x = relic_center[0] - total_w // 2
        for i in range(bar_count):
            h_factor = abs(math.sin(now * 0.008 + i * 1.2))
            bar_h = int(12 + h_factor * 18)
            bar_rect = pygame.Rect(
                start_x + i * (bar_width + 3),
                relic_center[1] - bar_h // 2 - 6,
                bar_width,
                bar_h
            )
            pygame.draw.rect(screen, rgb_color_2 if i % 2 == 0 else main_color, bar_rect, border_radius=2)

        txt_sub_relic = fonts["small"].render("CLIQUER", True, TEXT_COLOR)
        screen.blit(
            txt_sub_relic,
            (
                relic_center[0] - txt_sub_relic.get_width() // 2,
                relic_center[1] + 16,
            ),
        )

        for p in click_particles:
            alpha = max(0, int((p["life"] / 0.45) * 255))
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], alpha), (3, 3), 3)
            screen.blit(s, (p["x"] - 3, p["y"] - 3))

        for ft in floating_texts:
            txt_s = fonts["title"].render(ft["text"], True, ft["color"])
            screen.blit(txt_s, (ft["x"] - txt_s.get_width() // 2, ft["y"]))

        btn_menu = pygame.Rect(
            int(W * 0.02), int(H * 0.03), int(W * 0.08), int(H * 0.045)
        )
        draw_cyber_card(
            screen,
            btn_menu,
            CYAN,
            is_hovered=btn_menu.collidepoint(mouse_pos),
            bg_color=(20, 30, 50, 180),
        )
        txt_m = fonts["small"].render("[ MENU ]", True, CYAN)
        screen.blit(
            txt_m,
            (
                btn_menu.x + (btn_menu.width - txt_m.get_width()) // 2,
                btn_menu.y + 7,
            ),
        )

        btn_autoclick = pygame.Rect(
            int(W * 0.11), int(H * 0.03), int(W * 0.13), int(H * 0.045)
        )
        ac_color = GREEN if game.autoclick_enabled else RED
        draw_cyber_card(
            screen,
            btn_autoclick,
            ac_color,
            is_hovered=btn_autoclick.collidepoint(mouse_pos),
            bg_color=(20, 30, 50, 180),
        )
        ac_label = f"AUTO: Nv.{game.autoclick_level} [{'ON' if game.autoclick_enabled else 'OFF'}]"
        txt_ac = fonts["small"].render(ac_label, True, ac_color)
        screen.blit(
            txt_ac,
            (
                btn_autoclick.x + (btn_autoclick.width - txt_ac.get_width()) // 2,
                btn_autoclick.y + 7,
            ),
        )

        btn_upg_auto = pygame.Rect(
            int(W * 0.25), int(H * 0.03), int(W * 0.15), int(H * 0.045)
        )
        auto_cost = game.get_autoclick_cost()
        can_afford_auto = game.money >= auto_cost
        draw_cyber_card(
            screen,
            btn_upg_auto,
            GOLD if can_afford_auto else CARD_BORDER,
            is_hovered=btn_upg_auto.collidepoint(mouse_pos),
            bg_color=(20, 30, 50, 180),
        )
        txt_upg_a = fonts["small"].render(
            f"UP: {format_num(auto_cost)} EC",
            True,
            GOLD if can_afford_auto else MUTED_COLOR,
        )
        screen.blit(
            txt_upg_a,
            (
                btn_upg_auto.x + (btn_upg_auto.width - txt_upg_a.get_width()) // 2,
                btn_upg_auto.y + 7,
            ),
        )

        txt_ec = fonts["large"].render(f"{format_num(game.money)} EC", True, CYAN)
        txt_cps = fonts["med"].render(
            f"PRODUCTION: {format_num(game.get_cps())} EC/s", True, GOLD
        )
        txt_cp = fonts["small"].render(
            f"PUISSANCE DE CLIC: +{format_num(game.get_click_power())}",
            True,
            TEXT_COLOR,
        )

        screen.blit(txt_ec, (int(W * 0.03), int(H * 0.11)))
        screen.blit(txt_cps, (int(W * 0.03), int(H * 0.17)))
        screen.blit(txt_cp, (int(W * 0.03), int(H * 0.21)))

        tabs = [
            ("bots", "BOTS"),
            ("upgrades", "AMÉLIO"),
            ("items", "OBJETS"),
            ("story", "HISTOIRE"),
        ]
        for i, (tab_id, label) in enumerate(tabs):
            t_rect = pygame.Rect(
                int(W * 0.54) + i * int(W * 0.105),
                int(H * 0.03),
                int(W * 0.10),
                int(H * 0.055),
            )
            is_active = game.active_tab == tab_id
            is_hov = t_rect.collidepoint(mouse_pos)

            draw_cyber_card(
                screen,
                t_rect,
                CYAN if is_active else (PANEL_BORDER if is_hov else CARD_BORDER),
                is_hovered=is_hov,
                bg_color=(25, 35, 60, 180) if is_active else (14, 18, 30, 130),
            )
            txt_t = fonts["med"].render(
                label, True, CYAN if is_active else MUTED_COLOR
            )
            screen.blit(
                txt_t,
                (t_rect.x + (t_rect.width - txt_t.get_width()) // 2, t_rect.y + 12),
            )

        if game.active_tab == "bots":
            bots_menu.draw(screen, list_clip_rect, mouse_pos, game, fonts)

        elif game.active_tab == "upgrades":
            upgrades_menu_widget.draw(screen, list_clip_rect, mouse_pos, game, fonts)

        else:
            list_surface = pygame.Surface(
                (list_clip_rect.width, list_clip_rect.height), pygame.SRCALPHA
            )
            offset = game.scroll_offsets.get(game.active_tab, 0)
            card_w = list_clip_rect.width - 15

            if game.active_tab == "items":
                for i, it in enumerate(ITEMS_DATA):
                    y = i * 135 - offset
                    if -120 <= y <= list_clip_rect.height:
                        item_rect = pygame.Rect(5, y, card_w, 125)
                        rel_mouse = (
                            mouse_pos[0] - list_clip_rect.x,
                            mouse_pos[1] - list_clip_rect.y,
                        )
                        is_hov = item_rect.collidepoint(rel_mouse)
                        bought = game.items.get(it["id"], False)

                        draw_cyber_card(
                            list_surface,
                            item_rect,
                            GREEN if bought else (PINK if is_hov else CARD_BORDER),
                            is_hovered=is_hov,
                            bg_color=(14, 18, 32, 160),
                        )
                        draw_cyber_icon(
                            list_surface,
                            it["icon"],
                            item_rect.x + 10,
                            item_rect.y + 25,
                            PINK,
                            now / 1000.0,
                        )

                        txt_title = fonts["med"].render(
                            f"{it['name']}", True, TEXT_COLOR
                        )
                        list_surface.blit(
                            txt_title, (item_rect.x + 80, item_rect.y + 10)
                        )

                        render_wrapped_text(
                            list_surface,
                            f"BONUS: {it['perf']}",
                            fonts["small"],
                            GOLD,
                            pygame.Rect(item_rect.x + 80, item_rect.y + 32, card_w - 90, 20),
                        )
                        render_wrapped_text(
                            list_surface,
                            it["desc"],
                            fonts["small"],
                            MUTED_COLOR,
                            pygame.Rect(item_rect.x + 80, item_rect.y + 54, card_w - 90, 65),
                        )

                        status_txt = "ÉQUIPÉ (DÉBLOQUÉ DANS L'HISTOIRE)" if bought else "VERROUILLÉ (LIRE L'HISTOIRE)"
                        txt_st = fonts["small"].render(
                            status_txt, True, GREEN if bought else RED
                        )
                        list_surface.blit(txt_st, (item_rect.x + 80, item_rect.y + 102))

            elif game.active_tab == "story":
                for i, (req, text, item_id) in enumerate(STORY_CHAPTERS):
                    y = i * 155 - offset
                    if -140 <= y <= list_clip_rect.height:
                        item_rect = pygame.Rect(5, y, card_w, 145)
                        unlocked = req in game.unlocked_story

                        draw_cyber_card(
                            list_surface,
                            item_rect,
                            CYAN if unlocked else CARD_BORDER,
                            is_hovered=False,
                            bg_color=(14, 18, 32, 160),
                        )

                        txt_req = fonts["med"].render(
                            f"LOG ARCHIVE // DAVID MARTINEZ - {format_num(req)} EC",
                            True,
                            CYAN if unlocked else MUTED_COLOR,
                        )
                        list_surface.blit(
                            txt_req, (item_rect.x + 15, item_rect.y + 10)
                        )

                        if unlocked:
                            first_line = text.split('\n')[0]
                            render_wrapped_text(
                                list_surface,
                                first_line,
                                fonts["small"],
                                TEXT_COLOR,
                                pygame.Rect(item_rect.x + 15, item_rect.y + 35, card_w - 30, 65),
                            )

                            txt_click_hint = fonts["small"].render(
                                "[ Cliquer pour ouvrir le grand texte & récupérer l'objet ]", True, GOLD
                            )
                            list_surface.blit(txt_click_hint, (item_rect.x + 15, item_rect.y + 115))
                        else:
                            txt_lock = fonts["small"].render(
                                "[ DONNÉES CHIFFRÉES - Accumulez l'énergie requise ]",
                                True,
                                MUTED_COLOR,
                            )
                            list_surface.blit(
                                txt_lock, (item_rect.x + 15, item_rect.y + 55)
                            )

            screen.blit(list_surface, (list_clip_rect.x, list_clip_rect.y))

        if active_modal:
            modal_w, modal_h = int(W * 0.5), int(H * 0.6)
            modal_rect = pygame.Rect(
                (W - modal_w) // 2, (H - modal_h) // 2, modal_w, modal_h
            )
            draw_cyber_card(
                screen, modal_rect, CYAN, is_hovered=False, bg_color=(10, 14, 26, 245)
            )

            btn_close = pygame.Rect(modal_rect.right - 40, modal_rect.y + 10, 30, 30)
            draw_cyber_card(screen, btn_close, RED, is_hovered=btn_close.collidepoint(mouse_pos))
            txt_cls = fonts["med"].render("X", True, RED)
            screen.blit(
                txt_cls,
                (
                    btn_close.x + (btn_close.width - txt_cls.get_width()) // 2,
                    btn_close.y + (btn_close.height - txt_cls.get_height()) // 2,
                ),
            )

            m_type, m_data = active_modal
            if m_type == "bot":
                txt_title = fonts["large"].render(m_data["name"], True, m_data["color"])
                screen.blit(txt_title, (modal_rect.x + 30, modal_rect.y + 25))

                paragraphs = [
                    f"Production : +{format_num(m_data['cps'])} EC/s",
                    "",
                    "Description :",
                    m_data["desc"],
                    "",
                    "Lore & Historique :",
                    m_data.get("lore", "Aucune donnée supplémentaire enregistrée dans les archives de Night City.")
                ]
                curr_y = modal_rect.y + 90
                for para in paragraphs:
                    if para:
                        render_wrapped_text(
                            screen,
                            para,
                            fonts["small"],
                            TEXT_COLOR,
                            pygame.Rect(modal_rect.x + 30, curr_y, modal_rect.width - 60, 40),
                        )
                        curr_y += 32
                    else:
                        curr_y += 12

            elif m_type == "upgrade":
                txt_title = fonts["large"].render(m_data["name"], True, GOLD)
                screen.blit(txt_title, (modal_rect.x + 30, modal_rect.y + 25))

                paragraphs = [
                    f"Coût d'acquisition : {format_num(m_data['cost'])} EC",
                    "",
                    "Description de l'amélioration :",
                    m_data["desc"],
                    "",
                    "Spécifications techniques :",
                    m_data.get("lore", "Module de surcadençage matériel certifié par les techniciens de Santo Domingo.")
                ]
                curr_y = modal_rect.y + 90
                for para in paragraphs:
                    if para:
                        render_wrapped_text(
                            screen,
                            para,
                            fonts["small"],
                            TEXT_COLOR,
                            pygame.Rect(modal_rect.x + 30, curr_y, modal_rect.width - 60, 40),
                        )
                        curr_y += 32
                    else:
                        curr_y += 12

            elif m_type == "item":
                txt_title = fonts["large"].render(m_data["name"], True, PINK)
                screen.blit(txt_title, (modal_rect.x + 30, modal_rect.y + 25))

                bought = game.items.get(m_data["id"], False)
                paragraphs = [
                    f"Bonus d'effet : {m_data['perf']}",
                    f"Statut actuel : {'Équipé (Débloqué)' if bought else 'Verrouillé (Lire l’histoire)'}",
                    "",
                    "Description :",
                    m_data["desc"]
                ]
                curr_y = modal_rect.y + 90
                for para in paragraphs:
                    if para:
                        render_wrapped_text(
                            screen,
                            para,
                            fonts["small"],
                            TEXT_COLOR,
                            pygame.Rect(modal_rect.x + 30, curr_y, modal_rect.width - 60, 40),
                        )
                        curr_y += 35
                    else:
                        curr_y += 15

            elif m_type == "story":
                req, text, item_id = m_data
                txt_title = fonts["large"].render(f"ARCHIVE // {format_num(req)} EC", True, CYAN)
                screen.blit(txt_title, (modal_rect.x + 30, modal_rect.y + 25))

                render_wrapped_text(
                    screen,
                    text,
                    fonts["small"],
                    TEXT_COLOR,
                    pygame.Rect(modal_rect.x + 30, modal_rect.y + 90, modal_rect.width - 60, modal_rect.height - 180),
                )

                if item_id:
                    item_obj = next(it for it in ITEMS_DATA if it["id"] == item_id)
                    has_item = game.items.get(item_id, False)

                    btn_item = pygame.Rect(
                        modal_rect.x + 30, modal_rect.bottom - 60, modal_rect.width - 60, 40
                    )
                    draw_cyber_card(
                        screen,
                        btn_item,
                        GREEN if has_item else PINK,
                        is_hovered=btn_item.collidepoint(mouse_pos),
                    )
                    btn_label = f"ÉQUIPÉ : {item_obj['name']}" if has_item else f"RÉCUPÉRER L'OBJET : {item_obj['name']}"
                    txt_btn = fonts["small"].render(btn_label, True, GREEN if has_item else PINK)
                    screen.blit(
                        txt_btn,
                        (
                            btn_item.x + (btn_item.width - txt_btn.get_width()) // 2,
                            btn_item.y + 12,
                        ),
                    )

        if is_paused:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((5, 7, 15, 220))
            screen.blit(overlay, (0, 0))

            btn_w, btn_h = int(W * 0.25), int(H * 0.065)
            cx = W // 2 - btn_w // 2

            if menu_state == "main":
                p_box = pygame.Rect(
                    int(W * 0.33), int(H * 0.14), int(W * 0.34), int(H * 0.72)
                )
                draw_cyber_card(
                    screen, p_box, CYAN, is_hovered=False, bg_color=PANEL_BG
                )

                txt_pause = fonts["large"].render("SYSTEM PAUSE", True, CYAN)
                screen.blit(
                    txt_pause,
                    (
                        p_box.x + (p_box.width - txt_pause.get_width()) // 2,
                        p_box.y + 20,
                    ),
                )

                label_jouer = (
                    "JOUER"
                    if game.relic_clicks == 0 and game.money == 0
                    else "REPRENDRE"
                )
                menu_options = [
                    (label_jouer, CYAN),
                    ("RECOMMENCER (RESTART)", PINK),
                    ("SAUVEGARDES", GOLD),
                    ("PARAMÈTRES", TEXT_COLOR),
                    ("QUITTER", RED),
                ]

                for idx, (label, col) in enumerate(menu_options):
                    b_rect = pygame.Rect(
                        cx, int(H * 0.26) + idx * int(H * 0.075), btn_w, btn_h
                    )
                    b_hov = b_rect.collidepoint(mouse_pos)
                    draw_cyber_card(
                        screen,
                        b_rect,
                        col if b_hov else CARD_BORDER,
                        is_hovered=b_hov,
                        bg_color=(25, 35, 60) if b_hov else CARD_BG,
                    )

                    txt_opt = fonts["med"].render(label, True, col)
                    screen.blit(
                        txt_opt,
                        (
                            b_rect.x + (b_rect.width - txt_opt.get_width()) // 2,
                            b_rect.y + (btn_h - txt_opt.get_height()) // 2,
                        ),
                    )

            elif menu_state == "settings":
                p_box = pygame.Rect(
                    int(W * 0.33), int(H * 0.14), int(W * 0.34), int(H * 0.72)
                )
                draw_cyber_card(
                    screen, p_box, TEXT_COLOR, is_hovered=False, bg_color=PANEL_BG
                )

                txt_settings = fonts["large"].render("PARAMÈTRES", True, CYAN)
                screen.blit(
                    txt_settings,
                    (
                        p_box.x + (p_box.width - txt_settings.get_width()) // 2,
                        p_box.y + 20,
                    ),
                )

                current_res = RESOLUTIONS_LIST[res_index]
                mode_str = "PLEIN ÉCRAN" if is_fullscreen else "FENÊTRÉ"
                settings_options = [
                    (f"RÉSOLUTION [{current_res[0]}x{current_res[1]}]", TEXT_COLOR),
                    (f"MODE [{mode_str}]", TEXT_COLOR),
                    (f"FPS [{FPS_LIST[fps_index]}]", TEXT_COLOR),
                    ("MODIFIER LES TOUCHES", GOLD),
                    ("RETOUR", CYAN),
                ]

                for idx, (label, col) in enumerate(settings_options):
                    b_rect = pygame.Rect(
                        cx, int(H * 0.26) + idx * int(H * 0.075), btn_w, btn_h
                    )
                    b_hov = b_rect.collidepoint(mouse_pos)
                    draw_cyber_card(
                        screen,
                        b_rect,
                        col if b_hov else CARD_BORDER,
                        is_hovered=b_hov,
                        bg_color=(25, 35, 60) if b_hov else CARD_BG,
                    )

                    txt_opt = fonts["med"].render(label, True, col)
                    screen.blit(
                        txt_opt,
                        (
                            b_rect.x + (b_rect.width - txt_opt.get_width()) // 2,
                            b_rect.y + (btn_h - txt_opt.get_height()) // 2,
                        ),
                    )

                if resolution_dropdown_open:
                    res_btn_rect = pygame.Rect(cx, int(H * 0.26), btn_w, btn_h)
                    for r_idx, res in enumerate(RESOLUTIONS_LIST):
                        item_rect = pygame.Rect(cx, res_btn_rect.bottom + r_idx * btn_h, btn_w, btn_h)
                        item_hov = item_rect.collidepoint(mouse_pos)
                        is_current = (res_index == r_idx)

                        draw_cyber_card(
                            screen,
                            item_rect,
                            CYAN if is_current else (TEXT_COLOR if item_hov else CARD_BORDER),
                            is_hovered=item_hov,
                            bg_color=(30, 45, 75) if item_hov else (15, 22, 38),
                        )
                        res_label = f"{res[0]}x{res[1]}"
                        txt_res = fonts["med"].render(res_label, True, CYAN if is_current else TEXT_COLOR)
                        screen.blit(
                            txt_res,
                            (
                                item_rect.x + (item_rect.width - txt_res.get_width()) // 2,
                                item_rect.y + (btn_h - txt_res.get_height()) // 2,
                            ),
                        )

            elif menu_state == "controls":
                p_box = pygame.Rect(
                    int(W * 0.28), int(H * 0.14), int(W * 0.44), int(H * 0.72)
                )
                draw_cyber_card(
                    screen, p_box, GOLD, is_hovered=False, bg_color=PANEL_BG
                )

                txt_ctrl = fonts["large"].render("LISTE DES TOUCHES", True, GOLD)
                screen.blit(
                    txt_ctrl,
                    (
                        p_box.x + (p_box.width - txt_ctrl.get_width()) // 2,
                        p_box.y + 20,
                    ),
                )

                actions_list = list(game.controls.keys())
                for idx, act in enumerate(actions_list):
                    txt_act = fonts["med"].render(act, True, TEXT_COLOR)
                    screen.blit(txt_act, (p_box.x + 30, int(H * 0.26) + idx * int(H * 0.08) + 10))

                    key_name = pygame.key.name(game.controls[act]).upper()
                    if waiting_for_key_action == act:
                        key_name = "APPUYEZ SUR UNE TOUCHE..."
                        btn_col = RED
                    else:
                        btn_col = CARD_BORDER

                    b_rect = pygame.Rect(cx + int(btn_w * 0.6), int(H * 0.26) + idx * int(H * 0.08), int(btn_w * 0.4), btn_h)
                    b_hov = b_rect.collidepoint(mouse_pos)
                    draw_cyber_card(screen, b_rect, CYAN if b_hov else btn_col, is_hovered=b_hov, bg_color=(25, 35, 60))

                    txt_k = fonts["small"].render(key_name, True, CYAN if waiting_for_key_action == act else TEXT_COLOR)
                    screen.blit(
                        txt_k,
                        (
                            b_rect.x + (b_rect.width - txt_k.get_width()) // 2,
                            b_rect.y + (btn_h - txt_k.get_height()) // 2,
                        ),
                    )

                btn_back_ctrl = pygame.Rect(cx, int(H * 0.75), btn_w, btn_h)
                draw_cyber_card(
                    screen, btn_back_ctrl, CYAN, is_hovered=btn_back_ctrl.collidepoint(mouse_pos)
                )
                txt_bc = fonts["med"].render("RETOUR", True, CYAN)
                screen.blit(
                    txt_bc,
                    (
                        btn_back_ctrl.x + (btn_back_ctrl.width - txt_bc.get_width()) // 2,
                        btn_back_ctrl.y + (btn_h - txt_bc.get_height()) // 2,
                    ),
                )

            elif menu_state == "saves":
                p_box = pygame.Rect(
                    int(W * 0.28), int(H * 0.12), int(W * 0.44), int(H * 0.76)
                )
                draw_cyber_card(
                    screen, p_box, GOLD, is_hovered=False, bg_color=PANEL_BG
                )

                txt_head = fonts["large"].render("SAUVEGARDES", True, GOLD)
                screen.blit(
                    txt_head,
                    (
                        p_box.x + (p_box.width - txt_head.get_width()) // 2,
                        p_box.y + 25,
                    ),
                )

                for slot in range(1, 4):
                    slot_y = int(H * 0.26) + (slot - 1) * int(H * 0.16)
                    slot_rect = pygame.Rect(
                        int(W * 0.31), slot_y, int(W * 0.38), int(H * 0.13)
                    )
                    info = get_slot_info(slot)

                    is_active_slot = game.current_slot == slot
                    draw_cyber_card(
                        screen,
                        slot_rect,
                        CYAN if is_active_slot else CARD_BORDER,
                        is_hovered=False,
                    )

                    t_title = fonts["med"].render(
                        f"SLOT {slot}" + (" [ACTIF]" if is_active_slot else ""),
                        True,
                        CYAN if is_active_slot else TEXT_COLOR,
                    )
                    screen.blit(t_title, (slot_rect.x + 15, slot_rect.y + 15))

                    t_detail = fonts["small"].render(
                        f"Énergie: {format_num(info['money'])} EC"
                        if info
                        else "--- EMPLACEMENT VIDE ---",
                        True,
                        MUTED_COLOR,
                    )
                    screen.blit(t_detail, (slot_rect.x + 15, slot_rect.y + 45))

                    btn_load = pygame.Rect(
                        int(W * 0.5), slot_y + 35, int(W * 0.07), 35
                    )
                    btn_save = pygame.Rect(
                        int(W * 0.58), slot_y + 35, int(W * 0.07), 35
                    )
                    btn_del = pygame.Rect(int(W * 0.66), slot_y + 35, 35, 35)

                    draw_cyber_card(
                        screen,
                        btn_load,
                        GREEN if info else CARD_BORDER,
                        is_hovered=btn_load.collidepoint(mouse_pos),
                    )
                    txt_ld = fonts["small"].render(
                        "LOAD", True, GREEN if info else MUTED_COLOR
                    )
                    screen.blit(
                        txt_ld,
                        (
                            btn_load.x + (btn_load.width - txt_ld.get_width()) // 2,
                            btn_load.y + 10,
                        ),
                    )

                    draw_cyber_card(
                        screen,
                        btn_save,
                        GOLD,
                        is_hovered=btn_save.collidepoint(mouse_pos),
                    )
                    txt_sv = fonts["small"].render("SAVE", True, GOLD)
                    screen.blit(
                        txt_sv,
                        (
                            btn_save.x + (btn_save.width - txt_sv.get_width()) // 2,
                            btn_save.y + 10,
                        ),
                    )

                    draw_cyber_card(
                        screen,
                        btn_del,
                        RED if info else CARD_BORDER,
                        is_hovered=btn_del.collidepoint(mouse_pos),
                    )
                    txt_dl = fonts["small"].render(
                        "X", True, RED if info else MUTED_COLOR
                    )
                    screen.blit(
                        txt_dl,
                        (
                            btn_del.x + (btn_del.width - txt_dl.get_width()) // 2,
                            btn_del.y + 10,
                        ),
                    )

                btn_back = pygame.Rect(cx, int(H * 0.78), btn_w, btn_h)
                draw_cyber_card(
                    screen, btn_back, CYAN, is_hovered=btn_back.collidepoint(mouse_pos)
                )
                txt_b = fonts["med"].render("RETOUR", True, CYAN)
                screen.blit(
                    txt_b,
                    (
                        btn_back.x + (btn_back.width - txt_b.get_width()) // 2,
                        btn_back.y + (btn_h - txt_b.get_height()) // 2,
                    ),
                )

        if confirmation_modal:
            c_rect = pygame.Rect(0, 0, W, H)
            draw_cyber_card(screen, c_rect, RED, is_hovered=False, bg_color=(12, 16, 28, 240))

            action, data = confirmation_modal
            msg = ""
            if action == "quit":
                msg = "Voulez-vous vraiment quitter le jeu ?"
            elif action == "restart":
                msg = "Recommencer la partie ? Toute progression non sauvegardée sera perdue."
            elif action == "delete_save":
                msg = f"Supprimer définitivement la sauvegarde du Slot {data} ?"

            txt_msg = fonts["large"].render(msg, True, TEXT_COLOR)
            screen.blit(txt_msg, (c_rect.x + (c_rect.width - txt_msg.get_width()) // 2, c_rect.y + int(H * 0.4)))

            btn_w_mod = int(W * 0.22)
            btn_h_mod = int(H * 0.08)
            btn_yes = pygame.Rect(W // 2 - btn_w_mod - int(W * 0.03), c_rect.y + int(H * 0.55), btn_w_mod, btn_h_mod)
            btn_no = pygame.Rect(W // 2 + int(W * 0.03), c_rect.y + int(H * 0.55), btn_w_mod, btn_h_mod)

            draw_cyber_card(screen, btn_yes, GREEN, is_hovered=btn_yes.collidepoint(mouse_pos), bg_color=(20, 35, 50))
            draw_cyber_card(screen, btn_no, RED, is_hovered=btn_no.collidepoint(mouse_pos), bg_color=(35, 20, 30))

            txt_yes = fonts["med"].render("OUI", True, GREEN)
            txt_no = fonts["med"].render("NON", True, RED)

            screen.blit(txt_yes, (btn_yes.x + (btn_yes.width - txt_yes.get_width()) // 2, btn_yes.y + (btn_h_mod - txt_yes.get_height()) // 2))
            screen.blit(txt_no, (btn_no.x + (btn_no.width - txt_no.get_width()) // 2, btn_no.y + (btn_h_mod - txt_no.get_height()) // 2))

        draw_notifications(screen, fonts["med"], game.notifications, W)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()