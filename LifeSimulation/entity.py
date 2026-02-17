import pygame
import random
import math
from settings import *
from utils import generate_russian_name, save_to_genealogy


class Entity:
    def __init__(self, x, y, color, kingdom_id=None, genes=None, age=0, gen_count=1,
                 parents=("Unknown", "Unknown"), heritage=None, first_name=None,
                 last_name=None, gender=None):

        self.gender = gender if gender is not None else random.randint(0, 1)
        f_gen, l_gen = generate_russian_name(self.gender)
        self.first_name = first_name if first_name else f_gen
        self.last_name = last_name if last_name else l_gen
        self.name = f"{self.first_name} {self.last_name}"

        self.x, self.y = x, y
        self.color = color
        self.kingdom_id = kingdom_id
        self.heritage_id = heritage if heritage is not None else kingdom_id
        self.parents = parents
        self.profession = random.choice(["Farmer", "Scientist", "Warrior", "Explorer"])
        self.loyalty = 100

        save_to_genealogy(self.name, parents[0], parents[1], gen_count, self.gender)

        self.genes = genes if genes else {
            "sp": random.uniform(1.6, 2.8),
            "int": random.random(),
            "max_age": random.uniform(200, 400)
        }

        self.health = 100
        self.hunger = 10
        self.age = age
        self.gen_count = gen_count
        self.personal_science = 0
        self.target = None
        self.decision_cooldown = 0
        self.reproduction_cooldown = 0

    def move_logic(self, foods, entities, food_sectors, world, time_scale):
        self.age += (1 / FPS) * time_scale
        self.hunger += (0.025 + (self.genes["sp"] * 0.01)) * time_scale
        if self.reproduction_cooldown > 0: self.reproduction_cooldown -= 1 * time_scale

        if self.kingdom_id is None:
            for city in world.cities:
                if math.hypot(self.x - city.x, self.y - city.y) < CITY_JOIN_RADIUS:
                    self.kingdom_id = city.kingdom_id
                    self.color = city.color
                    world.log_event(f"{self.name} joined {world.kingdoms[self.kingdom_id].name}", self.color)
                    break

        self.decision_cooldown -= 1 * time_scale
        if self.decision_cooldown <= 0:
            self.decision_cooldown = random.randint(30, 60)
            self.target = None

            # 0. Самооборона/Война
            if self.kingdom_id is not None:
                enemies = [e for e in entities if e.kingdom_id is not None and e.kingdom_id != self.kingdom_id]
                for enemy in enemies:
                    rel = world.kingdoms[self.kingdom_id].relations.get(enemy.kingdom_id, 0)
                    if rel <= RELATION_WAR and math.hypot(self.x - enemy.x, self.y - enemy.y) < 200:
                        if self.profession == "Warrior":
                            self.target = [enemy.x, enemy.y, "attack", enemy]
                        else:
                            self.target = [self.x + (self.x - enemy.x), self.y + (self.y - enemy.y), "flee"]
                        break

            # 1. Еда
            if self.target is None and self.hunger > 30:
                sx, sy = int(self.x // SECTOR_SIZE), int(self.y // SECTOR_SIZE)
                best_d = 1000
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        key = (sx + dx, sy + dy)
                        if key in food_sectors:
                            for f in food_sectors[key]:
                                d = math.hypot(f[0] - self.x, f[1] - self.y)
                                if d < best_d: best_d, self.target = d, [f[0], f[1], "food"]

            # 2. Размножение
            elif self.target is None and self.age > 25 and self.reproduction_cooldown <= 0:
                partners = [p for p in entities if
                            p.gender != self.gender and p.age > 20 and p.reproduction_cooldown <= 0]
                if self.kingdom_id is not None: partners = [p for p in partners if p.kingdom_id == self.kingdom_id]
                if partners:
                    p = min(partners, key=lambda x: math.hypot(x.x - self.x, x.y - self.y))
                    if math.hypot(p.x - self.x, p.y - self.y) < 300: self.target = [p.x, p.y, "partner"]

            # 3. Город
            if self.target is None:
                if self.kingdom_id is not None:
                    my_cities = [c for c in world.cities if c.kingdom_id == self.kingdom_id]
                    if my_cities:
                        home = min(my_cities, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))
                        if math.hypot(home.x - self.x, home.y - self.y) > 150:
                            self.target = [home.x + random.randint(-40, 40), home.y + random.randint(-40, 40), "home"]
                        elif self.profession == "Explorer" and random.random() < 0.3:
                            self.target = [random.randint(0, WIDTH), random.randint(0, HEIGHT), "explore"]
                else:
                    visible = [c for c in world.cities if math.hypot(c.x - self.x, c.y - self.y) < CITY_VISION_RADIUS]
                    if visible:
                        c = min(visible, key=lambda city: math.hypot(city.x - self.x, city.y - self.y))
                        self.target = [c.x + random.randint(-50, 50), c.y + random.randint(-50, 50), "migration"]

        if self.target:
            dx, dy = self.target[0] - self.x, self.target[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 5:
                self.x += (dx / dist) * self.genes["sp"] * time_scale
                self.y += (dy / dist) * self.genes["sp"] * time_scale
                if len(self.target) > 3 and self.target[2] == "attack":
                    if dist < 15: self.target[3].health -= (2.0 if self.profession == "Warrior" else 0.5) * time_scale
            else:
                self.target = None
        else:
            self.x += random.uniform(-1, 1) * self.genes["sp"] * time_scale
            self.y += random.uniform(-1, 1) * self.genes["sp"] * time_scale

        self.x = max(10, min(WIDTH - 10, self.x))
        self.y = max(10, min(HEIGHT - 10, self.y))
        self.personal_science += self.genes["int"] * 0.15 * time_scale
        if random.random() < 0.05: world.update_tile(self.x, self.y, self.color, 'path')

    def draw(self, screen, is_selected=False):
        size = 2 + min(4, int(self.age / 8))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
        if self.profession == "Warrior": pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), size + 2,
                                                            1)
        if self.gender == 0:
            pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 1)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), size + 1, 1)
        if is_selected: pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), size + 5, 1)