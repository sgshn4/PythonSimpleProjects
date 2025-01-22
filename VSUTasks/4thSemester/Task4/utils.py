def read_file(path):
    lines = []
    f = open(path)
    for line in f:
        lines.append(line)
    f.close()
    return lines


def write_file(path, lines):
    string = ''
    for line in lines:
        string = string + line + '\n'
    f = open(path, 'w')
    f.write(string)
    f.close()
