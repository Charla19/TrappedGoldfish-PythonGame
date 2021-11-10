import pygame

class SoundManager:

    def __init__(self):
        self.sounds = {
            'click': pygame.mixer.Sound('assets/sounds/click.wav'),
            'game_over': pygame.mixer.Sound('assets/sounds/go.wav'),
            'fond_marin': pygame.mixer.Sound('assets/sounds/bound.wav'),
            'projectile': pygame.mixer.Sound('assets/sounds/tir.wav'),
        }

    def play(self, name):
        self.sounds[name].play()