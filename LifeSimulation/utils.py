import random
import os
from settings import GENEALOGY_FILE

M_NAMES = ["Ivan", "Dmitry", "Sergey", "Aleksey", "Andrey", "Artyom", "Nikolay", "Vladimir", "Igor", "Maksim", "Pavel", "Oleg"]
F_NAMES = ["Anna", "Elena", "Maria", "Olga", "Svetlana", "Tatiana", "Natalia", "Yulia", "Irina", "Daria", "Ksenia", "Alina"]
SURNAMES = ["Ivanov", "Petrov", "Smirnov", "Kuznetsov", "Sokolov", "Popov", "Lebedev", "Kozlov", "Novikov", "Morozov", "Solovyov", "Vasiliev"]

def generate_russian_name(gender):
    first = random.choice(M_NAMES if gender == 0 else F_NAMES)
    last = random.choice(SURNAMES)
    if gender == 1: last += "a"
    return first, last

def inherit_surname(f_last, m_last, child_gender):
    rand = random.random()
    f_root = f_last[:-1] if f_last.endswith('a') else f_last
    m_root = m_last[:-1] if m_last.endswith('a') else m_last
    if rand < 0.85: base = f_root
    elif rand < 0.98: base = m_root
    else: base = random.choice(SURNAMES)
    return base + ("a" if child_gender == 1 else "")

def generate_city_name(surname):
    root = surname[:-1] if surname.endswith('a') else surname
    suffixes = ["grad", "sk", "o", "vka", "burg"]
    return root + random.choice(suffixes)

def generate_kingdom_name(surname):
    root = surname[:-1] if surname.endswith('a') else surname
    types = ["Empire of ", "Kingdom of ", "Republic of ", "State of "]
    return random.choice(types) + root

def mutate_color(c1, c2, force_bright=False):
    if force_bright:
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    return tuple(max(40, min(255, (c1[i] + c2[i]) // 2 + random.randint(-15, 15))) for i in range(3))

def save_to_genealogy(name, p1, p2, gen, gender):
    with open(GENEALOGY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name}|{p1}|{p2}|{gen}|{gender}\n")

def clear_genealogy():
    # Надежный способ очистки файла
    with open(GENEALOGY_FILE, "w", encoding="utf-8") as f:
        f.write("")