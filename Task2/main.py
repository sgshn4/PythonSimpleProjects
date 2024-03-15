import copy


# Main cycle
def solution(matrix):
    result = []
    for i in range(len(matrix)):
        result.append([])
        for j in range(len(matrix[i])):
            if matrix[i][j] != 'i':
                temp = check_move(copy.deepcopy(matrix), j, i, matrix[i][j])
                result[i].append(replace(temp))
        print(result[i])


# Recursion to fill items with neighbour
def check_move(matrix, x, y, num):
    if -1 < x < len(matrix[0]) and len(matrix) > y > -1 and matrix[y][x] == num:
        matrix[y][x] = 'i'
        check_move(matrix, x, y - 1, num)  # Up
        check_move(matrix, x, y + 1, num)  # Down
        check_move(matrix, x - 1, y, num)  # Left
        check_move(matrix, x + 1, y, num)  # Right
    return matrix


# Counter for filled items
def replace(matrix):
    count = -1
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == 'i':
                count += 1
    return count


solution([[1, 2, 3, 9, 9],
          [2, 2, 2, 9, 2],
          [1, 1, 2, 2, 4]])
