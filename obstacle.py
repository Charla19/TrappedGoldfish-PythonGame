import random

import pygame


class Obstacle(pygame.sprite.Sprite):
    image_source = None
    image_mask = None

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health = self.max_health = 60
        if Obstacle.image_source is None:
            Obstacle.image_source = pygame.image.load("assets/requin.png").convert_alpha()
            Obstacle.image_mask = pygame.mask.from_surface(Obstacle.image_source)
        self.image, self.mask = Obstacle.image_source, Obstacle.image_mask
        self.rect = self.image.get_rect()
        self.rect.x = game.WIDTH + random.randint(20, 175)
        self.rect.y = random.randint(game.PLAY_TOP + 8, game.PLAY_BOTTOM - self.rect.height - 8)
        self.x = float(self.rect.x)
        self.velocity = random.uniform(180, 360)

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            self.game.add_score(self.game.SHARK_POINTS, combo_bonus=True)

    def forward(self, dt=1 / 60):
        if round(self.x) != self.rect.x:
            self.x = float(self.rect.x)
        self.x -= self.velocity * dt
        self.rect.x = round(self.x)
        if self.rect.right < 0:
            self.kill()
            self.game.add_score(2, combo_bonus=True)
        elif self.game.check_collision(self, self.game.all_players):
            self.game.player.damage(12)
