import random
import copy


class Game:
    def __init__(self, w, h):
        self.map_w = w
        self.map_h = h
        self.x = None
        self.y = None
        self.game_map = None
        self.randomize_map()
        self.score = 0

    def randomize_map(self):
        self.randomize_position()
        result = []
        for i in range(self.map_h):
            result.append([])
            for j in range(self.map_w):
                if i == self.y and  j == self.x:
                    result[i].append('*')
                else:
                    result[i].append(random.randint(1, 6))
        self.game_map = result

    def randomize_position(self):
        self.x = random.randint(0, self.map_w - 1)
        self.y = random.randint(0, self.map_h - 1)

    def make_move(self, point_x, point_y):
        # Move on Y Axis
        if point_x == self.x:
            step = point_y - self.y
            for i in range(self.game_map[point_y][point_x]):
                if (0 < self.y + step < self.map_h and self.game_map[self.y + step][self.x]
                        is not '*'):
                    self.y += step
                    self.game_map[self.y][self.x] = '*'
                    self.score += 1
        # Move on X Axis
        elif point_y == self.y:
            step = point_x - self.x
            for i in range(self.game_map[point_y][point_x]):
                if (0 < self.x + step < self.map_w and self.game_map[self.y][self.x + step]
                        is not '*'):
                    self.x += step
                    self.game_map[self.y][self.x] = '*'
                    self.score += 1
        # Move on XY
        elif (point_x + 1 == self.x and (point_y + 1 == self.y or point_y - 1 == self.y)) or (
                point_x - 1 == self.x and (point_y + 1 == self.y or point_y - 1 == self.y)):
            step_y = point_y - self.y
            step_x = point_x - self.x
            for i in range(self.game_map[point_y][point_x]):
                if (0 < self.y + step_y < self.map_h and self.game_map[
                    self.y + step_y][self.x] is not '*') and (
                        0 < self.x + step_x < self.map_w and self.game_map[self.y][
                            self.x + step_x] is not '*'):
                    self.x += step_x
                    self.y += step_y
                    self.game_map[self.y][self.x] = '*'
                    self.score += 1
