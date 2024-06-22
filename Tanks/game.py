import pygame
import sys
import point
import ball
import utils

# Инициализация Pygame
pygame.init()

# Размеры окна игры
WIDTH, HEIGHT = 800, 600

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (165, 42, 42)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Minecraft")

# Размеры блоков и мира
BLOCK_SIZE = 30
GRID_WIDTH = WIDTH // BLOCK_SIZE
GRID_HEIGHT = HEIGHT // BLOCK_SIZE
map = []
map.append(point.Point(0, 100, GREEN))

x = 0
y = 0
speed = 1
b1 = ball.Ball(WIDTH // 2, speed, utils.PATH_RES + 'bottle.png')

def draw_screen():
    for i in map:
        pos_x = i.x - x
        pos_y = i.y - y
        b1.update(pos_x, pos_y)
        pygame.draw.rect(screen, i.block, (pos_x, pos_y, 30, 30))
    pygame.display.update()


# Основной игровой цикл
def main():
    global x, y
    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    # Получаем координаты клика и преобразуем их в координаты сетки
                    i, j = event.pos

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_s]:
            y += 1
        if keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_d]:
            x += 1

        # Отрисовка фона
        screen.fill(BLUE)
        screen.blit(b1.image, b1.rect)

        pygame.display.update()


        # Отрисовка сетки мира
        draw_screen()
        # Обновление экрана
        pygame.display.flip()


if __name__ == "__main__":
    main()
