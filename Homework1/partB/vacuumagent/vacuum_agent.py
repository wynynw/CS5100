from typing import *
import random

def load_config(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    grid = lines[0].split(": ")[1].split(" ")
    grid[0], grid[1] = int(grid[0]), int(grid[1])

    dirt = lines[2:2 + grid[0]]
    dirt = [[float(num) for num in row.split(' ')] for row in dirt]

    max_moves = int(lines[2 + grid[0]].split(": ")[1])

    location = lines[3 + grid[0]].split(": ")[1].split(" ")
    location[0], location[1] = int(location[0])-1, int(location[1])-1

    return location, max_moves, grid, dirt

class Agent:
    def __init__(self, location: List, max_moves: int, map_size: List, dirt: List):
        self.total_score = 0
        self.location = location
        self.max_moves = max_moves
        self.map = Map(map_size, dirt)
        self.walked = set()
        self.walked.add(tuple(location))

    def is_move_invalid(self, move):

        if move == 'Right' and self.location[1] == self.map.map_size[1] - 1:
            return True
        elif move == 'Left' and self.location[1] == 0:
            return True
        elif move == 'Up' and self.location[0] == 0:
            return True
        elif move == 'Down' and self.location[0] == self.map.map_size[0] - 1:
            return True
        else:
            return False

    def do(self, option):
        if option == 'Right':
            self.location[1] += 1
        if option == 'Left':
            self.location[1] -= 1
        if option == 'Up':
            self.location[0] -= 1
        if option == 'Down':
            self.location[0] += 1
        if option == 'Suck':
            self.total_score += self.map.dirt[self.location[0]][self.location[1]]
            self.map.dirt[self.location[0]][self.location[1]] = 0

        self.walked.add((self.location[0], self.location[1]))

    def print_info(self, move, epoch=0):
        print("{} {:.1f}".format(move, self.total_score, 5))
        if epoch % 5 == 0 and epoch != 0:
            self.map.print_dirt(self)


class Map:

    def __init__(self, map_size: List, dirt):
        self.map_size = map_size
        self.dirt = dirt

    def print_dirt(self, agent: Agent):
        print()
        for row in self.dirt[:agent.location[0]]:
            i = 0
            for col in row:
                if i == 0:
                    i += 1
                else:
                    print(", ", end='')
                print(col, end='')
            print()

        curr_row = self.dirt[agent.location[0]]

        for col in curr_row[:agent.location[1]]:
            print("{} ".format(col), end='')

        print("[{}] ".format(self.dirt[agent.location[0]][agent.location[1]]), end="")

        i = 0
        for col in curr_row[agent.location[1] + 1:]:
            if i == 0:
                i += 1
            else:
                print(" ", end='')
            print("{}".format(col), end='')
        print()

        for row in self.dirt[agent.location[0] + 1:]:
            i = 0
            for col in row:
                if i == 0:
                    i += 1
                else:
                    print(" ", end='')
                print(col, end='')
            print()
        print()


class RandomAgent(Agent):

    def run(self):
        for i in range(self.max_moves):
            if self.map.dirt[self.location[0]][self.location[1]] > 0:
                option = 'Suck'
            else:
                option = random.choice(['Right', 'Left', 'Up', 'Down'])
                while self.is_move_invalid(option):
                    option = random.choice(['Right', 'Left', 'Up', 'Down'])

            self.do(option)
            self.print_info(option, i)


class GreedyAgent(Agent):
    def run(self):
        for i in range(self.max_moves):
            if self.map.dirt[self.location[0]][self.location[1]] > 0:
                option = 'Suck'
            else:
                option = self.get_max_neighbor()

            self.do(option)
            self.print_info(option, i)

    def get_max_neighbor(self):
        max_neighbor, val = 'Right', 0

        if not self.is_move_invalid('Right'):
            max_neighbor = 'Right'
        if not self.is_move_invalid('Left'):
            max_neighbor = 'Left'
        if not self.is_move_invalid('Up'):
            max_neighbor = 'Up'
        if not self.is_move_invalid('Down'):
            max_neighbor = 'Down'

        row = self.location[0]
        col = self.location[1]
        if not self.is_move_invalid('Right'):
            if val < self.map.dirt[row][col + 1]:
                max_neighbor = 'Right'
                val = self.map.dirt[row][col + 1]
        if not self.is_move_invalid('Left'):
            if val < self.map.dirt[row][col - 1]:
                max_neighbor = 'Left'
                val = self.map.dirt[row][col - 1]
        if not self.is_move_invalid('Up'):
            if val < self.map.dirt[row - 1][col]:
                max_neighbor = 'Up'
                val = self.map.dirt[row - 1][col]
        if not self.is_move_invalid('Down'):
            if val < self.map.dirt[row + 1][col]:
                max_neighbor = 'Down'
                val = self.map.dirt[row + 1][col]
        return max_neighbor


class StateAgent(Agent):
    def run(self):
        for i in range(self.max_moves):
            if self.map.dirt[self.location[0]][self.location[1]] > 0:
                option = 'Suck'
            else:
                option = self.get_best_neighbor()

            self.do(option)
            self.print_info(option, i)

    def get_best_neighbor(self):
        neighbor = {}
        y = self.location[0]
        x = self.location[1]

        flag = True
        if (not self.is_move_invalid('Right')) and ((y, x + 1) not in self.walked):
            flag = False
            neighbor['Right'] = self.map.dirt[y][x + 1]
        if (not self.is_move_invalid('Left')) and ((y, x - 1) not in self.walked):
            flag = False
            neighbor['Left'] = self.map.dirt[y][x - 1]
        if (not self.is_move_invalid('Up')) and ((y - 1, x) not in self.walked):
            flag = False
            neighbor['Up'] = self.map.dirt[y - 1][x]
        if (not self.is_move_invalid('Down')) and ((y + 1, x) not in self.walked):
            flag = False
            neighbor['Down'] = self.map.dirt[y + 1][x]
        if flag:
            while(True):
                step = random.choice(['Right', 'Left', 'Up', 'Down'])
                if self.is_move_invalid(step):
                    continue
                else:
                    break
            return step

        keys = list(neighbor.keys())
        random.shuffle(keys)
        neighbor = dict([(key, neighbor[key]) for key in keys])
        return max(neighbor, key=neighbor.get)

seed = 1024

pos, moves, grid, dirt = load_config('environ.txt')
random.seed(seed)
print("**Random Agent** start with {},{}\n".format(pos[0]+1, pos[1]+1))
reflex_agent = RandomAgent(pos, moves, grid, dirt)
reflex_agent.run()

pos, moves, grid, dirt = load_config('environ.txt')
random.seed(seed)
print("\n**Greedy Agent** start with {},{}\n".format(pos[0]+1, pos[1]+1))
greedy_agent = GreedyAgent(pos, moves, grid, dirt)
greedy_agent.run()

pos, moves, grid, dirt = load_config('environ.txt')
random.seed(seed)
state_agent = StateAgent(pos, moves, grid, dirt)
print("\n**State Agent** start with {},{}\n".format(pos[0]+1, pos[1]+1))
state_agent.run()

# print("{:.2f}".format(reflex_agent.total_score))
# print("{:.2f}".format(greedy_agent.total_score))
# print("{:.2f}".format(state_agent.total_score))
