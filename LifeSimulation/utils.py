import random

PREFIXES = ["Ar", "Be", "Cy", "Dr", "El", "Fa", "Go", "Ha", "Is", "Ju", "Ka", "Lu", "Mo", "Ni", "Or", "Pa", "Qu", "Ri", "Sy", "Ty", "Va", "Wy", "Xi", "Ye", "Ze"]
SUFFIXES = ["on", "ia", "us", "ax", "is", "en", "ar", "el", "um", "or", "in", "os", "an"]
CITY_PREFIXES = ["New ", "Old ", "Saint ", "Port ", "Fort ", "North ", "South ", "High "]
CITY_ROOTS = ["burg", "ville", "chester", "mouth", "ford", "land", "stead", "bridge", "grad"]
KINGDOM_TYPES = ["Empire of ", "Kingdom of ", "Republic of ", "Dominion of ", "Holy State of "]

def generate_name():
    return random.choice(PREFIXES) + "-" + random.choice(SUFFIXES)

def generate_city_name():
    if random.random() < 0.3:
        return random.choice(CITY_PREFIXES) + generate_name().split('-')[0]
    return generate_name().split('-')[0] + random.choice(CITY_ROOTS)

def generate_kingdom_name(founder_name):
    return random.choice(KINGDOM_TYPES) + founder_name

def mutate_color(c1, c2, force_bright=False):
    if force_bright:
        return random.choice([(255, 50, 50), (50, 255, 50), (80, 150, 255), (255, 255, 50), (255, 50, 255), (0, 255, 255)])
    new_c = list(((c1[i] + c2[i]) // 2 for i in range(3)))
    idx = random.randint(0, 2)
    new_c[idx] = max(50, min(255, new_c[idx] + random.choice([-30, 30])))
    return tuple(new_c)