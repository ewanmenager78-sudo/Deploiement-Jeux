import math
import pygame
from config import (
    CARD_BG,
    CARD_BORDER,
    CYAN,
    GOLD,
    GREEN,
    MUTED_COLOR,
    PINK,
    RED,
    TEXT_COLOR,
    font_med,
    font_small,
)

def format_num(n):
    if n < 1000:
        return f"{int(n)}"
    for unit in ["k", "M", "Md", "B"]:
        n /= 1000.0
        if n < 1000:
            return f"{n:.1f}{unit}"
    return f"{n:.1f}T"

def draw_cyber_card(surface, rect, border_color, is_hovered=False, bg_color=CARD_BG):
    """Dessine une carte cyberpunk avec les coins biseautés."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    cut = 8

    points = [
        (x + cut, y), (x + w, y),
        (x + w, y + h - cut), (x + w - cut, y + h),
        (x, y + h), (x, y + cut)
    ]
    
    pygame.draw.polygon(surface, bg_color, points)
    pygame.draw.polygon(surface, border_color, points, 1 if not is_hovered else 2)

    if is_hovered:
        pygame.draw.line(surface, border_color, (x, y + cut), (x + cut + 4, y), 2)
        pygame.draw.line(surface, border_color, (x + w - cut - 4, y + h), (x + w, y + h - cut), 2)


class CyberButton:
    def __init__(self, x, y, width, height, text, border_color=CYAN, text_color=TEXT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.border_color = border_color
        self.text_color = text_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Fond légèrement plus clair ou teinté au survol
        bg_color = (20, 25, 45) if is_hovered else CARD_BG
        current_border = GOLD if is_hovered else self.border_color
        
        # Utilisation de la charte cyberpunk existante
        draw_cyber_card(surface, self.rect, current_border, is_hovered=is_hovered, bg_color=bg_color)
        
        # Rendu du texte centré avec la police moyenne
        txt_surf = font_med.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


def draw_cyber_icon(surface, icon_type, x, y, color, now):
    """Génère des icônes vectorielles animées style Cyberpunk."""
    box_rect = pygame.Rect(x, y, 60, 60)
    draw_cyber_card(surface, box_rect, color, is_hovered=False, bg_color=(10, 12, 22))

    cx, cy = x + 30, y + 30
    pulse = math.sin(now * 5) * 2

    if icon_type == "drone":
        offset = math.sin(now * 4) * 3
        pygame.draw.ellipse(surface, color, (cx - 16, cy - 6 + offset, 32, 12), 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx, int(cy + offset)), 2)
        pygame.draw.line(surface, color, (cx - 12, cy + offset), (cx - 20, cy + 8 + offset), 1)
        pygame.draw.line(surface, color, (cx + 12, cy + offset), (cx + 20, cy + 8 + offset), 1)

    elif icon_type == "cyborg":
        pygame.draw.circle(surface, color, (cx, cy - 2), int(12 + pulse), 2)
        pygame.draw.rect(surface, RED, (cx - 6, cy - 4, 12, 4))
        pygame.draw.line(surface, color, (cx - 8, cy + 12), (cx + 8, cy + 12), 2)

    elif icon_type == "ai":
        pygame.draw.rect(surface, color, (cx - 14, cy - 14, 28, 28), 2)
        r = int(4 + math.sin(now * 6) * 2)
        pygame.draw.circle(surface, PINK, (cx, cy), max(1, r))
        pygame.draw.line(surface, color, (cx - 18, cy), (cx - 14, cy), 2)
        pygame.draw.line(surface, color, (cx + 14, cy), (cx + 18, cy), 2)

    elif icon_type == "core":
        ang = now * 2
        for i in range(3):
            a = ang + i * (2 * math.pi / 3)
            px = cx + math.cos(a) * 12
            py = cy + math.sin(a) * 12
            pygame.draw.circle(surface, color, (int(px), int(py)), 4)
        pygame.draw.circle(surface, GOLD, (cx, cy), int(6 + pulse))

    elif icon_type == "drill":
        p1 = (cx, cy - 16)
        p2 = (cx + 14, cy + 14)
        p3 = (cx - 14, cy + 14)
        pygame.draw.polygon(surface, color, [p1, p2, p3], 2)
        pygame.draw.line(surface, PINK, (cx, cy - 8), (cx, cy + 10), 2)

    elif icon_type == "chip":
        pygame.draw.rect(surface, color, (cx - 12, cy - 12, 24, 24), 2)
        pygame.draw.rect(surface, CYAN, (cx - 5, cy - 5, 10, 10))
        for offset_p in [-8, 0, 8]:
            pygame.draw.line(surface, color, (cx + offset_p, cy - 12), (cx + offset_p, cy - 17), 1)
            pygame.draw.line(surface, color, (cx + offset_p, cy + 12), (cx + offset_p, cy + 17), 1)

def render_wrapped_text(surface, text, font, color, rect):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= rect.width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y = rect.y
    for line in lines:
        if y + font.get_height() <= rect.y + rect.height:
            txt_surf = font.render(line, True, color)
            surface.blit(txt_surf, (rect.x, y))
            y += font.get_height() + 2

def draw_notifications(surface, font, notifications, width):
    y_offset = 20
    for notif in notifications[:]:
        box_w = min(500, width - 40)
        box_h = 60
        box_x = (width - box_w) // 2
        box_y = y_offset

        surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        surf.fill((13, 16, 28, 230))
        pygame.draw.rect(surf, GOLD, (0, 0, box_w, box_h), width=2)

        txt_t = font_med.render(notif["title"], True, GOLD)
        txt_d = font_small.render(notif["text"], True, TEXT_COLOR)

        surf.blit(txt_t, (15, 8))
        surf.blit(txt_d, (15, 30))

        surface.blit(surf, (box_x, box_y))
        y_offset += box_h + 10