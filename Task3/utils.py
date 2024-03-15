import tablet


def read_file(path):
    t = []
    f = open(path)
    for line in f:
        line_obj = line.split('|')
        t.append(tablet.Tablet(line_obj[0], int(line_obj[1]), int(line_obj[2]), int(line_obj[3])))
    f.close()
    return t


def write_file(path, t):
    string = ''
    for i in t:
        string = (string + i.title + '|' + str(i.memory) + '|' + str(i.rating) + '|' +
                  str(i.price) + '\n')
    f = open(path, 'w')
    f.write(string)
    f.close()
