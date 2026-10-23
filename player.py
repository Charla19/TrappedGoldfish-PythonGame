import math

import pygame

from projectile import Projectile
from sounds import SoundManager


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health = self.max_health = 100
        self.attack = 20
        self.velocity = 300.0
        self.sound_manager = SoundManager()
        self.all_projectile = pygame.sprite.Group()
        self.image = pygame.image.load("assets/poisson.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(24, 320))
        self.position_y = float(self.rect.y)
        self.speed_y = 0.0
        self.invulnerable_until = 0.0
        self.last_shot = -1.0

    def damage(self, amount):
        if not self.game.is_playing or self.game.shield_remaining > 0:
            return
        now = self.game.elapsed
        if now < self.invulnerable_until:
            return
        self.invulnerable_until = now + 0.7
        self.game.break_combo()
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.game.game_over()

    def launch_projectile(self):
        if not self.game.is_playing or self.game.paused:
            return False
        if self.game.elapsed - self.last_shot < 0.18 - 1e-8:
            return False
        self.last_shot = self.game.elapsed
        self.all_projectile.add(Projectile(self))
        self.sound_manager.play("projectile")
        return True

    def move(self, direction, dt):
        if self.rect.y != round(self.position_y):
            self.position_y = float(self.rect.y)
        target = direction * self.velocity
        rate = 28 if direction else 34
        decay = math.exp(-rate * dt)
        self.position_y += target * dt + (self.speed_y - target) * (1 - decay) / rate
        self.speed_y = target + (self.speed_y - target) * decay
        low, high = self.game.PLAY_TOP, self.game.PLAY_BOTTOM - self.rect.height
        self.position_y = max(low, min(high, self.position_y))
        self.rect.y = round(self.position_y)
        if self.position_y in (low, high):
            self.speed_y = 0.0

    def move_up(self, dt=1 / 60):
        self.move(-1, dt)

    def move_down(self, dt=1 / 60):
        self.move(1, dt)
