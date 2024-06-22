import pygame
import sys
import point
import ball
import utils
import tank

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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Minecraft")

map = []

x = 0
y = 0
speed = 1
b1 = ball.Ball(WIDTH // 2, speed, utils.PATH_RES + 'bottle.png')

player = tank.Tank(WC, HC, 60, 110, GREEN, 1, 1, utils.PATH_RES + 'base.png',
                   utils.PATH_RES + 'turret.png')
map.append(b1)
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()


def draw_screen():
    for i in map:
        i.update(x, y)
    player.draw(screen)
    pygame.display.update()

# Основной игровой цикл
def main():
    global x, y
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
                    all_sprites.add(player.shoot())
                    bullets.add(player.shoot())

        # Управление автомобилем с клавиатуры
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and keys[pygame.K_s]:
            player.turn_right()
            x += player.moveX(-1)
            y -= player.moveY(-1)
        elif keys[pygame.K_d] and keys[pygame.K_s]:
            player.turn_left()
            x += player.moveX(-1)
            y -= player.moveY(-1)
        else:
            if keys[pygame.K_a]:
                player.turn_left()
            if keys[pygame.K_d]:
                player.turn_right()
            if keys[pygame.K_w]:
                x += player.moveX(1)
                y -= player.moveY(1)
            if keys[pygame.K_s]:
                x += player.moveX(-1)
                y -= player.moveY(-1)


        # Отрисовка фона
        screen.fill(BLUE)
        screen.blit(b1.image, b1.rect)

        bullets.update()
        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.update()
        draw_screen()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
