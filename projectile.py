import pygame

# Définir la classe qui va gérer le projectile
class Projectile(pygame.sprite.Sprite):

    # Définir le constructeur de cette classe
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.velocity = 15
        self.image = pygame.image.load('assets/bulles.png')
        self.image = pygame.transform.scale(self.image, (40,40))
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x + 90
        self.rect.y = player.rect.y + 25
        self.origin_image = self.image
        self.angle = 0

    # Rotation des projectiles
    def rotate(self):
        self.angle += 7
        self.image = pygame.transform.rotozoom(self.origin_image, self.angle, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

    def remove(self):
        self.player.all_projectile.remove(self)

    def move(self):
        self.rect.x += self.velocity
        self.rotate()

        # Vérifier si le projectile entre en colliqion avec un obstacle
        for obstacle in self.player.game.check_collision(self, self.player.game.all_obstacle):
            # Supprimer le projectile
            self.remove()
            # Infliger des dégats
            obstacle.damage(self.player.attack)
        if self.player.game.check_collision(self, self.player.game.all_obstacle):
            self.remove()

        # Vérifier si notre projectile n'est plus présent sur l'écran
        if self.rect.x > 961:
            # Supprimer le projectile  de l'écran
            self.remove()

