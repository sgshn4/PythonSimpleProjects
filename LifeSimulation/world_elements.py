import pygame
import random
import math
from settings import *
from utils import generate_city_name, generate_kingdom_name


class City:
    def __init__(self, x, y, kingdom_id, color, name):
        self.x, self.y = x, y
        self.kingdom_id = kingdom_id
        self.color = color
        self.name = name
        self.mayor = None
        self.food_timer = 0
        self.is_abandoned = False
        self.ghost_timer = 0

    def update(self, foods, entities, world, time_scale):
        self.food_timer += 1 * time_scale
        local_members = [e for e in entities if
                         e.kingdom_id == self.kingdom_id and math.hypot(e.x - self.x, e.y - self.y) < 200]

        if len(local_members) == 0:
            self.ghost_timer += 1 * time_scale
            if self.ghost_timer > FPS * 10:
                self.is_abandoned = True
        else:
            self.is_abandoned = False
            self.ghost_timer = 0

        if self.is_abandoned:
            if random.random() < 0.005 * time_scale:
                return "destroy"
            for e in entities:
                if e.kingdom_id is not None and math.hypot(e.x - self.x, e.y - self.y) < 40:
                    self.kingdom_id = e.kingdom_id
                    self.color = e.color
                    self.is_abandoned = False
                    self.ghost_timer = 0
                    break
        else:
            if self.food_timer > FPS * 4:
                self.food_timer = 0
                if len(foods) < 800:
                    foods.append([self.x + random.randint(-60, 60), self.y + random.randint(-60, 60)])

            king = world.kingdoms[self.kingdom_id].king
            eligible = [e for e in local_members if e != king]
            if eligible:
                self.mayor = max(eligible, key=lambda e: e.personal_science)
            else:
                self.mayor = None
        return "keep"

    def draw(self, screen, font):
        c = (60, 60, 60) if self.is_abandoned else self.color
        pygame.draw.rect(screen, c, (self.x - 15, self.y - 15, 30, 30))
        pygame.draw.rect(screen, (200, 200, 200), (self.x - 15, self.y - 15, 30, 30), 1)
        txt = font.render(self.name, True, (255, 255, 255))
        screen.blit(txt, (self.x - txt.get_width() // 2, self.y + 18))


class Kingdom:
    def __init__(self, kingdom_id, color, founder_name, founder_surname, start_time):
        self.id = kingdom_id
        self.color = color
        self.founder_full_name = f"{founder_name} {founder_surname}"
        self.name = generate_kingdom_name(founder_surname)
        self.king = None
        self.science = 0
        self.era = 0
        self.pop_count = 0
        self.males = 0
        self.females = 0
        self.creation_tick = start_time
        self.last_city_science = 0
        self.relations = {}

    def update_leader(self, entities, world):
        members = [e for e in entities if e.kingdom_id == self.id]
        self.pop_count = len(members)
        self.males = len([e for e in members if e.gender == 0])
        self.females = self.pop_count - self.males

        old_king = self.king
        if members:
            self.king = max(members, key=lambda e: e.personal_science)
            if old_king and old_king != self.king:
                world.log_event(f"Coronation: {self.king.name} is the new King of {self.name}", self.color)
        else:
            self.king = None

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
        self.messages = []  # Список [(text, color, time_expire), ...]

    def log_event(self, text, color=(255, 255, 255)):
        expire = pygame.time.get_ticks() + (MSG_DURATION * 1000)
        self.messages.append([text, color, expire])
        if len(self.messages) > MSG_MAX_COUNT:
            self.messages.pop(0)

    def draw_messages(self, screen, font):
        now = pygame.time.get_ticks()
        self.messages = [m for m in self.messages if m[2] > now]
        for i, (text, color, expire) in enumerate(self.messages):
            # Эффект затухания
            alpha = min(255, (expire - now) // 10)
            s = font.render(text, True, color)
            s.set_alpha(alpha)
            screen.blit(s, (20, HEIGHT - 40 - i * 25))

    def update_politics(self, time_scale):
        kids = list(self.kingdoms.keys())
        for i in range(len(kids)):
            for j in range(i + 1, len(kids)):
                id1, id2 = kids[i], kids[j]
                if id2 not in self.kingdoms[id1].relations:
                    self.kingdoms[id1].relations[id2] = 0
                    self.kingdoms[id2].relations[id1] = 0

                old_rel = self.kingdoms[id1].relations[id2]
                # Дрейф
                if self.kingdoms[id1].relations[id2] > 0: self.kingdoms[id1].relations[id2] -= 0.005 * time_scale
                if self.kingdoms[id1].relations[id2] < 0: self.kingdoms[id1].relations[id2] += 0.005 * time_scale

                # Близость городов портит отношения
                for c1 in [c for c in self.cities if c.kingdom_id == id1]:
                    for c2 in [c for c in self.cities if c.kingdom_id == id2]:
                        if math.hypot(c1.x - c2.x, c1.y - c2.y) < 350:
                            self.kingdoms[id1].relations[id2] -= 0.03 * time_scale

                new_rel = self.kingdoms[id1].relations[id2]
                self.kingdoms[id2].relations[id1] = new_rel

                # Лог начала войны
                if old_rel > RELATION_WAR and new_rel <= RELATION_WAR:
                    self.log_event(f"WAR: {self.kingdoms[id1].name} vs {self.kingdoms[id2].name}!", (255, 50, 50))

    def update_tile(self, x, y, color, t_type='path'):
        tx, ty = int(x // GRID_SIZE), int(y // GRID_SIZE)
        key = (tx, ty)
        if key not in self.grid: self.grid[key] = {'f': 0, 'p': 0}
        if t_type == 'path':
            self.grid[key]['p'] = min(40, self.grid[key]['p'] + 1)
        else:
            self.grid[key]['f'] = min(50, self.grid[key]['f'] + 2)
        pygame.draw.rect(self.bg_surface, (color[0] // 8, color[1] // 8, color[2] // 8),
                         (tx * GRID_SIZE, ty * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def cleanup_kingdoms(self):
        to_delete = []
        for kid, k in self.kingdoms.items():
            has_cities = any(c.kingdom_id == kid for c in self.cities)
            if k.pop_count == 0 and not has_cities:
                to_delete.append(kid)
        for kid in to_delete:
            self.log_event(f"The {self.kingdoms[kid].name} has fallen...", (150, 150, 150))
            del self.kingdoms[kid]