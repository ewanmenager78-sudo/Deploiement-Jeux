import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON RELIC — 2087 | Menu Améliorations")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Courier New", 14, bold=True)
font_med = pygame.font.SysFont("Courier New", 18, bold=True)

class CyberUpgradesMenu:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.scroll_y = 0
        self.max_scroll = 0
        
        self.upgrades = [
            {"id": "neural_net", "name": "Neural Overclock", "cost": 150, "level": 1, "desc": "+15% Vitesse de clics", "icon_type": "chip", "color": (0, 255, 255)},
            {"id": "quantum_core", "name": "Quantum Core v1", "cost": 500, "level": 0, "desc": "Génère 5 Reliques/s", "icon_type": "core", "color": (255, 0, 128)},
            {"id": "nanobots", "name": "Swarm Nanobots", "cost": 1200, "level": 0, "desc": "Double l'auto-collecte", "icon_type": "bots", "color": (0, 255, 128)},
            {"id": "plasma_drill", "name": "Plasma Drill Mk.II", "cost": 3000, "level": 0, "desc": "+50 Puissance de forage", "icon_type": "drill", "color": (255, 165, 0)},
            {"id": "ai_governor", "name": "AI Sub-Routine", "cost": 7500, "level": 0, "desc": "Automatise les clics", "icon_type": "ai", "color": (147, 112, 219)},
            {"id": "dark_matter", "name": "Dark Matter Engine", "cost": 20000, "level": 0, "desc": "Multiplicateur global x2", "icon_type": "engine", "color": (0, 191, 255)}
        ]
        
        self.item_height = 80
        self.spacing = 10
        self.content_height = len(self.upgrades) * (self.item_height + self.spacing)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 30
            self.clamp_scroll()

    def clamp_scroll(self):
        max_limit = self.content_height - self.rect.height + 20
        self.max_scroll = max(0, max_limit)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def draw_cyber_icon(self, surface, icon_type, x, y, color):
        icon_rect = pygame.Rect(x, y, 60, 60)
        pygame.draw.rect(surface, (15, 15, 30), icon_rect)
        pygame.draw.rect(surface, color, icon_rect, 1)
        
        if icon_type == "chip":
            pygame.draw.rect(surface, color, (x+15, y+15, 30, 30), 2)
            pygame.draw.line(surface, color, (x+5, y+30), (x+15, y+30), 1)
            pygame.draw.line(surface, color, (x+45, y+30), (x+55, y+30), 1)
            pygame.draw.line(surface, color, (x+30, y+5), (x+30, y+15), 1)
            pygame.draw.line(surface, color, (x+30, y+45), (x+30, y+55), 1)
        elif icon_type == "core":
            pygame.draw.circle(surface, color, (x+30, y+30), 15, 2)
            pygame.draw.circle(surface, color, (x+30, y+30), 5)
        elif icon_type == "bots":
            pygame.draw.rect(surface, color, (x+20, y+20, 20, 25), 2)
            pygame.draw.line(surface, color, (x+25, y+15), (x+35, y+15), 2)
            pygame.draw.circle(surface, (255, 255, 255), (x+25, y+28), 2)
            pygame.draw.circle(surface, (255, 255, 255), (x+35, y+28), 2)
        elif icon_type == "drill":
            pygame.draw.polygon(surface, color, [(x+30, y+10), (x+45, y+50), (x+15, y+50)])
        elif icon_type == "ai":
            for i in range(3):
                pygame.draw.circle(surface, color, (x+15 + i*15, y+30), 4)
            pygame.draw.line(surface, color, (x+15, y+30), (x+45, y+30), 1)
        elif icon_type == "engine":
            pygame.draw.rect(surface, color, (x+22, y+15, 16, 30), 2)
            pygame.draw.line(surface, color, (x+15, y+25), (x+45, y+35), 1)

    def draw(self, surface, mouse_pos):
        content_surface = pygame.Surface((self.rect.width - 15, max(self.content_height, self.rect.height)))
        content_surface.fill((10, 10, 18))

        for i, up in enumerate(self.upgrades):
            item_y = i * (self.item_height + self.spacing)
            item_rect = pygame.Rect(10, item_y, content_surface.get_width() - 20, self.item_height)
            
            adjusted_mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y + self.scroll_y)
            is_hovered = item_rect.collidepoint(adjusted_mouse_pos)
            
            bg_color = (25, 25, 45) if is_hovered else (18, 18, 30)
            border_color = up["color"] if is_hovered else (40, 40, 70)
            
            pygame.draw.rect(content_surface, bg_color, item_rect)
            pygame.draw.rect(content_surface, border_color, item_rect, 1)
            
            self.draw_cyber_icon(content_surface, up["icon_type"], item_rect.x + 10, item_rect.y + 10, up["color"])
            
            name_surf = font_med.render(f"{up['name']} (Lv.{up['level']})", True, (240, 240, 255))
            desc_surf = font_small.render(up["desc"], True, (150, 150, 180))
            cost_surf = font_small.render(f"COÛT: {up['cost']} RELIQUES", True, up["color"])
            
            content_surface.blit(name_surf, (item_rect.x + 85, item_rect.y + 12))
            content_surface.blit(desc_surf, (item_rect.x + 85, item_rect.y + 36))
            content_surface.blit(cost_surf, (item_rect.x + 85, item_rect.y + 54))

        surface.blit(content_surface, (self.rect.x, self.rect.y), (0, self.scroll_y, self.rect.width, self.rect.height))

        if self.max_scroll > 0:
            bar_height = max(30, int(self.rect.height * (self.rect.height / self.content_height)))
            bar_y = self.rect.y + int((self.scroll_y / self.max_scroll) * (self.rect.height - bar_height))
            pygame.draw.rect(surface, (40, 40, 70), (self.rect.right - 10, self.rect.y, 6, self.rect.height))
            pygame.draw.rect(surface, (0, 255, 255), (self.rect.right - 10, bar_y, 6, bar_height))

menu = CyberUpgradesMenu(50, 50, 450, 500)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        menu.handle_event(event)

    screen.fill((5, 5, 10))
    
    title_surf = font_med.render("// SYSTEM UPGRADES", True, (0, 255, 255))
    screen.blit(title_surf, (50, 20))
    
    menu.draw(screen, mouse_pos)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()