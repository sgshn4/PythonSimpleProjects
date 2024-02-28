def read_file(path):
    lines = []
    f = open(path)
    for line in f:
        lines.append(line)
    f.close()
    return lines


def write_file(path, t):
    string = ''
    for i in t:
        string = (string + i.get_title() + '|' + str(i.get_memory()) + '|' + str(i.get_rating()) + '|' +
                  str(i.get_price()) + '\n')
    f = open(path, 'w')
    f.write(string)
    f.close()