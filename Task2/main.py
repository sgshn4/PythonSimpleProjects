import copy
def solution(matrix):
    result = []
    for i in range(len(matrix)):
        result.append([])
        for j in range(len(matrix[i])):
            if matrix[i][j] != 'i':
                result[i].append(check_move(matrix, j, i, matrix[i][j], 0))
        print(result[i])


def check_move(matrix, x, y, num, count):
    if -1 < x < len(matrix[0]) and len(matrix) > y > -1 and matrix[y][x] == num:
        matrix[y][x] = 'i'
        counts = [check_move(matrix, x, y - 1, num, count + 1),
                  check_move(matrix, x, y + 1, num, count + 1),
                  check_move(matrix, x - 1, y, num, count + 1),
                  check_move(matrix, x + 1, y, num, count + 1)]
        max_num = None
        for i in reversed(range(len(counts))):
            if counts[i] is None:
                counts.pop(i)
        if len(counts) > 1:
            for i in counts:
                if max_num is None or max_num < i:
                    max_num = i
        else:
            max_num = 0
        return max_num
    else:
        return count


solution([[1, 2, 3, 9, 9],
          [2, 2, 2, 9, 2],
          [1, 1, 2, 2, 4]])
