import pygame
import random
import math
import os
from settings import *
from utils import *
from world_elements import World, Kingdom, City
from entity import Entity


# --- ОВЕРЛЕИ ---

class Overlay:
    def __init__(self, title):
        self.active = False
        self.title = title
        self.scroll = [0, 0]

    def draw_base(self, screen, font):
        rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)
        pygame.draw.rect(screen, (15, 15, 25), rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2)
        screen.blit(font.render(f"{self.title} (ESC-Close, WASD-Scroll)", True, (255, 255, 255)), (70, 70))
        return rect


class KingdomStats(Overlay):
    def __init__(self):
        super().__init__("Kingdoms of the World")
        self.rects = {}  # kingdom_id -> Rect для клика

    def draw(self, screen, font, world):
        rect = self.draw_base(screen, font)
        self.rects = {}
        y = 120
        for kid, k in world.kingdoms.items():
            k_rect = pygame.Rect(rect.x + 50, rect.y + y + self.scroll[1], 400, 30)
            if rect.collidepoint(k_rect.centerx, k_rect.centery):
                pygame.draw.rect(screen, (30, 30, 45), k_rect)
                self.rects[kid] = k_rect
                txt = f"{k.name} | Pop: {k.pop_count} | Era: {k.era} (Click for Details)"
                screen.blit(font.render(txt, True, k.color), (k_rect.x + 10, k_rect.y + 5))
            y += 40


class KingdomDetail(Overlay):
    def __init__(self):
        super().__init__("Kingdom Details")
        self.k = None

    def draw(self, screen, font, world):
        if not self.k or self.k.id not in world.kingdoms:
            self.active = False
            return

        rect = self.draw_base(screen, font)
        k = world.kingdoms[self.k.id]

        passed_ticks = (pygame.time.get_ticks() - k.creation_tick) // 1000
        king_name = k.king.name if k.king else "Interregnum"
        city_names = [c.name for c in world.cities if c.kingdom_id == k.id]

        lines = [
            f"Official Name: {k.name}",
            f"Founder: {k.founder_full_name}",
            f"Current Monarch: {king_name}",
            f"Kingdom Age: {passed_ticks}s",
            f"Population: {k.pop_count} (Males: {k.males}, Females: {k.females})",
            f"Science: {int(k.science)}",
            f"Cities: {', '.join(city_names)}",
            "--- Diplomacy ---"
        ]

        for other_id, val in k.relations.items():
            if other_id in world.kingdoms:
                status = "WAR" if val <= RELATION_WAR else ("ALLY" if val >= RELATION_ALLY else "Neutral")
                lines.append(f"  vs {world.kingdoms[other_id].name}: {status} ({int(val)})")

        for i, l in enumerate(lines):
            screen.blit(font.render(l, True, (255, 255, 255)), (rect.x + 50, rect.y + 100 + i * 25 + self.scroll[1]))


class GenealogyTree(Overlay):
    def __init__(self):
        super().__init__("Family Tree")
        self.nodes = []

    def load(self, target_name):
        self.nodes = []
        if not os.path.exists(GENEALOGY_FILE): return
        raw = {}
        with open(GENEALOGY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 5: raw[p[0]] = p

        def build(name, x, y, depth):
            if name not in raw or depth > 4 or name == "Unknown": return None
            d = raw[name]
            node = {"name": name, "pos": (x, y), "sex": int(d[4]), "f": None, "m": None}
            self.nodes.append(node)
            node["f"] = build(d[1], x - 260 / (depth + 1), y + 100, depth + 1)
            node["m"] = build(d[2], x + 240 / (depth + 1), y + 100, depth + 1)
            return node

        build(target_name, (WIDTH - 100) // 2, 100, 0)

    def draw(self, screen, font):
        rect = self.draw_base(screen, font)
        for n in self.nodes:
            nx, ny = rect.x + n["pos"][0] + self.scroll[0], rect.y + n["pos"][1] + self.scroll[1]
            for pk in ["f", "m"]:
                if n[pk]:
                    px, py = rect.x + n[pk]["pos"][0] + self.scroll[0], rect.y + n[pk]["pos"][1] + self.scroll[1]
                    color = (100, 150, 255) if pk == "f" else (255, 150, 200)
                    pygame.draw.line(screen, color, (nx, ny), (px, py), 1)
        for n in self.nodes:
            nx, ny = rect.x + n["pos"][0] + self.scroll[0], rect.y + n["pos"][1] + self.scroll[1]
            if rect.collidepoint(nx, ny):
                col = (50, 120, 255) if n["sex"] == 0 else (255, 100, 200)
                pygame.draw.circle(screen, col, (int(nx), int(ny)), 8)
                txt = font.render(n["name"], True, (255, 255, 255))
                screen.blit(txt, (nx - txt.get_width() // 2, ny + 12))


# --- ГЛАВНЫЙ ЦИКЛ ---

def main():
    pygame.init()
    clear_genealogy()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont("Verdana", 13)
    world, clock = World(), pygame.time.Clock()
    sim_start = pygame.time.get_ticks()

    tree_ov = GenealogyTree()
    stats_ov = KingdomStats()
    detail_ov = KingdomDetail()

    time_scale = 1
    fullscreen = False
    entities = [Entity(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100),
                       (random.randint(80, 180), random.randint(80, 180), random.randint(80, 180)), age=40) for _ in
                range(60)]
    foods, selected_e, k_id_counter = [], None, 0

    while True:
        food_sectors = {}
        for f in foods:
            key = (f[0] // SECTOR_SIZE, f[1] // SECTOR_SIZE)
            if key not in food_sectors: food_sectors[key] = []
            food_sectors[key].append(f)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: time_scale = 1
                if event.key == pygame.K_2: time_scale = 2
                if event.key == pygame.K_3: time_scale = 5
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if fullscreen else 0)
                if event.key == pygame.K_ESCAPE: tree_ov.active = stats_ov.active = detail_ov.active = False
                if event.key == pygame.K_k:
                    if detail_ov.active:
                        detail_ov.active = False; stats_ov.active = True
                    else:
                        stats_ov.active = not stats_ov.active

                active = tree_ov if tree_ov.active else (
                    stats_ov if stats_ov.active else (detail_ov if detail_ov.active else None))
                if active:
                    if event.key == pygame.K_w: active.scroll[1] += 60
                    if event.key == pygame.K_s: active.scroll[1] -= 60
                    if event.key == pygame.K_a: active.scroll[0] += 60
                    if event.key == pygame.K_d: active.scroll[0] -= 60

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if stats_ov.active:
                    for kid, r in stats_ov.rects.items():
                        if r.collidepoint(mx, my):
                            detail_ov.k = world.kingdoms[kid]
                            detail_ov.active = True
                            stats_ov.active = False
                            break
                elif not tree_ov.active and not detail_ov.active:
                    if selected_e and 20 < mx < 120 and 210 < my < 235:
                        tree_ov.load(selected_e.name);
                        tree_ov.active = True;
                        tree_ov.scroll = [0, 0]
                    else:
                        selected_e = None
                        for e in entities:
                            if math.hypot(e.x - mx, e.y - my) < 15: selected_e = e; break

        if not tree_ov.active and not stats_ov.active and not detail_ov.active:
            screen.fill((0, 0, 0));
            screen.blit(world.bg_surface, (0, 0))
            if len(foods) < 400 and random.random() < 0.5: foods.append(
                [random.randint(20, WIDTH - 20), random.randint(20, HEIGHT - 20)])

            world.update_politics(time_scale)
            for k in world.kingdoms.values(): k.update_leader(entities, world); k.update_era()

            rem_cities = []
            for city in world.cities:
                if city.update(foods, entities, world, time_scale) == "keep":
                    rem_cities.append(city);
                    city.draw(screen, font)
            world.cities = rem_cities

            new_borns, dead_list = [], []
            for e in entities:
                if e.hunger > 100 or e.age > e.genes["max_age"] or e.health <= 0:
                    if e.kingdom_id is not None and world.kingdoms[e.kingdom_id].king == e:
                        world.log_event(f"The King {e.name} has passed away.", world.kingdoms[e.kingdom_id].color)
                    dead_list.append(e);
                    if e == selected_e: selected_e = None
                    continue

                e.move_logic(foods, entities, food_sectors, world, time_scale)

                if e.kingdom_id is None and e.personal_science > THRESHOLD_FOUNDING and k_id_counter < 10:
                    bright = mutate_color(e.color, e.color, True)
                    e.color = bright;
                    e.kingdom_id = k_id_counter;
                    e.heritage_id = k_id_counter;
                    e.hunger = 0
                    world.kingdoms[k_id_counter] = Kingdom(k_id_counter, bright, e.first_name, e.last_name,
                                                           pygame.time.get_ticks())
                    world.cities.append(City(e.x, e.y, k_id_counter, bright, generate_city_name(e.last_name)))
                    world.log_event(f"The {world.kingdoms[k_id_counter].name} was founded!", bright)
                    k_id_counter += 1

                if e.kingdom_id is not None:
                    k = world.kingdoms[e.kingdom_id]
                    k.science += e.genes["int"] * 0.015 * time_scale
                    thresh = THRESHOLD_CITY_BUILD * 0.6 if e.profession == "Explorer" else THRESHOLD_CITY_BUILD
                    if k.science - k.last_city_science > thresh:
                        if all(math.hypot(e.x - c.x, e.y - c.y) > 280 for c in world.cities):
                            c_name = generate_city_name(e.last_name)
                            world.cities.append(City(e.x, e.y, e.kingdom_id, e.color, c_name))
                            world.log_event(f"New City: {c_name} ({k.name})", e.color)
                            k.last_city_science = k.science

                if e.gender == 0 and e.age > 30 and e.reproduction_cooldown <= 0:
                    for p in entities:
                        if p.gender == 1 and p.age > 20 and p.reproduction_cooldown <= 0:
                            if math.hypot(e.x - p.x, e.y - p.y) < 15:
                                e.reproduction_cooldown = p.reproduction_cooldown = 70 * FPS
                                e.hunger += 40;
                                p.hunger += 40
                                cg = random.randint(0, 1)
                                cf, _ = generate_russian_name(cg)
                                cl = inherit_surname(e.last_name, p.last_name, cg)
                                baby = Entity(e.x, e.y, mutate_color(e.color, p.color),
                                              kingdom_id=p.kingdom_id, gender=cg,
                                              first_name=cf, last_name=cl, gen_count=max(e.gen_count, p.gen_count) + 1,
                                              parents=(e.name, p.name), heritage=e.kingdom_id)
                                new_borns.append(baby);
                                break

                if e.target and len(e.target) > 2 and e.target[2] == "food":
                    for f in foods:
                        if abs(f[0] - e.target[0]) < 3 and abs(f[1] - e.target[1]) < 3:
                            foods.remove(f);
                            e.hunger = max(0, e.hunger - 85);
                            break
                e.draw(screen, (e == selected_e))

            for d in dead_list: entities.remove(d)
            entities.extend(new_borns);
            world.cleanup_kingdoms()
            for f in foods: pygame.draw.circle(screen, (160, 160, 0), (int(f[0]), int(f[1])), 2)

            # UI
            passed = (pygame.time.get_ticks() - sim_start) // 1000
            pygame.draw.rect(screen, (20, 20, 30), (WIDTH // 2 - 160, 5, 330, 25))
            screen.blit(
                font.render(f"Time: {passed}s | Pop: {len(entities)} | Speed: x{time_scale}", True, (200, 255, 200)),
                (WIDTH // 2 - 150, 8))
            world.draw_messages(screen, font)

            if selected_e:
                rect = pygame.Rect(10, 10, 260, 250)
                pygame.draw.rect(screen, (15, 15, 25), rect);
                pygame.draw.rect(screen, selected_e.color, rect, 1)
                k_name = world.kingdoms[
                    selected_e.kingdom_id].name if selected_e.kingdom_id in world.kingdoms else "Wild"
                h_obj = world.kingdoms.get(selected_e.heritage_id)
                h_name = h_obj.founder_full_name if h_obj else "Unknown"
                lines = [f"Name: {selected_e.name}", f"Kingdom: {k_name}", f"Bloodline: {h_name}",
                         f"Loyalty: {int(selected_e.loyalty)}%", f"Job: {selected_e.profession}",
                         f"Age: {int(selected_e.age)}s / {int(selected_e.genes['max_age'])}",
                         f"Gen: {selected_e.gen_count}"]
                for i, l in enumerate(lines): screen.blit(font.render(l, True, (255, 255, 255)), (20, 20 + i * 18))
                pygame.draw.rect(screen, (50, 50, 100), (20, 210, 100, 25))
                screen.blit(font.render("Show Family", True, (255, 255, 255)), (28, 215))

        if tree_ov.active: tree_ov.draw(screen, font)
        if stats_ov.active: stats_ov.draw(screen, font, world)
        if detail_ov.active: detail_ov.draw(screen, font, world)
        pygame.display.flip();
        clock.tick(FPS)


if __name__ == "__main__": main()