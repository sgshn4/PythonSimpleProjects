import pygame
import serial
import time
import sys
from collections import deque

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ArduinoSnake")
clock = pygame.time.Clock()

try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
except serial.SerialException:
    print("Arduino not connected. Starting with keyboard...")
    arduino = None


class Snake:
    def __init__(self):
        self.positions = deque([(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.game_over = False

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        if self.game_over:
            return

        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        if new_head in self.positions:
            self.game_over = True
        else:
            self.positions.appendleft(new_head)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.positions = deque([(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.game_over = False

    def render(self, surface):
        for p in self.positions:
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, GREEN, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BLACK, rect, 1)


def get_joystick_direction(x, y):
    deadzone = 100

    if x < 512 - deadzone:
        return (-1, 0)
    elif x > 512 + deadzone:
        return (1, 0)
    elif y < 512 - deadzone:
        return (0, -1)
    elif y > 512 + deadzone:
        return (0, 1)
    else:
        return None


def main():
    snake = Snake()
    food = Food()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if snake.game_over and event.key == pygame.K_SPACE:
                    snake.reset()

        if arduino and arduino.in_waiting > 0:
            try:
                data = arduino.readline().decode('utf-8').strip().split(',')
                if len(data) == 3:
                    x, y, button = map(int, data)
                    if button == 0 and snake.game_over:
                        snake.reset()
                    new_dir = get_joystick_direction(x, y)
                    if new_dir:
                        if (new_dir[0] * -1, new_dir[1] * -1) != snake.direction:
                            snake.direction = new_dir
            except:
                pass

        if not arduino:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and snake.direction != (0, 1):
                snake.direction = (0, -1)
            elif keys[pygame.K_DOWN] and snake.direction != (0, -1):
                snake.direction = (0, 1)
            elif keys[pygame.K_LEFT] and snake.direction != (1, 0):
                snake.direction = (-1, 0)
            elif keys[pygame.K_RIGHT] and snake.direction != (-1, 0):
                snake.direction = (1, 0)

        if not snake.game_over:
            snake.update()

            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 1
                food.randomize_position()
                while food.position in snake.positions:
                    food.randomize_position()

        screen.fill(WHITE)
        draw_grid(screen)
        snake.render(screen)
        food.render(screen)
        font = pygame.font.SysFont('Arial', 20)
        score_text = font.render(f'Score: {snake.score}', True, BLACK)
        screen.blit(score_text, (10, 10))
        if snake.game_over:
            font = pygame.font.SysFont('Arial', 36)
            game_over_text = font.render('Game over', True, RED)
            restart_text = font.render('Press Space', True, BLACK)
            screen.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - 180, HEIGHT // 2 + 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    if arduino:
        arduino.close()
    sys.exit()


if __name__ == "__main__":
    import random

    main()
