import pygame
import random
# Créer une classe qui va gérer la notion d'obstacle sur le jeu
class Obstacle(pygame.sprite.Sprite):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health = 60
        self.max_health = 100
        self.attack = 0.5
        self.image = pygame.image.load("assets/requin.png")
        self.rect = self.image.get_rect()
        self.rect.x = 875 + random.randint(0, 200)
        self.rect.y = random.randint(0, 650)
        self.velocity = random.randint(2, 6)

    def damage(self, amount):
        # Infliger les dégats
        self.health -= amount

        # Véérifier si son nouveau nombre de vie et inférieur à zéro
        if self.health <= 0:
            # Réapparaître comme un nouvel obstacle
            self.rect.x = 875 + random.randint(0, 1000)
            self.velocity = random.randint(2, 6)
            self.health = self.max_health
            # ajouter le nombre de points
            self.game.add_score(5)

        # si la barre d'évènement est chargé à son maximum
        if self.game.fleche.is_full_loaded():
            # retirer du jeu
            self.game.all_obstacle.remove(self)

    def update_health_bar(self, surface):

        # Dessiner la barre de vie
        pygame.draw.rect(surface, (60, 60, 60), [self.rect.x +10, self.rect.y, self.max_health, 5])
        pygame.draw.rect(surface, (100, 200, 60), [self.rect.x +10, self.rect.y, self.health, 5])

    def forward(self):
        # Le déplacement ne se fait que si il n'y a pas de collision avec un groupe de joueur
        if not self.game.check_collision(self, self.game.all_players):
            self.rect.x -= self.velocity
        # Si le monstre entre en collision avec le joueur
        else:
            # Indliger des dégâts
            self.game.player.damage(self.attack)





