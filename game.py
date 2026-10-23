"""Time-based gameplay and a compact, shared-style heads-up display."""

import random

import pygame

import controls
import ui
from fleche import FlecheFallEvent
from healing import HealingBubble
from obstacle import Obstacle
from pearl import Pearl
from player import Player
from sounds import SoundManager


class Game:
    WIDTH, HEIGHT = 961, 650
    PLAY_TOP, PLAY_BOTTOM = 112, 590
    PEARL_POINTS, SHARK_POINTS = 5, 10
    HEAL_INTERVAL, HEAL_AMOUNT = 30.0, 10

    def __init__(self):
        ui.font.cache_clear()
        ui.label.cache_clear()
        SoundManager._sounds = None
        self.sound_manager = SoundManager()
        self.player = Player(self)
        self.all_players = pygame.sprite.Group(self.player)
        self.all_obstacle = pygame.sprite.Group()
        self.pearls = pygame.sprite.Group()
        self.healing_bubbles = pygame.sprite.Group()
        self.fleche = FlecheFallEvent(self)
        self.pressed = {}
        self.is_playing = self.paused = False
        self.mouse_fire = False
        self.motion_enabled = True
        self._reset_counters()
        radius = max(self.player.rect.size) // 2 + 13
        self.shield_image = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        center = (radius + 2, radius + 2)
        pygame.draw.circle(self.shield_image, (90, 224, 255, 30), center, radius)
        pygame.draw.circle(self.shield_image, (138, 247, 255, 220), center, radius, 2)
        pygame.draw.arc(self.shield_image, (240, 255, 255, 220),
                        (8, 8, radius * 2 - 12, radius * 2 - 12), 0.5, 1.8, 3)

    def _reset_counters(self):
        self.score = self.pearls_collected = self.combo_count = 0
        self.elapsed = self.spawn_timer = self.survival_timer = 0.0
        self.combo_remaining = self.shield_remaining = 0.0
        self.best_multiplier = 1
        self.shield_charge = self.shield_uses = 0
        self.pearl_timer = 0.65
        self.heal_timer = self.HEAL_INTERVAL
        self.last_pearl_y = random.uniform(180, 510)
        self.popups = []

    @property
    def multiplier(self):
        return min(5, 1 + self.combo_count // 3)

    @property
    def shield_ready(self):
        return self.shield_charge >= 8 and self.shield_remaining <= 0

    def start(self):
        self._reset_counters()
        self.is_playing, self.paused = True, False
        self.clear_input()
        self.all_obstacle.empty()
        self.pearls.empty()
        self.healing_bubbles.empty()
        self.player.all_projectile.empty()
        self.fleche.all_lance.empty()
        self.fleche.reset_percent()
        self.player.health = self.player.max_health
        self.player.rect.topleft = (24, 320)
        self.player.previous_center = self.player.rect.center
        self.player.position_y = 320.0
        self.player.speed_y = self.player.invulnerable_until = 0.0
        self.player.last_shot = -1.0
        for index in range(3):
            self.spawn_obstacle(extra_x=index * 225)

    def clear_input(self):
        self.pressed.clear()
        self.mouse_fire = False
        self.player.speed_y = 0.0

    def add_score(self, points, combo_bonus=False):
        self.score += points * (self.multiplier if combo_bonus else 1)

    def spawn_pearl(self, x=None, y=None):
        if len(self.pearls) >= 18:
            return None
        if y is None:
            # Mostly reachable changes in height, with occasional wider jumps.
            if random.random() < 0.25:
                y = random.uniform(140, self.PLAY_BOTTOM - 24)
            else:
                offset = random.choice((-1, 1)) * random.uniform(45, 145)
                y = self.last_pearl_y + offset
            y = max(140, min(self.PLAY_BOTTOM - 24, y))
            if abs(y - self.last_pearl_y) < 30:
                y = max(140, min(self.PLAY_BOTTOM - 24,
                                self.last_pearl_y + (65 if self.last_pearl_y < 350 else -65)))
        self.last_pearl_y = y
        pearl = Pearl(self.WIDTH + 28 if x is None else x, y)
        self.pearls.add(pearl)
        return pearl

    def collect_pearl(self, pearl):
        if not self.is_playing or not pearl.alive():
            return
        pearl.kill()
        self.pearls_collected += 1
        self.combo_count += 1
        self.combo_remaining = 3.5
        self.best_multiplier = max(self.best_multiplier, self.multiplier)
        points = self.PEARL_POINTS * self.multiplier
        self.add_score(points)
        was_ready = self.shield_ready
        if self.shield_remaining <= 0:
            self.shield_charge = min(8, self.shield_charge + 1)
        self.popups.append({"text": f"+{points}", "x": 125,
                            "y": float(self.player.rect.centery), "life": 0.8})
        if self.shield_ready and not was_ready:
            self.popups.append({"text": "Bouclier prêt  ·  → / E", "x": 480,
                                "y": 128.0, "life": 1.7})

    def break_combo(self):
        self.combo_count = 0
        self.combo_remaining = 0.0

    def spawn_healing(self):
        if self.healing_bubbles:
            return None
        y = random.uniform(self.PLAY_TOP + 40, self.PLAY_BOTTOM - 35)
        bubble = HealingBubble(self.WIDTH + 32, y)
        self.healing_bubbles.add(bubble)
        return bubble

    def collect_healing(self, bubble):
        if not self.is_playing or bubble not in self.healing_bubbles:
            return
        bubble.kill()
        restored = min(self.HEAL_AMOUNT, self.player.max_health - self.player.health)
        self.player.health += restored
        message = f"+{restored:g} PV" if restored else "Vie au maximum"
        self.popups.append({"text": message, "x": 150,
                            "y": float(self.player.rect.centery - 30), "life": 1.3,
                            "color": ui.AQUA})
        self.sound_manager.play("click")

    def activate_shield(self):
        if not self.is_playing or self.paused or not self.shield_ready:
            return False
        self.shield_charge = 0
        self.shield_remaining = 5.0
        self.shield_uses += 1
        self.popups = [popup for popup in self.popups if not popup["text"].startswith("Bouclier prêt")]
        self.sound_manager.play("click")
        return True

    def update_bonuses(self, dt):
        self.shield_remaining = max(0.0, self.shield_remaining - dt)
        self.combo_remaining = max(0.0, self.combo_remaining - dt)
        if self.combo_remaining == 0:
            self.break_combo()
        self.pearls.update(dt)
        self.healing_bubbles.update(dt)
        self.heal_timer = max(0.0, self.heal_timer - dt)
        if self.heal_timer <= 1e-8 and not self.healing_bubbles:
            self.spawn_healing()
            self.heal_timer = self.HEAL_INTERVAL
        for bubble in list(self.healing_bubbles):
            if self.player.rect.colliderect(bubble.rect.inflate(-16, -16)):
                self.collect_healing(bubble)
        self.pearl_timer -= dt
        # Each event emits one pearl, rarely two. Nothing appears in the middle
        # of the scene: all new collectibles enter through the right edge.
        while self.pearl_timer <= 0:
            pearl = self.spawn_pearl()
            if pearl and random.random() < 0.14:
                second_y = pearl.base_y + (85 if pearl.base_y < 350 else -85)
                self.spawn_pearl(x=self.WIDTH + 45, y=second_y)
            delay = random.uniform(0.5, 1.1)
            self.pearl_timer += delay
        for pearl in list(self.pearls):
            if self.player.rect.colliderect(pearl.rect.inflate(-16, -16)):
                self.collect_pearl(pearl)
        for popup in self.popups:
            popup["life"] -= dt
            if self.motion_enabled and popup["text"].startswith("+"):
                popup["y"] -= 22 * dt
        self.popups = [popup for popup in self.popups if popup["life"] > 0]

    def game_over(self):
        if self.is_playing:
            self.is_playing, self.paused = False, False
            self.clear_input()
            self.sound_manager.play("game_over")

    def spawn_obstacle(self, extra_x=0):
        obstacle = Obstacle(self)
        obstacle.rect.x += extra_x
        obstacle.x = float(obstacle.rect.x)
        self.all_obstacle.add(obstacle)
        return obstacle

    def spawn_interval(self):
        return max(0.85, 2.25 - self.elapsed / 75.0)

    def step(self, dt):
        if not self.is_playing or self.paused:
            return
        dt = min(max(dt, 0.0), 0.1)
        for sprite in [self.player, *self.pearls, *self.healing_bubbles, *self.player.all_projectile,
                       *self.all_obstacle, *self.fleche.all_lance]:
            sprite.previous_center = sprite.rect.center
        self.elapsed += dt
        self.spawn_timer += dt
        self.survival_timer += dt
        while self.survival_timer >= 1.0 - 1e-8:
            self.survival_timer -= 1.0
            self.add_score(1)
        if self.spawn_timer >= self.spawn_interval() and len(self.all_obstacle) < 6:
            self.spawn_timer -= self.spawn_interval()
            self.spawn_obstacle()
        direction = int(any(self.pressed.get(key) for key in controls.DOWN))
        direction -= int(any(self.pressed.get(key) for key in controls.UP))
        self.player.move(direction, dt)
        if self.mouse_fire or any(self.pressed.get(key) for key in controls.FIRE):
            self.player.launch_projectile()
        self.update_bonuses(dt)
        for projectile in list(self.player.all_projectile):
            projectile.move(dt)
        for obstacle in list(self.all_obstacle):
            obstacle.forward(dt)
            if not self.is_playing:
                break
        if self.is_playing:
            self.fleche.add_percent(dt)
            self.fleche.attempt_fall()
            for lance in list(self.fleche.all_lance):
                lance.fall(dt)
                if not self.is_playing:
                    break

    def update(self, screen, dt):
        self.step(dt)
        self.draw_world(screen)

    def draw_world(self, screen, alpha=1.0):
        def draw_sprite(sprite):
            current = sprite.rect.center
            previous = getattr(sprite, "previous_center", current)
            center = (round(previous[0] + (current[0] - previous[0]) * alpha),
                      round(previous[1] + (current[1] - previous[1]) * alpha))
            screen.blit(sprite.image, sprite.image.get_rect(center=center))
            return center

        for group in (self.pearls, self.healing_bubbles, self.player.all_projectile,
                      self.all_obstacle, self.fleche.all_lance):
            for sprite in group:
                draw_sprite(sprite)
        player_center = draw_sprite(self.player)
        if self.shield_remaining > 0:
            screen.blit(self.shield_image, self.shield_image.get_rect(center=player_center))
        for popup in self.popups:
            image = ui.label(popup["text"], 19, popup.get("color", ui.CORAL), True)
            rect = image.get_rect(center=(popup["x"], popup["y"]))
            if popup["text"].startswith("Bouclier prêt"):
                ui.panel(screen, rect.inflate(28, 12))
            else:
                shadow = ui.label(popup["text"], 19, ui.INK, True)
                for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    screen.blit(shadow, rect.move(*offset))
            screen.blit(image, rect)
        self.draw_hud(screen)

    def draw_hud(self, screen):
        ui.panel(screen, (16, 16, 929, 82))
        ui.text(screen, "SCORE", (32, 24), 17, ui.MUTED)
        ui.text(screen, f"{self.score:,}".replace(",", " "), (32, 43), 30, bold=True,
                max_width=144)
        ui.text(screen, f"VIE  {max(0, int(self.player.health))}%", (192, 30), 17, ui.PALE)
        ui.meter(screen, (192, 65, 128, 8), self.player.health / 100, ui.AQUA)
        ui.text(screen, "PERLES", (350, 25), 17, ui.MUTED)
        ui.text(screen, self.pearls_collected, (350, 48), 24, ui.CORAL, True)
        ui.text(screen, f"COMBO ×{self.multiplier}", (458, 30), 19, ui.PALE, True)
        ui.meter(screen, (458, 65, 150, 8), self.combo_remaining / 3.5, ui.CORAL)
        ui.panel(screen, (16, 604, 929, 32), 235)
        ui.text(screen, "↑ ↓  Nager     Entrée / Espace  Tirer     → / E  Bouclier",
                (32, 609), 17, ui.MUTED)
        ui.text(screen, "Vague", (776, 609), 17, ui.MUTED)
        ui.meter(screen, (842, 618, 84, 5), self.fleche.percent / 100, ui.CORAL)

    def check_collision(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)
