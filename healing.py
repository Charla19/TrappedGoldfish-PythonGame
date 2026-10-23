"""Rare healing bubble, distinguished from pearls by its heart silhouette."""

import math

import pygame


class HealingBubble(pygame.sprite.Sprite):
    image_source = None

    def __init__(self, x, y):
        super().__init__()
        if HealingBubble.image_source is None:
            image = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(image, (126, 245, 210, 25), (30, 30), 30)
            pygame.draw.circle(image, (14, 66, 77, 235), (30, 30), 23)
            pygame.draw.circle(image, (147, 246, 214, 240), (30, 30), 23, 2)
            heart = (255, 182, 153)
            pygame.draw.circle(image, heart, (24, 26), 7)
            pygame.draw.circle(image, heart, (36, 26), 7)
            pygame.draw.polygon(image, heart, [(17, 26), (43, 26), (30, 42)])
            pygame.draw.arc(image, (228, 255, 246), (10, 10, 40, 40), 0.7, 1.8, 2)
            HealingBubble.image_source = image
        self.image = HealingBubble.image_source
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.base_y = y
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        self.x -= 160 * dt
        self.rect.center = (round(self.x), round(self.base_y + math.sin(self.age * 2) * 5))
        if self.rect.right < 0:
            self.kill()
