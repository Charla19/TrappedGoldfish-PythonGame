import pygame


class SoundManager:
    _sounds = None
    _mixer = None

    def __init__(self):
        # One set of decoded samples per mixer lifetime, never per enemy or shot.
        if SoundManager._sounds is None or SoundManager._mixer != pygame.mixer.get_init():
            SoundManager._mixer = pygame.mixer.get_init()
            if SoundManager._mixer:
                SoundManager._sounds = {
                    "click": pygame.mixer.Sound("assets/sounds/click.wav"),
                    "game_over": pygame.mixer.Sound("assets/sounds/go.wav"),
                    "projectile": pygame.mixer.Sound("assets/sounds/tir.wav"),
                }
                for name, sound in SoundManager._sounds.items():
                    sound.set_volume(0.22 if name == "projectile" else 0.4)

    def play(self, name):
        if pygame.mixer.get_init() and SoundManager._sounds:
            sound = SoundManager._sounds.get(name)
            if sound:
                sound.play()
