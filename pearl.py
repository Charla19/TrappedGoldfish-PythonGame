"""Collectible pearls drawn to match the game's underwater palette."""

import math
import random

import pygame


class Pearl(pygame.sprite.Sprite):
    image_source = None

    def __init__(self, x, y):
        super().__init__()
        if Pearl.image_source is None:
            image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(image, (102, 236, 238, 30), (20, 20), 20)
            pygame.draw.circle(image, (127, 244, 238, 75), (20, 20), 16)
            pygame.draw.circle(image, (244, 230, 204), (20, 20), 11)
            pygame.draw.circle(image, (255, 252, 235), (18, 17), 8)
            pygame.draw.circle(image, (255, 255, 255), (16, 15), 3)
            pygame.draw.arc(image, (224, 179, 145), (10, 10, 21, 21), 3.5, 6, 2)
            Pearl.image_source = image
        self.image = Pearl.image_source
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.base_y = y
        self.age = 0.0
        self.speed = random.uniform(200, 235)
        self.phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.age += dt
        self.x -= self.speed * dt
        self.rect.center = (round(self.x), round(self.base_y + math.sin(self.age * 2 + self.phase) * 5))
        if self.rect.right < 0:
            self.kill()
