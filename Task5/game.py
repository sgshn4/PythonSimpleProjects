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
        self.is_lose = False

    def randomize_map(self):
        self.randomize_position()
        self.is_lose = False
        result = []
        for i in range(self.map_h):
            result.append([])
            for j in range(self.map_w):
                if i == self.y and j == self.x:
                    result[i].append('*')
                else:
                    result[i].append(random.randint(1, 6))
        self.game_map = result

    def randomize_position(self):
        self.x = random.randint(0, self.map_w - 1)
        self.y = random.randint(0, self.map_h - 1)

    def make_move(self, point_x, point_y):
        if self.game_map[point_y][point_x] != '*' and not self.is_lose:
            # Move on XY
            step_y = point_y - self.y
            step_x = point_x - self.x
            if -2 < step_x < 2 and -2 < step_y < 2:
                for i in range(self.game_map[point_y][point_x]):
                    if -1 < self.y + step_y < self.map_h and -1 < self.x + step_x < self.map_w:
                        if self.game_map[self.y + step_y][self.x + step_x] != '*':
                            self.x += step_x
                            self.y += step_y
                            self.game_map[self.y][self.x] = '*'
                            self.score += 1
                        else:
                            self.is_lose = True
                            break
                    else:
                        self.is_lose = True
                        break
