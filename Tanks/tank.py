import pygame
import math
import colors
import bullet as bt
import aimer


class Tank():
    def __init__(self, x, y, width, height, color, max_speed, angle_speed, base_path, turret_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 0
        self.max_speed = max_speed
        self.angle_speed = angle_speed
        self.angle = 0
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.turret_angle = 0
        self.cannon_angle = 0

        self.car_image = pygame.image.load(base_path).convert_alpha()
        self.turret_image = pygame.image.load(turret_path).convert_alpha()

    def draw(self, screen):
        rotated_car = pygame.transform.rotate(self.car_image, self.angle)
        rotated_rect = rotated_car.get_rect(center=(self.x, self.y))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (self.x)
        dy = mouse_y - (self.y)
        self.turret_angle = math.degrees(math.atan2(dy, -dx)) + self.angle
        self.cannon_angle = (180 / math.pi) * -math.atan2(dy, dx) + self.angle
        screen.blit(rotated_car, rotated_rect)

        rotated_turret = pygame.transform.rotate(self.turret_image, self.turret_angle)
        turret_rect = rotated_turret.get_rect()
        turret_rect.center = (self.x, self.y)
        screen.blit(rotated_turret, turret_rect.topleft)

    def moveX(self, dir):
        self.speed = self.max_speed * dir
        return self.speed * math.cos(math.radians(self.angle))

    def moveY(self, dir):
        self.speed = self.max_speed * dir
        return  self.speed * math.sin(math.radians(self.angle))

    def turn_left(self):
        self.angle += self.angle_speed
        if self.angle >= 360:
            self.angle -= 360

    def turn_right(self):
        self.angle -= self.angle_speed
        if self.angle < 0:
            self.angle += 360

    def shoot(self):
        # Определение точки выстрела (кончика ствола башни)
        turret_end_x = self.x + math.cos(math.radians(self.turret_angle)) * 30
        turret_end_y = self.y - math.sin(math.radians(self.turret_angle)) * 30

        # Создание снаряда и добавление его в группу снарядов
        bullet = bt.Bullet(colors.WHITE, 10, 10, turret_end_x, turret_end_y, self.cannon_angle, 1000, 1000)
        return bullet