import pygame
import random
import math
from settings import *
from utils import generate_name


class Entity:
    def __init__(self, x, y, color, kingdom_id=None, genes=None, age=0, gen_count=1, parents=("None", "None")):
        self.name = generate_name()
        self.gender = random.randint(0, 1)
        self.x, self.y = x, y
        self.color = color
        self.kingdom_id = kingdom_id
        self.parents = parents  # Список из двух имен

        if genes:
            self.genes = {
                "sp": max(1.0, genes["sp"] + random.uniform(-0.1, 0.1)),
                "int": max(0.1, genes["int"] + random.uniform(-0.05, 0.05)),
                "max_age": max(60, genes["max_age"] + random.uniform(-10, 10))
            }
        else:
            self.genes = {"sp": random.uniform(1.3, 2.7), "int": random.random(), "max_age": random.uniform(150, 250)}

        self.hunger = 20
        self.age = age
        self.gen_count = gen_count
        self.personal_science = 0
        self.target = None
        self.decision_cooldown = random.randint(0, 20)
        self.reproduction_cooldown = 0

    def move_logic(self, foods, entities, food_sectors, world):
        self.age += 1 / FPS
        eff = 1.0
        if self.kingdom_id is not None and self.kingdom_id in world.kingdoms:
            if world.kingdoms[self.kingdom_id].era == 1: eff = 0.75
        self.hunger += (0.05 + (self.genes["sp"] * 0.01)) * eff
        if self.reproduction_cooldown > 0: self.reproduction_cooldown -= 1

        if self.kingdom_id is None:
            for city in world.cities:
                if math.hypot(self.x - city.x, self.y - city.y) < CITY_JOIN_RADIUS:
                    self.kingdom_id = city.kingdom_id
                    self.color = city.color
                    break

        self.decision_cooldown -= 1
        if self.decision_cooldown <= 0:
            self.decision_cooldown = 30
            self.target = None
            if self.hunger > 35:
                sx, sy = int(self.x // SECTOR_SIZE), int(self.y // SECTOR_SIZE)
                best_d = 800
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        key = (sx + dx, sy + dy)
                        if key in food_sectors:
                            for f in food_sectors[key]:
                                d = math.hypot(f[0] - self.x, f[1] - self.y)
                                if d < best_d: best_d, self.target = d, f
            elif self.age > 30 and self.reproduction_cooldown <= 0:
                partners = [p for p in entities if p.kingdom_id == self.kingdom_id
                            and p.gender != self.gender and p.age > 30 and p.reproduction_cooldown <= 0]
                if partners:
                    p = min(partners, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
                    if math.hypot(p.x - self.x, p.y - self.y) < 200: self.target = p

        if self.target:
            tx, ty = (self.target.x, self.target.y) if isinstance(self.target, Entity) else (self.target[0],
                                                                                             self.target[1])
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 8:
                if isinstance(self.target, list):
                    if self.target in foods:
                        foods.remove(self.target)
                        self.hunger = max(0, self.hunger - 75)
                        world.update_tile(self.x, self.y, self.color, 'fert')
                    self.target = None
            else:
                self.x += (dx / dist) * self.genes["sp"]
                self.y += (dy / dist) * self.genes["sp"]
        else:
            self.x += random.uniform(-0.5, 0.5) * self.genes["sp"]
            self.y += random.uniform(-0.5, 0.5) * self.genes["sp"]

        self.x = max(10, min(WIDTH - 10, self.x))
        self.y = max(10, min(HEIGHT - 10, self.y))
        self.personal_science += self.genes["int"] * 0.06
        if random.random() < 0.05: world.update_tile(self.x, self.y, self.color, 'path')

    def draw(self, screen, is_selected=False):
        size = 3 if self.age < 15 else 5
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
        if self.gender == 0:
            pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 1)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), size + 1, 1)
        if is_selected: pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), size + 5, 1)