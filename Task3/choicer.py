import tablet
import utils
import random


def solution(gadgets, rating, memory, count):
    sorted_gadgets = []
    gadget = None

    # Sort by memory and price
    for i in gadgets:
        if i.memory >= memory and i.rating >= rating:
            sorted_gadgets.append(i)

    # Sort by price
    for i in sorted_gadgets:
        if gadget is None or gadget.price > i.price:
            gadget = i
    return output(gadget, count)


def output(gadget, count):
    if gadget is not None:
        result = (str(gadget.title) + '|' + str(gadget.memory) + '|' + str(gadget.rating) + '|' + str(gadget.price) +
                  '|' + str(gadget.price * count))
    else:
        result = ''
    return result


# print('=====Price List=====')
# memory = int(input('Input memory: '))
# rating = int(input('Input rating: '))
# count = int(input('Input count: '))
# print('====================')
# result = solution(utils.read_tablets('txt.txt'), rating, memory, count)
# print(result)
# print('====================')
