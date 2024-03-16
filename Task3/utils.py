import tablet


def read_tablets(path):
    strs = read_data(path)
    tablets = []
    for i in strs:
        tablets.append(tablet.Tablet(i[0], int(i[1]), int(i[2]), int(i[3])))
    return tablets


def read_data(path):
    t = []
    f = open(path)
    for line in f:
        line_obj = line.split('|')
        line_obj[-1] = line_obj[-1][:-1]
        t.append(line_obj)
    f.close()
    return t


def write_file(path, t):
    string = ''
    for i in t:
        string = string + i + '\n'
    f = open(path, 'w')
    f.write(string)
    f.close()
