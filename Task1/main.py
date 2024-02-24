import sys


def solution(source):
    maxcount = []
    sums = []
    count = []
    # Find chains
    for i in range(len(source) - 1):
        if source[i] < source[i + 1]:
            count.append(source[i])
        else:
            count.append(source[i])
            maxcount.append(count)
            count = []
    # Find sums from chains
    for i in range(len(maxcount)):
        sum = 0
        for j in range(len(maxcount[i])):
            sum += maxcount[i][j]
        sums.append(sum)
    index = -1
    maxnum = -sys.maxsize - 1
    # Find max chain
    for i in range(len(sums)):
        if maxnum < sums[i]:
            maxnum = sums[i]
            index = i
    return maxcount[index]


print(solution([7, 4, 4, 7, 6, 3, 5, 5, 7, 2, 0, -1]))
