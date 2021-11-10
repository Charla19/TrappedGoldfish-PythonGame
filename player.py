import pygame

import game
from projectile import Projectile

# Créer une première classe qui va representer le joueur
from sounds import SoundManager


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health = 100
        self.attack = 20
        self.max_health = 100
        self.velocity = 5
        self.sound_manager = SoundManager()
        self.all_projectile = pygame.sprite.Group()
        self.image = pygame.image.load("assets/poisson.png")
        # récupérer la position du joueur
        self.rect = self.image.get_rect()
        self.rect.y = 550

    def damage(self, amount):
        if self.health - amount > amount:
            self.health -= amount
        else:
            # Si le joueur n'a plus de point de vie
            self.game.game_over()

    def update_health_bar(self, surface):
        # Dessiner la barre de vie
        pygame.draw.rect(surface, (60, 60, 60), [self.rect.x + 5, self.rect.y, self.max_health, 5])
        pygame.draw.rect(surface, (100, 200, 60), [self.rect.x + 5, self.rect.y, self.health, 5])

    def launch_projectile(self):
        # Créer une nouvelle instance de la classe projectile
        self.all_projectile.add(Projectile(self))
        # jouer le son
        self.sound_manager.play('projectile')

    def move_up(self):
        # Si le joueur n'est pas en collision avec un obstacle
        if not self.game.check_collision(self, self.game.all_obstacle):
            self.rect.x = self.velocity

        self.rect.y -= self.velocity

    def move_down(self):
        self.rect.y += self.velocity