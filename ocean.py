"""Continuous layered water: one reef image, no scrolling texture seams."""

import math
import random

import pygame


class Ocean:
    def __init__(self, image, size=(961, 650)):
        self.width, self.height = size
        self.base = pygame.transform.smoothscale(image, size).convert()
        wash = pygame.Surface(size, pygame.SRCALPHA)
        wash.fill((1, 24, 39, 38))
        self.base.blit(wash, (0, 0))
        self.time = 0.0
        rng = random.Random(241)
        self.dust = [(rng.uniform(0, self.width), rng.uniform(106, self.height),
                      rng.uniform(8, 32), rng.choice((1, 1, 2)), rng.uniform(0, math.tau))
                     for _ in range(34)]
        self.rays = pygame.Surface(size, pygame.SRCALPHA)
        for x, spread in [(120, 105), (480, 150), (755, 100)]:
            pygame.draw.polygon(self.rays, (137, 226, 243, 13),
                                [(x, 0), (x + 40, 0),
                                 (x + spread, self.height), (x - spread, self.height)])
        self.speck = {}
        for radius in (1, 2):
            dot = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(dot, (174, 231, 232, 16), (6, 6), radius + 3)
            pygame.draw.circle(dot, (192, 242, 241, 85), (6, 6), radius)
            self.speck[radius] = dot

    def update(self, dt, enabled=True):
        if enabled:
            self.time += max(0.0, dt)

    def draw(self, screen, motion=True):
        screen.blit(self.base, (0, 0))
        if not motion:
            return
        self.rays.set_alpha(round(155 + math.sin(self.time * 0.25) * 30))
        screen.blit(self.rays, (0, 0))
        for x, y, speed, radius, phase in self.dust:
            px = (x - self.time * speed) % (self.width + 24) - 12
            py = y + math.sin(self.time * 0.35 + phase) * 8
            screen.blit(self.speck[radius], (round(px) - 6, round(py) - 6))
