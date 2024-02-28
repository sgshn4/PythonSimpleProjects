import utils


def solution(lines):
    result = []
    for line in lines:
        equals = False
        plus = False
        one = False
        minus = False
        start_index = -1
        for i in range(len(line)):
            if line[i] == '=':
                start_index = i
                equals = True
            elif line[i] == '+' and equals:
                plus = True
            elif line[i] == '-' and equals:
                minus = True
            elif (line[i] == '1' and equals and plus) or (line[i] == '1' and equals and minus):
                one = True
            elif equals or plus or minus and line[i] == ' ':
                pass
            else:
                equals = False
                plus = False
                one = False
                minus = False
            if (equals and plus and one) or (equals and minus and one):
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


print(solution(utils.read_file('txt.txt')))
