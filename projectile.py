import pygame


class Projectile(pygame.sprite.Sprite):
    frames = None

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.velocity = 900.0
        if Projectile.frames is None:
            source = pygame.image.load("assets/bulles.png").convert_alpha()
            source = pygame.transform.smoothscale(source, (36, 36))
            Projectile.frames = []
            for angle in range(0, 360, 10):
                frame = pygame.transform.rotozoom(source, angle, 1)
                Projectile.frames.append((frame, pygame.mask.from_surface(frame)))
        self.angle = 0.0
        self.image, self.mask = Projectile.frames[0]
        self.rect = self.image.get_rect(center=(player.rect.right + 12, player.rect.centery))
        self.position = pygame.Vector2(self.rect.center)

    def remove(self):
        self.kill()

    def move(self, dt=1 / 60):
        self.position.x += self.velocity * dt
        self.angle = (self.angle + 420 * dt) % 360
        self.image, self.mask = Projectile.frames[int(self.angle // 10)]
        self.rect = self.image.get_rect(center=(round(self.position.x), round(self.position.y)))
        for obstacle in self.player.game.check_collision(self, self.player.game.all_obstacle):
            self.kill()
            obstacle.damage(self.player.attack)
            break
        if self.rect.left > self.player.game.WIDTH:
            self.kill()
