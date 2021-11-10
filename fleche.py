import pygame
from lance import Lance

# Créer une classe pour gérer cet évènement
class FlecheFallEvent:

    # lors du chargement -> créer un compteur
    def __init__(self, game):
        self.percent = 0
        self.percent_speed = 60
        self.game = game

        #définir un groupe de sprite pour stocker nos lances
        self.all_lance = pygame.sprite.Group()

    def add_percent(self):
        self.percent += self.percent_speed / 100

    def is_full_loaded(self):
        return self.percent >= 100

    def reset_percent(self):
        self.percent = 0

    def lance_fall(self):
        # boucle pour les valeurs entre 1 et 10
        for i in range(1, 5):
            # apparaître une première boule de feu
            self.all_lance.add(Lance(self))

    def attempt_fall(self):
        # la jauge est totalement chargé
        if self.is_full_loaded():
            print("Pluie de flèches !!")
            self.lance_fall()
            self.reset_percent()

    def update_bar(self, surface):

        # ajouter du pourcentage à la barre
        self.add_percent()

        # Appel de la méthode pour essayer de déclancher la pluie
        self.attempt_fall()

        # barre noire en arrière plan
        pygame.draw.rect(surface, (0, 0, 0), [
            0, # axe des x
            surface.get_height() - 10, # axe des y
            surface.get_width(), # longueur de la fenêtre
            1 # épaisseur de la barre
        ])
        # barre rouge commme jauge d'évènement
        pygame.draw.rect(surface, (187, 11, 11), [
            0, # axe des x
            surface.get_height() - 10, # axe des y
            (surface.get_width() / 100) * self.percent, # longueur de la fenêtre
            1 # épaisseur de la barre
        ])