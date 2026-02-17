import pygame
import random
import math
from settings import *
from utils import generate_city_name, generate_kingdom_name


class City:
    def __init__(self, x, y, kingdom_id, color):
        self.x, self.y = x, y
        self.kingdom_id = kingdom_id
        self.color = color
        self.name = generate_city_name()
        self.mayor = None
        self.food_timer = 0

    def update(self, foods, entities, world):
        self.food_timer += 1
        if self.food_timer > FPS * 5:
            self.food_timer = 0
            if len(foods) < 400:
                rx = self.x + random.randint(-40, 40)
                ry = self.y + random.randint(-40, 40)
                foods.append([rx, ry])

        # Король не может быть мэром
        king = world.kingdoms[self.kingdom_id].king
        local_entities = [e for e in entities if
                          e.kingdom_id == self.kingdom_id and e != king and math.hypot(e.x - self.x,
                                                                                       e.y - self.y) < 100]
        if local_entities:
            self.mayor = max(local_entities, key=lambda e: e.personal_science)
        else:
            self.mayor = None

    def draw(self, screen, font):
        rect = pygame.Rect(self.x - 12, self.y - 12, 24, 24)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1)
        name_surf = font.render(self.name, True, (200, 200, 200))
        screen.blit(name_surf, (self.x - name_surf.get_width() // 2, self.y + 15))


class Kingdom:
    def __init__(self, kingdom_id, color, founder_name):
        self.id = kingdom_id
        self.color = color
        self.founder_name = founder_name
        self.name = generate_kingdom_name(founder_name)
        self.king = None
        self.science = 0
        self.era = 0
        self.pop_count = 0
        self.last_city_science = 0
        self.avg_speed = 0
        self.avg_int = 0

    def update_leader(self, entities):
        civ_members = [e for e in entities if e.kingdom_id == self.id]
        if civ_members:
            self.king = max(civ_members, key=lambda e: e.personal_science)
            # Заодно считаем статистику
            self.avg_speed = sum(e.genes['sp'] for e in civ_members) / len(civ_members)
            self.avg_int = sum(e.genes['int'] for e in civ_members) / len(civ_members)
            self.pop_count = len(civ_members)
        else:
            self.king = None
            self.pop_count = 0

    def update_era(self):
        if self.science > THRESHOLD_ERA_1 and self.era == 0:
            self.era = 1


class World:
    def __init__(self):
        self.grid = {}
        self.bg_surface = pygame.Surface((WIDTH, HEIGHT))
        self.bg_surface.fill((5, 5, 8))
        self.kingdoms = {}
        self.cities = []
        self.is_extinct = False

    def update_tile(self, x, y, color, t_type='path'):
        tx, ty = int(x // GRID_SIZE), int(y // GRID_SIZE)
        key = (tx, ty)
        if key not in self.grid: self.grid[key] = {'f': 0, 'p': 0}
        if t_type == 'path':
            self.grid[key]['p'] = min(40, self.grid[key]['p'] + 1)
        else:
            self.grid[key]['f'] = min(50, self.grid[key]['f'] + 2)
        pygame.draw.rect(self.bg_surface, (color[0] // 6, color[1] // 6, color[2] // 6),
                         (tx * GRID_SIZE, ty * GRID_SIZE, GRID_SIZE, GRID_SIZE))