import pygame
import random
import math
from settings import *
from utils import mutate_color, generate_name
from world_elements import World, Kingdom, City
from entity import Entity


def main():
    pygame.init()
    # Изначально оконный режим
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("A-Life: Era of Kingdoms (Press 'F' for Fullscreen)")

    font = pygame.font.SysFont("Verdana", 13)
    title_font = pygame.font.SysFont("Verdana", 14, bold=True)
    big_font = pygame.font.SysFont("Verdana", 60, bold=True)

    world = World()
    clock = pygame.time.Clock()
    fullscreen = False

    # Стартовая популяция диких (серых)
    entities = [Entity(random.randint(100, 1000), random.randint(100, 750), (120, 120, 120), age=40) for _ in range(50)]
    foods = [[random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)] for _ in range(130)]

    selected_e, k_id_counter = None, 0
    selected_k_stats = None

    running = True
    while running:
        if not world.is_extinct:
            # Оптимизация секторов еды
            food_sectors = {}
            for f in foods:
                key = (f[0] // SECTOR_SIZE, f[1] // SECTOR_SIZE)
                if key not in food_sectors: food_sectors[key] = []
                food_sectors[key].append(f)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

                # Полноэкранный режим
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        fullscreen = not fullscreen
                        if fullscreen:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    clicked_ui = False
                    # Клик по списку королевств справа
                    for i, k in world.kingdoms.items():
                        y_pos = 10 + i * 65
                        if WIDTH - 210 < mx < WIDTH - 10 and y_pos < my < y_pos + 60:
                            selected_k_stats = k
                            clicked_ui = True
                            break

                    if not clicked_ui:
                        selected_k_stats = None
                        selected_e = None
                        for e in entities:
                            if math.hypot(e.x - mx, e.y - my) < 15:
                                selected_e = e
                                break

            screen.fill((0, 0, 0))
            screen.blit(world.bg_surface, (0, 0))

            if len(foods) < 180 and random.random() < 0.3:
                foods.append([random.randint(20, WIDTH - 20), random.randint(20, HEIGHT - 20)])

            # Обновление королей и эпох
            for k in world.kingdoms.values():
                k.update_era()
                k.update_leader(entities)

            # Обновление мэров и городов
            for city in world.cities:
                city.update(foods, entities, world)
                city.draw(screen, font)

            new_borns, dead_list = [], []

            for e in entities:
                e.move_logic(foods, entities, food_sectors, world)

                # Основание королевства
                if e.kingdom_id is None and e.personal_science > THRESHOLD_FOUNDING and k_id_counter < 6:
                    new_bright = mutate_color(e.color, e.color, force_bright=True)
                    e.color = new_bright;
                    e.kingdom_id = k_id_counter
                    world.kingdoms[k_id_counter] = Kingdom(k_id_counter, new_bright, e.name)
                    world.cities.append(City(e.x, e.y, k_id_counter, new_bright))
                    k_id_counter += 1

                # Развитие (наука и новые города)
                if e.kingdom_id is not None:
                    k = world.kingdoms[e.kingdom_id]
                    k.science += e.genes["int"] * 0.01
                    if k.science - k.last_city_science > THRESHOLD_CITY_BUILD:
                        if all(math.hypot(e.x - c.x, e.y - c.y) > 150 for c in world.cities):
                            world.cities.append(City(e.x, e.y, e.kingdom_id, e.color))
                            k.last_city_science = k.science

                # Смерть
                if e.hunger > 100 or e.age > e.genes["max_age"]:
                    dead_list.append(e)
                    if e == selected_e: selected_e = None
                    continue

                # Размножение (ИСПРАВЛЕНО: kingdom_id вместо civ_id)
                if e.gender == 0 and e.age > 35 and e.reproduction_cooldown <= 0:
                    for p in entities:
                        if p.kingdom_id == e.kingdom_id and p.gender == 1 and p.age > 35 and p.reproduction_cooldown <= 0:
                            if math.hypot(e.x - p.x, e.y - p.y) < 12:
                                e.reproduction_cooldown = p.reproduction_cooldown = 60 * FPS
                                e.hunger += 45;
                                p.hunger += 45
                                nc = mutate_color(e.color, p.color)
                                # Создание ребенка с родителями
                                baby = Entity(e.x, e.y, nc, e.kingdom_id, genes=e.genes,
                                              gen_count=max(e.gen_count, p.gen_count) + 1,
                                              parents=(e.name, p.name))
                                new_borns.append(baby)
                                break
                e.draw(screen, (e == selected_e))

            for d in dead_list:
                if d in entities: entities.remove(d)
            entities.extend(new_borns)
            if not entities: world.is_extinct = True

            for f in foods: pygame.draw.circle(screen, (160, 160, 0), f, 2)

            # UI Справа: Королевства
            for i, k in world.kingdoms.items():
                y_pos = 10 + i * 65
                pygame.draw.rect(screen, (20, 20, 30), (WIDTH - 210, y_pos, 200, 60))
                pygame.draw.rect(screen, k.color, (WIDTH - 210, y_pos, 200, 60), 1)
                king_name = k.king.name if k.king else "Dead"
                screen.blit(title_font.render(k.name, True, k.color), (WIDTH - 200, y_pos + 5))
                screen.blit(font.render(f"Pop: {k.pop_count} | King: {king_name}", True, (255, 255, 255)),
                            (WIDTH - 200, y_pos + 22))
                screen.blit(font.render(f"Sci: {int(k.science)}", True, (180, 180, 180)), (WIDTH - 200, y_pos + 40))

            # UI Слева: Инфо о существе
            if selected_e:
                info_rect = pygame.Rect(10, 10, 260, 200)
                pygame.draw.rect(screen, (15, 15, 25), info_rect);
                pygame.draw.rect(screen, selected_e.color, info_rect, 1)

                title = "Citizen"
                k_obj = world.kingdoms.get(selected_e.kingdom_id)
                if k_obj:
                    if k_obj.king == selected_e: title = "KING"
                    for c in world.cities:
                        if c.mayor == selected_e: title = "MAYOR"

                g_str = "Male" if selected_e.gender == 0 else "Female"
                k_name = k_obj.name if k_obj else "Wilderness"

                lines = [
                    f"Name: {selected_e.name}", f"Title: {title}", f"Sex: {g_str}",
                    f"Parents: {selected_e.parents[0]} & {selected_e.parents[1]}",
                    f"House: {k_name}", f"Gen: {selected_e.gen_count}",
                    f"Age: {int(selected_e.age)}/{int(selected_e.genes['max_age'])}s",
                    f"Exp: {int(selected_e.personal_science)}", f"Hunger: {int(selected_e.hunger)}%"
                ]
                for i, l in enumerate(lines): screen.blit(font.render(l, True, (255, 255, 255)), (20, 20 + i * 18))

            # UI Снизу: Статистика королевства
            if selected_k_stats:
                stat_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 150, 300, 130)
                pygame.draw.rect(screen, (10, 10, 20), stat_rect);
                pygame.draw.rect(screen, selected_k_stats.color, stat_rect, 1)
                lines = [
                    f"--- {selected_k_stats.name} ---",
                    f"Founder: {selected_k_stats.founder_name}",
                    f"Population: {selected_k_stats.pop_count}",
                    f"Avg Speed: {selected_k_stats.avg_speed:.2f}",
                    f"Avg Intellect: {selected_k_stats.avg_int:.2f}",
                    f"Total Science: {int(selected_k_stats.science)}"
                ]
                for i, l in enumerate(lines):
                    col = (255, 255, 255) if i > 0 else selected_k_stats.color
                    screen.blit(font.render(l, True, col), (WIDTH // 2 - 130, HEIGHT - 140 + i * 18))

            pygame.display.flip();
            clock.tick(FPS)
        else:
            screen.fill((30, 0, 0));
            msg = big_font.render("EXTINCTION", True, (255, 255, 255))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()