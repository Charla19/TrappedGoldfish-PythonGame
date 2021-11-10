import pygame
import random

# créer une classe pour gérer cette lance
from sounds import SoundManager


class Lance(pygame.sprite.Sprite):

    def __init__(self, fleche):
        super().__init__()
        # définir l'image associé à cette lance
        self.sound_manager = SoundManager()
        self.image = pygame.image.load('assets/espadon.png')
        self.rect = self.image.get_rect()
        self.velocity = random.randint(2, 7)
        self.rect.y = random.randint(0, 650)
        self.rect.x = 961
        self.fleche = fleche


    def fall(self):
        self.rect.x -= self.velocity

        # vérifier si la lance touche le joueur
        if self.fleche.game.check_collision(
                self, self.fleche.game.all_players
        ):
            print("joueur touché")
            self.fleche.game.player.damage(2.7)
            self.sound_manager.play('click')