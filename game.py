
from player import Player
from obstacle import Obstacle
from fleche import FlecheFallEvent

import pygame

# Créer une seconde classe qui va représenter notre jeu
from sounds import SoundManager


class Game:

    def __init__(self):
        # Définir si notre jeu a commencé ou non
        self.is_playing = False
        # Générer notre joueur
        self.all_players = pygame.sprite.Group()
        self.player = Player(self)
        self.all_players.add(self.player)
        # générer l'évènement fleche
        self.fleche = FlecheFallEvent(self)
        # Groupe d'obstacle
        self.all_obstacle = pygame.sprite.Group()
        # gerer le son
        self.sound_manager = SoundManager()
        # mettre le score à zéro
        self.font = pygame.font.SysFont("Arial Black", 30)
        self.score = 0
        self.pressed = {}

    def start(self):
        self.is_playing = True
        self.spawn_obstacle()
        self.spawn_obstacle()
        self.spawn_obstacle()
        self.spawn_obstacle()
        self.spawn_obstacle()

    def add_score(self, points):
        self.score += points

    def game_over(self):
        # remettre le jeu à neuf, retirer les monstres, remettre le joueur à 100% vie, jeu en attente
        self.all_obstacle = pygame.sprite.Group()
        self.player.health = self.player.max_health
        self.is_playing = False
        self.score = 0
        self.sound_manager.play('game_over')

    def update(self, screen):
        # afficher le score sur l'écran
        score_text = self.font.render(f"SCORE :{self.score}", 1, (0, 0, 0))
        screen.blit(score_text, (20, 20))

        # Appliquer l'image du joueur
        screen.blit(self.player.image, self.player.rect)

        # Actualiser la barre de vie du joueur
        self.player.update_health_bar(screen)

        # actualiser la barre d'évènement du jeu
        self.fleche.update_bar(screen)


        # Récupérer les projectiles du joueur
        for projectile in self.player.all_projectile:
            projectile.move()

        # Récupérer les obstacles de notre jeu
        for obstacle in self.all_obstacle:
            obstacle.forward()
            #obstacle.update_health_bar(screen)

        # récupérer les lances de notre jeu
        for lance in self.fleche.all_lance:
            lance.fall()


        # Appliquer l'ensemble des images de mon groupe de projecteur
        self.player.all_projectile.draw(screen)

        # Appliquer l'ensemble des images de mon goupe d' obstacle
        self.all_obstacle.draw(screen)

        # appliquer l'ensemble des images de mon groupe de lance
        self.fleche.all_lance.draw(screen)

        # Vérifier si le joueur souhaite aller en haut ou en bas
        if self.pressed.get(pygame.K_UP) and self.player.rect.y > 0:
            self.player.move_up()
        elif self.pressed.get(pygame.K_DOWN) and self.player.rect.y < 590:
            self.player.move_down()

    def check_collision(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)

    def spawn_obstacle(self):
        obstacle = Obstacle(self)
        self.all_obstacle.add(obstacle)
