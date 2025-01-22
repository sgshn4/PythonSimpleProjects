import pygame
import sys
import point
import ball
import utils
import tank
import colors

class Game():
    def __init__(self):
        # Инициализация Pygame
        pygame.init()

        # Размеры окна игры
        WIDTH, HEIGHT = 800, 600
        WC = WIDTH / 2
        HC = HEIGHT / 2

        # Цвета
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (0, 0, 255)
        GREEN = (0, 255, 0)
        BROWN = (165, 42, 42)

        # Создание окна
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pygame Minecraft")

        self.map = []

        self.x = 0
        self.y = 0
        speed = 1
        self.b1 = ball.Ball(WIDTH // 2, speed, utils.PATH_RES + 'bottle.png')

        self.player = tank.Tank(WC, HC, 60, 110, GREEN, 1, 1, utils.PATH_RES + 'base.png',
                           utils.PATH_RES + 'turret.png')
        self.map.append(self.b1)
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.main()

    def draw_screen(self):
        for i in self.map:
            i.update(self.x, self.y)
        self.player.draw(self.screen)
        pygame.display.update()

    # Основной игровой цикл
    def main(self):
        clock = pygame.time.Clock()
        while True:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Выстрел игрока
                        self.all_sprites.add(self.player.shoot())
                        self.bullets.add(self.player.shoot())

            # Управление автомобилем с клавиатуры
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and keys[pygame.K_s]:
                self.player.turn_right()
                self.x += self.player.moveX(-1)
                self.y -= self.player.moveY(-1)
            elif keys[pygame.K_d] and keys[pygame.K_s]:
                self.player.turn_left()
                self.x += self.player.moveX(-1)
                self.y -= self.player.moveY(-1)
            else:
                if keys[pygame.K_a]:
                    self.player.turn_left()
                if keys[pygame.K_d]:
                    self.player.turn_right()
                if keys[pygame.K_w]:
                    self.x += self.player.moveX(1)
                    self.y -= self.player.moveY(1)
                if keys[pygame.K_s]:
                    self.x += self.player.moveX(-1)
                    self.y -= self.player.moveY(-1)


            # Отрисовка фона
            self.screen.fill(colors.BLUE)
            self.screen.blit(self.b1.image, self.b1.rect)

            self.bullets.update()
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)

            pygame.display.update()
            self.draw_screen()
            pygame.display.flip()
            clock.tick(30)


if __name__ == "__main__":
    game = Game()
