import pygame


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, speed, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect(center=(x, 0))
        self.speed = speed

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y