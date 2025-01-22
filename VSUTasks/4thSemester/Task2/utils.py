def read_file(path):
    t = []
    f = open(path)
    for line in f:
        strnums = line.split(' ')
        strnums[-1] = strnums[-1][:-1]
        for i in range(len(strnums)):
            strnums[i] = int(strnums[i])
        t.append(strnums)
    f.close()
    return t


def write_file(path, t):
    string = ''
    for i in t:
        line = ''
        for j in i:
            line = line + str(j) + ' '
        string = string + line + '\n'
    f = open(path, 'w')
    f.write(string)
    f.close()
