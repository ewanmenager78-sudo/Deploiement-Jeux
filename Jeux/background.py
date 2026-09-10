import math
import random

import pygame

from config import CYBERPUNK_QUOTES, RED


class CyberpunkCityBackground:
    """Décor animé de Night City : immeubles, panneaux publicitaires,
    véhicules, dirigeable publicitaire, pluie et projecteurs."""

    def __init__(self, width, height):
        self.CYAN = (0, 240, 255)
        self.PINK = (255, 0, 110)
        self.YELLOW = (255, 215, 0)
        self.GREEN = (0, 255, 128)
        self.resize(width, height)

    def resize(self, width, height):
        self.width = width
        self.height = height

        self.bg_surf = pygame.Surface((width, height))
        for y in range(0, height, 4):
            ratio = y / height
            r = int(6 + (22 - 6) * ratio)
            g = int(8 + (18 - 8) * ratio)
            b = int(18 + (40 - 18) * ratio)
            pygame.draw.rect(self.bg_surf, (r, g, b), (0, y, width, 4))

        self.buildings = self._gen_3d_buildings(count=14)
        self.ads = self._gen_billboards()
        self.ground_vehicles = [self._spawn_ground_vehicle() for _ in range(12)]
        self.air_vehicles = [self._spawn_air_vehicle() for _ in range(8)]

        self.blimp = {
            "x": -300,
            "y": int(height * 0.12),
            "speed": 25,
            "text": random.choice(CYBERPUNK_QUOTES),
            "w": 140,
            "h": 40,
        }

        self.searchlights = [
            {"x": int(width * 0.2), "angle": 0.2, "speed": 0.8},
            {"x": int(width * 0.8), "angle": -0.4, "speed": -0.6},
        ]

        # Gestion aléatoire de la pluie
        self.is_raining = random.choice([True, False])
        self.rain_timer = 0.0
        self.rain_duration = random.uniform(15.0, 45.0) if self.is_raining else random.uniform(20.0, 60.0)

        self.rain = [
            [
                random.randint(0, width),
                random.randint(0, height),
                random.randint(15, 25),
                random.randint(900, 1400),
            ]
            for _ in range(150)
        ]

    def _gen_3d_buildings(self, count):
        buildings = []
        step = self.width / count
        for i in range(count):
            w = random.randint(int(step * 0.85), int(step * 1.35))
            h = random.randint(int(self.height * 0.4), int(self.height * 0.85))
            x = int(i * step)

            windows = []
            for wy in range(
                self.height - h + 25,
                self.height - 80,
                max(14, int(self.height * 0.028)),
            ):
                for wx in range(x + 12, x + w - 12, max(12, int(self.width * 0.012))):
                    windows.append({
                        "x": wx,
                        "y": wy,
                        "color": random.choice([
                            self.CYAN,
                            self.YELLOW,
                            (180, 210, 255),
                            self.PINK,
                        ]),
                        "flicker_speed": random.uniform(0.5, 3.0),
                        "offset": random.uniform(0, 100),
                    })

            buildings.append({
                "x": x,
                "w": w,
                "h": h,
                "color": (10, 14, 26),
                "top_color": (20, 30, 50),
                "windows": windows,
                "neon_edge": random.choice([self.CYAN, self.PINK, self.GREEN, None]),
            })
        return buildings

    def _gen_billboards(self):
        ads = []
        types = ["CYBER_GIRL", "HOLOGRAM_EYE", "CORP_LOGO"]
        for b in self.buildings:
            if b["w"] > 75 and random.random() > 0.4:
                ad_w = int(b["w"] * random.uniform(0.6, 0.85))
                ad_h = random.randint(45, 70)
                ad_x = b["x"] + (b["w"] - ad_w) // 2
                ad_y = (
                    self.height - b["h"] + random.randint(30, max(35, b["h"] - 120))
                )

                ads.append({
                    "x": ad_x,
                    "y": ad_y,
                    "w": ad_w,
                    "h": ad_h,
                    "type": random.choice(types),
                    "color": random.choice([self.CYAN, self.PINK, self.GREEN]),
                    "duration": random.uniform(8.0, 15.0),
                    "timer": random.uniform(0, 5.0),
                })
        return ads

    def _spawn_ground_vehicle(self):
        is_motorcycle = random.random() > 0.6
        direction = 1 if random.random() > 0.5 else -1
        speed = (
            random.randint(180, 350) * direction
            if is_motorcycle
            else random.randint(120, 220) * direction
        )
        x = -40 if direction > 0 else self.width + 40
        y = self.height - random.randint(
            int(self.height * 0.02), int(self.height * 0.08)
        )

        return {
            "x": x,
            "y": y,
            "speed": speed,
            "is_moto": is_motorcycle,
            "color": self.PINK if is_motorcycle else self.CYAN,
            "length": int(self.width * 0.01)
            if is_motorcycle
            else int(self.width * 0.023),
        }

    def _spawn_air_vehicle(self):
        direction = 1 if random.random() > 0.5 else -1
        speed = random.randint(150, 300) * direction
        x = -60 if direction > 0 else self.width + 60
        y = random.randint(int(self.height * 0.1), int(self.height * 0.55))
        return {
            "x": x,
            "y": y,
            "speed": speed,
            "color": random.choice([self.CYAN, self.PINK, self.YELLOW]),
        }

    def update_and_draw(self, surface, dt, now, fonts):
        W, H = self.width, self.height

        surface.blit(self.bg_surf, (0, 0))

        for sl in self.searchlights:
            sl["angle"] += sl["speed"] * dt
            end_x = sl["x"] + math.sin(sl["angle"]) * (W * 0.35)
            beam_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.polygon(
                beam_surf,
                (0, 240, 255, 12),
                [(sl["x"], H * 0.7), (end_x - 40, 0), (end_x + 40, 0)],
            )
            surface.blit(beam_surf, (0, 0))

        time_sec = now / 1000.0

        bl = self.blimp
        bl["x"] += bl["speed"] * dt
        if bl["x"] > W + 600:
            bl["x"] = -400
            bl["text"] = random.choice(CYBERPUNK_QUOTES)

        bx, by = int(bl["x"]), bl["y"]

        pygame.draw.ellipse(surface, (15, 20, 30), (bx, by, bl["w"], bl["h"]))
        pygame.draw.ellipse(surface, RED, (bx, by, bl["w"], bl["h"]), 2)
        pygame.draw.rect(surface, RED, (bx + 40, by + 12, 60, 16))
        txt_ara = fonts["small"].render("NIGHT-C", True, (255, 255, 255))
        surface.blit(txt_ara, (bx + 42, by + 13))

        band_x = bx - 320
        band_y = by + 50
        pygame.draw.line(
            surface, (100, 100, 100), (bx + 70, by + 28), (band_x + 300, band_y + 12), 1
        )

        wave_y = int(math.sin(time_sec * 3) * 4)
        pygame.draw.rect(surface, (10, 10, 15), (band_x, band_y + wave_y, 300, 26))
        pygame.draw.rect(surface, RED, (band_x, band_y + wave_y, 300, 26), 1)

        txt_prop = fonts["small"].render(bl["text"], True, RED)
        surface.blit(txt_prop, (band_x + 10, band_y + wave_y + 4))

        for b in self.buildings:
            bx_b, bw, bh = b["x"], b["w"], b["h"]
            pygame.draw.rect(surface, b["color"], (bx_b, H - bh, bw, bh))
            roof_pts = [
                (bx_b, H - bh),
                (bx_b + 15, H - bh - 10),
                (bx_b + bw + 15, H - bh - 10),
                (bx_b + bw, H - bh),
            ]
            pygame.draw.polygon(surface, b["top_color"], roof_pts)

            if b["neon_edge"]:
                pygame.draw.line(
                    surface, b["neon_edge"], (bx_b + bw, H - bh), (bx_b + bw, H), 2
                )

            for w in b["windows"]:
                val = math.sin(time_sec * w["flicker_speed"] + w["offset"])
                if val > -0.2:
                    intensity = min(255, max(50, int((val + 1.2) * 110)))
                    col = (
                        min(255, int(w["color"][0] * (intensity / 255))),
                        min(255, int(w["color"][1] * (intensity / 255))),
                        min(255, int(w["color"][2] * (intensity / 255))),
                    )
                    pygame.draw.rect(surface, col, (w["x"], w["y"], 4, 6))

        for ad in self.ads:
            ad["timer"] += dt
            if ad["timer"] > ad["duration"]:
                ad["timer"] = 0
                ad["type"] = random.choice([
                    "CYBER_GIRL",
                    "HOLOGRAM_EYE",
                    "CORP_LOGO",
                ])
                ad["color"] = random.choice([self.CYAN, self.PINK, self.GREEN])

            ax, ay, aw, ah = ad["x"], ad["y"], ad["w"], ad["h"]
            pygame.draw.rect(surface, (8, 12, 22), (ax, ay, aw, ah))
            pygame.draw.rect(surface, ad["color"], (ax, ay, aw, ah), 2)

            center_x = ax + aw // 2
            center_y = ay + ah // 2

            if ad["type"] == "CYBER_GIRL":
                blink = math.sin(time_sec * 4) > 0.8
                pygame.draw.circle(
                    surface, ad["color"], (center_x, center_y - 4), 10, 1
                )
                pygame.draw.line(
                    surface,
                    ad["color"],
                    (center_x - 5, center_y - 6),
                    (center_x - 1, center_y - 6),
                    2,
                )
                if not blink:
                    pygame.draw.line(
                        surface,
                        self.YELLOW,
                        (center_x + 2, center_y - 6),
                        (center_x + 6, center_y - 6),
                        2,
                    )
                pygame.draw.arc(
                    surface,
                    ad["color"],
                    (center_x - 6, center_y - 2, 12, 10),
                    math.pi,
                    0,
                    2,
                )

            elif ad["type"] == "HOLOGRAM_EYE":
                iris_r = int(6 + math.sin(time_sec * 3) * 3)
                pygame.draw.ellipse(
                    surface, ad["color"], (center_x - 14, center_y - 10, 28, 20), 1
                )
                pygame.draw.circle(surface, self.PINK, (center_x, center_y), iris_r, 1)
                pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 2)

            elif ad["type"] == "CORP_LOGO":
                angle = time_sec * 2
                pts = [
                    (
                        center_x + math.cos(angle) * 12,
                        center_y + math.sin(angle) * 12,
                    ),
                    (
                        center_x + math.cos(angle + 2.1) * 12,
                        center_y + math.sin(angle + 2.1) * 12,
                    ),
                    (
                        center_x + math.cos(angle + 4.2) * 12,
                        center_y + math.sin(angle + 4.2) * 12,
                    ),
                ]
                pygame.draw.polygon(surface, ad["color"], pts, 2)

            if random.random() > 0.85:
                glitch_y = random.randint(ay, ay + ah)
                pygame.draw.line(
                    surface, (255, 255, 255), (ax, glitch_y), (ax + aw, glitch_y), 1
                )

        pygame.draw.rect(surface, (8, 10, 16), (0, H - 70, W, 70))
        pygame.draw.line(surface, (30, 45, 70), (0, H - 70), (W, H - 70), 2)

        for v in self.ground_vehicles:
            v["x"] += v["speed"] * dt
            if v["x"] < -80 or v["x"] > W + 80:
                v.update(self._spawn_ground_vehicle())

            vx, vy = int(v["x"]), int(v["y"])
            dir_sign = 1 if v["speed"] > 0 else -1
            trail_len = 35 if v["is_moto"] else 50
            pygame.draw.line(
                surface,
                RED,
                (vx, vy),
                (vx - (trail_len * dir_sign), vy),
                2 if v["is_moto"] else 3,
            )
            v_size = (10, 5) if v["is_moto"] else (v["length"], 8)
            pygame.draw.rect(
                surface,
                v["color"],
                (vx - v_size[0] // 2, vy - v_size[1] // 2, v_size[0], v_size[1]),
                border_radius=2,
            )

        for f in self.air_vehicles:
            f["x"] += f["speed"] * dt
            if f["x"] < -100 or f["x"] > W + 100:
                f.update(self._spawn_air_vehicle())

            fx, fy = int(f["x"]), int(f["y"])
            f_dir = 1 if f["speed"] > 0 else -1
            pygame.draw.line(
                surface, f["color"], (fx, fy), (fx - (40 * f_dir), fy), 2
            )
            pygame.draw.circle(surface, (255, 255, 255), (fx, fy), 3)

        # Gestion de l'alternance pluie / beau temps de façon aléatoire
        self.rain_timer += dt
        if self.rain_timer >= self.rain_duration:
            self.rain_timer = 0.0
            self.is_raining = not self.is_raining
            self.rain_duration = random.uniform(15.0, 45.0) if self.is_raining else random.uniform(20.0, 60.0)

        if self.is_raining:
            for drop in self.rain:
                drop[1] += drop[3] * dt
                drop[0] -= 120 * dt
                if drop[1] > H:
                    drop[1] = -20
                    drop[0] = random.randint(0, W + 200)

                pygame.draw.line(
                    surface,
                    (120, 180, 255, 90),
                    (drop[0], drop[1]),
                    (drop[0] - 4, drop[1] + drop[2]),
                    1,
                )
