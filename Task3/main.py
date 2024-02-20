import tablet
import utils
import random


def solution(gadgets, money):
    variants = []
    # First stage: money and memory
    max_memory = find_max_memory(gadgets)
    for i in gadgets:
        if i.get_price() <= money and i.get_memory() == max_memory:
            variants.append(i)
    # Second stage: rating
    if len(variants) > 1:
        max_rating = find_max_rating(variants)
        for i in reversed(range(len(variants))):
            if variants[i].get_rating() < max_rating:
                variants.remove(variants[i])
    elif len(variants) == 0:
        return None
    else:
        return variants[0]
    # Third stage: Samsung and Asus
    if len(variants) > 1:
        for i in variants:
            if i.get_title().find('Samsung') != -1 or i.get_title().find('Asus'):
                return i
    elif len(variants) == 0:
        return None
    else:
        return variants[0]
    # Last stage: Random
    return variants[random.randint(0, len(variants))]


def find_max_memory(gadgets):
    max_memory = 0
    for i in gadgets:
        if i.get_memory() > max_memory:
            max_memory = i.get_memory()
    return max_memory


def find_max_rating(gadgets):
    max_rating = 0
    for i in gadgets:
        if i.get_rating() > max_rating:
            max_rating = i.get_rating()
    return max_rating


print('=====Price List=====')
money = int(input('Input money: '))
result = solution(utils.read_file('txt.txt'), money)
if result is not None:
    print('Your best selection is')
    print(f'Title: {result.get_title()}')
    print(f'Memory: {result.get_memory()}')
    print(f'Rating: {result.get_rating()}')
    print(f'Price: {result.get_price()}')
else:
    print('We don\'t have for you any device :(')
print('====================')
