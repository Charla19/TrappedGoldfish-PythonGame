import random

import pygame


class Lance(pygame.sprite.Sprite):
    image_source = None
    image_mask = None

    def __init__(self, fleche):
        super().__init__()
        self.fleche = fleche
        if Lance.image_source is None:
            Lance.image_source = pygame.image.load("assets/espadon.png").convert_alpha()
            Lance.image_mask = pygame.mask.from_surface(Lance.image_source)
        self.image, self.mask = Lance.image_source, Lance.image_mask
        self.rect = self.image.get_rect()
        game = fleche.game
        self.rect.topleft = (game.WIDTH, random.randint(game.PLAY_TOP + 8,
                                                      game.PLAY_BOTTOM - self.rect.height - 8))
        self.x = float(self.rect.x)
        self.velocity = random.uniform(150, 390)

    def fall(self, dt=1 / 60):
        self.x -= self.velocity * dt
        self.rect.x = round(self.x)
        if self.rect.right < 0:
            self.kill()
        elif self.fleche.game.check_collision(self, self.fleche.game.all_players):
            self.fleche.game.player.damage(8)
            self.kill()
