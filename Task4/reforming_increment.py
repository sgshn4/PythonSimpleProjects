def solution(lines):
    result = []
    for line in lines:
        equals = False
        plus = False
        one = False
        minus = False
        variable = False
        start_index = -1
        for i in range(len(line)):
            if line[i] == '=':
                start_index = i
                equals = True
            elif line[i] == '+' and equals:
                plus = True
                variable = check_variables(line, start_index, i)
            elif line[i] == '-' and equals:
                minus = True
                variable = check_variables(line, start_index, i)
            elif (line[i] == '1' and equals and plus) or (line[i] == '1' and equals and minus):
                one = True
            elif equals or plus or minus and line[i] == ' ':
                pass
            else:
                equals = False
                plus = False
                one = False
                minus = False
            if (equals and one and variable) and (minus or plus):
                line = replace(line, start_index, plus)
                break
        result.append(line)
    return result


def replace(symbols, start_index, plus):
    replace_start = -1
    for i in reversed(range(start_index)):
        if symbols[i + 1] == '=' and symbols[i] != ' ':
            replace_start = start_index - 1
            break
        elif symbols[i] != ' ':
            replace_start = i
            break
    if plus:
        symbols = symbols[:replace_start + 1] + '++;'
    else:
        symbols = symbols[:replace_start + 1] + '--;'
    return symbols


def check_variables(symbols, equals_index, plus_index):
    first = ''
    second = ''
    for i in reversed(range(equals_index)):
        if symbols[i] != ' ':
            first = symbols[i] + first
    for i in reversed(range(plus_index)):
        if symbols[i] != ' ':
            if symbols[i] == '=':
                break
            second = symbols[i] + second
    if first == second:
        return True
    else:
        return False
