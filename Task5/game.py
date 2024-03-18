import random
import copy


class Game:
    def __init__(self, w, h):
        self.map_w = w
        self.map_h = h
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)
        self.game_map = self.randomize_map()

    def randomize_map(self):
        result = []
        for i in range(self.map_h):
            result.append([])
            for j in range(self.map_w):
                if i == self.y and  j == self.x:
                    result[i].append('*')
                else:
                    result[i].append(random.randint(1, 6))
        return result

    def make_move(self, point_x, point_y):
        # Move on Y Axis
        if point_x == self.x:
            for i in range(self.game_map[point_y][point_x]):
                if 0 < self.y + self.y - point_y < self.map_h and self.game_map[self.y + self.y - point_y][self.x] is not '*':
                    self.game_map[self.y][self.x] = '*'
                    self.y + self.y - point_y
        elif point_y == self.y:
            # Move on X Axis
            for i in range(self.game_map[point_y][point_x]):
                if 0 < self.x + self.x - point_x < self.map_w and self.game_map[self.y][self.x + self.x - point_x] is not '*':
                    self.game_map[self.y][self.x] = '*'
                    self.x + self.x - point_x



