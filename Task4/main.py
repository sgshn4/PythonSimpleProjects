def solution(source):
    symbols = []
    equals = False
    plus = False
    one = False
    index = -1
    start_index = -1
    result = []
    # Getting symbols
    for i in source:
        symbols.append(i)
    for i in symbols:
        index += 1
        if i == '=':
            start_index = index
            equals = True
        elif i == '+' and equals:
            plus = True
        elif i == '1' and equals and plus:
            one = True
        elif equals or plus and i == ' ':
            pass
        else:
            equals = False
            plus = False
            one = False
        if equals and plus and one:
            result = solution(replace(symbols, index, start_index))
    return result


def replace(symbols, index, start_index):
    replace_start = -1
    for i in reversed(range(index)):
        if symbols[i] != ' ':
            replace_start = i
    symbols[replace_start + 1] = '+'
    symbols[replace_start + 2] = '+'
    for i in range(start_index + 3, index):
        symbols.remove(symbols.pop[i])
    return symbols

