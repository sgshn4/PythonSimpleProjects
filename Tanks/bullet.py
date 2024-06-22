import pygame
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, width, height, start_x, start_y, angle, screen_w, screen_h):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)
        self.speed = 10
        self.angle = angle  # угол направления движения снаряда в градусах
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self):
        # Перевод угла направления в радианы
        radians = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(radians)
        self.rect.y -= self.speed * math.sin(radians)

        # Уничтожение снаряда, если он выходит за пределы экрана
        if self.rect.x < 0 or self.rect.x > self.screen_w or self.rect.y < 0 or self.rect.y > self.screen_h:
            self.kill()

