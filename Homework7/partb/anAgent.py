import enum


class Orientation(enum.Enum):
    north = 1
    south = 2
    east = 3
    west = 4

    @property
    def turn_left(self):
        dict_turn_left = {
            Orientation.north: Orientation.west,
            Orientation.south: Orientation.east,
            Orientation.east: Orientation.north,
            Orientation.west: Orientation.south
        }
        new_orientation = dict_turn_left.get(self)
        return new_orientation

    @property
    def turn_right(self):
        dict_turn_right = {
            Orientation.north: Orientation.east,
            Orientation.south: Orientation.west,
            Orientation.east: Orientation.south,
            Orientation.west: Orientation.north
        }
        new_orientation = dict_turn_right.get(self)
        return new_orientation


class Action():
    def __init__(self, is_forward=False, is_turn_left=False, is_turn_right=False,
                 is_shoot=False, is_grab=False, is_climb=False):
        assert is_forward ^ is_turn_left ^ is_turn_right ^ is_shoot ^ is_grab ^ is_climb
        self.is_forward = is_forward
        self.is_turn_left = is_turn_left
        self.is_turn_right = is_turn_right
        self.is_shoot = is_shoot
        self.is_grab = is_grab
        self.is_climb = is_climb

    @classmethod
    def forward(cls):
        return Action(is_forward=True)

    @classmethod
    def turn_left(cls):
        return Action(is_turn_left=True)

    @classmethod
    def turn_right(cls):
        return Action(is_turn_right=True)

    @classmethod
    def shoot(cls):
        return Action(is_shoot=True)

    @classmethod
    def grab(cls):
        return Action(is_grab=True)

    @classmethod
    def climb(cls):
        return Action(is_climb=True)

    def show(self):
        if self.is_forward:
            action_str = "forward"
        elif self.is_turn_left:
            action_str = "turn_left"
        elif self.is_turn_right:
            action_str = "turn_right"
        elif self.is_shoot:
            action_str = "shoot"
        elif self.is_grab:
            action_str = "grab"
        else:
            action_str = "climb"
        return action_str

from collections import namedtuple


class Coords(namedtuple('Coords', 'x y')):
    def adjacent_cells(self, grid_width, grid_height):
        neighbors = []
        if self.x > 0:  # to left
            neighbors.append(Coords(self.x - 1, self.y))
        if self.x < (grid_width - 1):  # to right
            neighbors.append(Coords(self.x + 1, self.y))
        if self.y > 0:  # below
            neighbors.append(Coords(self.x, self.y - 1))
        if self.y < (grid_height - 1):  # above
            neighbors.append(Coords(self.x, self.y + 1))
        return neighbors


class Percept():
    def __init__(self, stench, breeze, glitter, bump, scream, is_terminated, reward):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream
        self.is_terminated = is_terminated
        self.reward = reward

    def show(self):
        print("stench: {}, breeze: {}, glitter: {}, bump: {}, scream: {}, is_terminated: {}, reward: {}"
              .format(self.stench, self.breeze, self.glitter, self.bump, self.scream, self.is_terminated, self.reward))


class AgentState():
    def __init__(self, location=Coords(0, 0), orientation=Orientation.east, has_gold=False, has_arrow=True,
                 is_alive=True):
        self.location = location
        self.orientation = orientation
        self.has_gold = has_gold
        self.has_arrow = has_arrow
        self.is_alive = is_alive

    def turn_left(self):
        new_state = copy.deepcopy(self)
        new_state.orientation = new_state.orientation.turn_left
        return new_state

    def turn_right(self):
        new_state = copy.deepcopy(self)
        new_state.orientation = new_state.orientation.turn_right
        return new_state

    def forward(self, grid_width, grid_height):
        if self.orientation == Orientation.north:
            new_loc = Coords(self.location.x, min(grid_height - 1, self.location.y + 1))
        elif self.orientation == Orientation.south:
            new_loc = Coords(self.location.x, max(0, self.location.y - 1))
        elif self.orientation == Orientation.east:
            new_loc = Coords(min(grid_width - 1, self.location.x + 1), self.location.y)
        else:
            new_loc = Coords(max(0, self.location.x - 1), self.location.y)  # if Orientation.west
        new_state = copy.deepcopy(self)
        new_state.location = new_loc
        return new_state

    def apply_move_action(self, action, grid_width, grid_height):
        if action.is_forward:
            return self.forward(grid_width, grid_height)
        if action.is_turn_left:
            return self.turn_left()
        if action.is_turn_right:
            return self.turn_right()
        if action.is_shoot:
            return self.use_arrow()
        if action.is_climb:
            return self

    def use_arrow(self):
        new_state = copy.deepcopy(self)
        new_state.has_arrow = False
        return new_state

    def show(self):
        print("location: {}, orientation: {}, has_gold: {}, has_arrow: {}, is_alive: {}"
              .format(self.location, self.orientation, self.has_gold, self.has_arrow, self.is_alive))


# Create a list with all locations
def list_all_locations(grid_width, grid_height):
    all_cells = []
    for x in range(grid_width):
        for y in range(grid_height):
            all_cells.append(Coords(x, y))
    return all_cells


# Create locations for gold and wumpus
def random_location_except_origin(grid_width, grid_height):
    locations = list_all_locations(grid_width, grid_height)
    locations.remove(Coords(0, 0))
    return random.choice(locations)


# Create pit locations
def create_pit_locations(grid_width, grid_height, pit_prob):
    locations = list_all_locations(grid_width, grid_height)
    locations.remove(Coords(0, 0))
    pit_locations = [loc for loc in locations if random.random() < pit_prob]
    return pit_locations




class Environment():
    def __init__(self, grid_width, grid_height, pit_prob, allow_climb_without_gold, agent, pit_locations,
                 terminated, wumpus_loc, wumpus_alive, gold_loc):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.pit_prob = pit_prob
        self.allow_climb_without_gold = allow_climb_without_gold
        self.agent = agent
        self.pit_locations = pit_locations
        self.terminated = terminated
        self.wumpus_loc = wumpus_loc
        self.wumpus_alive = wumpus_alive
        self.gold_loc = gold_loc

    def is_pit_at(self, coords):
        return coords in self.pit_locations

    def is_wumpus_at(self, coords):
        return coords == self.wumpus_loc

    def is_agent_at(self, coords):
        return coords == self.agent.location

    def is_glitter(self):
        return self.gold_loc == self.agent.location

    def is_gold_at(self, coords):
        return coords == self.gold_loc

    def wumpus_in_line_of_fire(self):
        if self.agent.orientation == Orientation.west:
            return self.agent.location.x > self.wumpus_loc.x and self.agent.location.y == self.wumpus_loc.y
        if self.agent.orientation == Orientation.east:
            return self.agent.location.x < self.wumpus_loc.x and self.agent.location.y == self.wumpus_loc.y
        if self.agent.orientation == Orientation.south:
            return self.agent.location.x == self.wumpus_loc.x and self.agent.location.y > self.wumpus_loc.y
        if self.agent.orientation == Orientation.north:
            return self.agent.location.x == self.wumpus_loc.x and self.agent.location.y < self.wumpus_loc.y

    def kill_attempt_successful(self):
        return self.agent.has_arrow and self.wumpus_alive and self.wumpus_in_line_of_fire()

    def is_pit_adjacent(self, coords):
        for cell in coords.adjacent_cells(self.grid_width, self.grid_height):
            if cell in self.pit_locations:
                return True
        return False

    def is_wumpus_adjacent(self, coords):
        for cell in coords.adjacent_cells(self.grid_width, self.grid_height):
            if self.is_wumpus_at(cell):
                return True
        return False

    def is_breeze(self):
        return self.is_pit_adjacent(self.agent.location)

    def is_stench(self):
        return self.is_wumpus_adjacent(self.agent.location) or self.is_wumpus_at(self.agent.location)

    def apply_action(self, action):
        if self.terminated:
            return (self, Percept(False, False, False, False, False, True, 0))
        else:
            if action.is_forward:
                moved_agent = self.agent.forward(self.grid_width, self.grid_height)
                death = (self.is_wumpus_at(moved_agent.location) and self.wumpus_alive) or self.is_pit_at(
                    moved_agent.location)
                new_agent = copy.deepcopy(moved_agent)
                new_agent.is_alive = not death
                new_gold_loc = new_agent.location if self.agent.has_gold else self.gold_loc
                new_env = Environment(self.grid_width, self.grid_height, self.pit_prob, self.allow_climb_without_gold,
                                      new_agent, self.pit_locations, death, self.wumpus_loc, self.wumpus_alive,
                                      new_gold_loc)
                percept = Percept(new_env.is_stench(), new_env.is_breeze(), new_env.is_glitter(),
                                  new_agent.location == self.agent.location, False, death,
                                  -1 if new_agent.is_alive else -1001)
                return (new_env, percept)

            if action.is_turn_left:
                new_env = Environment(self.grid_width, self.grid_height, self.pit_prob, self.allow_climb_without_gold,
                                      self.agent.turn_left(), self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive, self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, False, -1)
                return (new_env, percept)

            if action.is_turn_right:
                new_env = Environment(self.grid_width, self.grid_height, self.pit_prob, self.allow_climb_without_gold,
                                      self.agent.turn_right(), self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive, self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, False, -1)
                return (new_env, percept)

            if action.is_grab:
                new_agent = copy.deepcopy(self.agent)
                new_agent.has_gold = self.is_glitter()
                new_gold_loc = new_agent.location if new_agent.has_gold else self.gold_loc
                new_env = Environment(self.grid_width, self.grid_height, self.pit_prob, self.allow_climb_without_gold,
                                      new_agent, self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive,
                                      new_gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, False, -1)
                return (new_env, percept)

            if action.is_climb:
                in_start_loc = self.agent.location == Coords(0, 0)
                success = self.agent.has_gold and in_start_loc
                is_terminated = success or (self.allow_climb_without_gold and in_start_loc)
                new_env = Environment(self.grid_width, self.grid_height, self.pit_prob, self.allow_climb_without_gold,
                                      self.agent, self.pit_locations, is_terminated, self.wumpus_loc, self.wumpus_alive,
                                      self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, is_terminated,
                                  999 if success else -1)
                return (new_env, percept)

            if action.is_shoot:
                had_arrow = self.agent.has_arrow
                wumpus_killed = self.kill_attempt_successful()
                new_agent = copy.deepcopy(self.agent)
                new_agent.has_arrow = False
                new_env = Environment(self.grid_width, self.grid_height, self.pit_prob, self.allow_climb_without_gold,
                                      new_agent, self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive and (not wumpus_killed), self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, wumpus_killed, False,
                                  -11 if had_arrow else -1)
                return (new_env, percept)

    @classmethod
    def new_game(cls, grid_width, grid_height, pit_prob, allow_climb_without_gold):
        new_pit_locations = create_pit_locations(grid_width, grid_height, pit_prob)
        new_wumpus_loc = random_location_except_origin(grid_width, grid_height)
        new_gold_loc = random_location_except_origin(grid_width, grid_height)
        env = Environment(grid_width, grid_height, pit_prob, allow_climb_without_gold,
                          AgentState(), new_pit_locations, False, new_wumpus_loc, True, new_gold_loc)
        percept = Percept(env.is_stench(), env.is_breeze(), False, False, False, False, 0.0)
        return (env, percept)

    def visualize(self):
        wumpus_symbol = "W" if self.wumpus_alive else "w"
        all_rows = []
        for y in range(self.grid_height - 1, -1, -1):
            row = []
            for x in range(self.grid_width):
                agent = "A" if self.is_agent_at(Coords(x, y)) else " "
                pit = "P" if self.is_pit_at(Coords(x, y)) else " "
                gold = "G" if self.is_gold_at(Coords(x, y)) else " "
                wumpus = wumpus_symbol if self.is_wumpus_at(Coords(x, y)) else " "
                cell = agent + pit + gold + wumpus
                row.append(cell)
            row_str = "|".join(row)
            all_rows.append(row_str)
        final_str = "\n".join(all_rows)
        print(final_str)


def encode_action_to_int(action):
    if action.is_forward:
        action_int = 0
    elif action.is_turn_left:
        action_int = 1
    elif action.is_turn_right:
        action_int = 2
    elif action.is_shoot:
        action_int = 3
    elif action.is_grab:
        action_int = 4
    else:  # climb
        action_int = 5
    return action_int


def decode_action_index(index):
    actions = [Action.forward(), Action.turn_left(), Action.turn_right(), Action.shoot(), Action.grab(), Action.climb()]
    return actions[index]


import numpy as np

# The ExperienceCollector class to collect all the states, decisions and rewards (as Python lists)

class ExperienceCollector:
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []

    def record_state(self, state):
        self.states.append(state)

    def record_action(self, action):
        self.actions.append(action)

    def record_reward(self, reward):
        self.rewards.append(reward)




class Agent:
    def __init__(self):
        pass

    def select_action(self, percept):
        raise NotImplementedError()


import networkx as nx
from pomegranate import *
import random
import copy


class ProbAgent(Agent):

    def __init__(self, grid_width, grid_height, pit_prob, agent_state, beeline_action_list,
                 breeze_locations, stench_locations, visited_locations, heard_scream,
                 inferred_pit_probs, inferred_wumpus_probs, perceives_glitter, perceives_bump):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.pit_prob = pit_prob
        self.agent_state = agent_state
        self.beeline_action_list = beeline_action_list
        self.breeze_locations = set(breeze_locations)
        self.stench_locations = set(stench_locations)
        self.visited_locations = set(visited_locations)
        self.heard_scream = heard_scream
        self.inferred_pit_probs = inferred_pit_probs
        self.inferred_wumpus_probs = inferred_wumpus_probs
        self.collector = None
        self.perceives_glitter = perceives_glitter
        self.perceives_bump = perceives_bump

    def set_collector(self, collector):
        self.collector = collector

    def show(self):
        self.agent_state.show()
        print("visited_locations: {}".format(self.visited_locations))
        print("breeze_locations: {}".format(self.breeze_locations))
        print("stench_locations: {}".format(self.stench_locations))
        print("heard_scream: {}".format(self.heard_scream))
        print("perceives_glitter: {}".format(self.perceives_glitter))
        print("perceives_bump: {}".format(self.perceives_bump))
        print("inferred_pit_probs: {}".format(self.inferred_pit_probs))
        print("inferred_wumpus_probs: {}".format(self.inferred_wumpus_probs))
        print("beeline_action_list: {}".format([action.show() for action in self.beeline_action_list]))

    def construct_beeline_plan(self, goal_node, safe_locations):

        # Create an undirected two-dimensional grid graph where each node is connected to its four nearest neighbors
        G = nx.grid_2d_graph(self.grid_width, self.grid_height)
        not_safe_locations = [node for node in G if node not in safe_locations]
        G.remove_nodes_from(not_safe_locations)  # keep only safe locations as nodes

        # Compute all shortest simple paths in the graph between source and target (every edge has weight/distance/cost 1)
        shortest_paths = [p for p in nx.all_shortest_paths(G, source=self.agent_state.location, target=goal_node)]

        # Functions for finding the new agent's orientation and required actions to move to the next point on the path

        def north(orientation, a, b):
            if a.x > b.x:  # move left
                return (orientation.turn_left, [Action.turn_left(), Action.forward()])
            if a.x < b.x:  # move right
                return (orientation.turn_right, [Action.turn_right(), Action.forward()])
            if a.y > b.y:  # move down
                return (orientation.turn_left.turn_left, [Action.turn_left(), Action.turn_left(), Action.forward()])
            if a.y < b.y:  # move up
                return (orientation, [Action.forward()])

        def south(orientation, a, b):
            if a.x > b.x:  # move left
                return (orientation.turn_right, [Action.turn_right(), Action.forward()])
            if a.x < b.x:  # move right
                return (orientation.turn_left, [Action.turn_left(), Action.forward()])
            if a.y > b.y:  # move down
                return (orientation, [Action.forward()])
            if a.y < b.y:  # move up
                return (orientation.turn_left.turn_left, [Action.turn_left(), Action.turn_left(), Action.forward()])

        def east(orientation, a, b):
            if a.x > b.x:  # move left
                return (orientation.turn_left.turn_left, [Action.turn_left(), Action.turn_left(), Action.forward()])
            if a.x < b.x:  # move right
                return (orientation, [Action.forward()])
            if a.y > b.y:  # move down
                return (orientation.turn_right, [Action.turn_right(), Action.forward()])
            if a.y < b.y:  # move up
                return (orientation.turn_left, [Action.turn_left(), Action.forward()])

        def west(orientation, a, b):
            if a.x > b.x:  # move left
                return (orientation, [Action.forward()])
            if a.x < b.x:  # move right
                return (orientation.turn_left.turn_left, [Action.turn_left(), Action.turn_left(), Action.forward()])
            if a.y > b.y:  # move down
                return (orientation.turn_left, [Action.turn_left(), Action.forward()])
            if a.y < b.y:  # move up
                return (orientation.turn_right, [Action.turn_right(), Action.forward()])

        dict_orientation_to_actions = {
            Orientation.north: north,
            Orientation.south: south,
            Orientation.east: east,
            Orientation.west: west
        }

        def determine_actions(orientation, a, b):
            func = dict_orientation_to_actions.get(orientation)
            return func(orientation, a, b)

        # Convert each shortest path into a plan (lists of actions)
        plans_list = []  # list with plans for all shortest paths
        for path in shortest_paths:
            path_coords = [Coords(*node) for node in path]  # convert all nodes to the Coords() type
            orientation = self.agent_state.orientation
            full_plan = []
            for i in range(len(path_coords) - 1):
                (orientation, actions) = determine_actions(orientation, path_coords[i], path_coords[i + 1])
                full_plan.extend(actions)
            plans_list.append(full_plan)

        # Find the number of turns for each plan (if more than one shortest path) and choose the plan with fewer turns
        if len(plans_list) > 1:
            plans_turn_counts = []
            for plan in plans_list:
                turn_count = 0
                for action in plan:
                    if action.is_turn_left or action.is_turn_right:
                        turn_count += 1
                plans_turn_counts.append(turn_count)
            beeline_plan_index = plans_turn_counts.index(min(plans_turn_counts))
            beeline_plan = plans_list[beeline_plan_index]
        else:
            beeline_plan = plans_list[0]
        return beeline_plan

    # Choose the first action from the beeline list of actions, update the agent_state and beeline_action_list

    def beeline(self, beeline_plan):
        beeline_action = beeline_plan[0]
        new_agent = copy.deepcopy(self)
        new_agent.agent_state = new_agent.agent_state.apply_move_action(beeline_action, self.grid_width,
                                                                        self.grid_height)
        new_agent.beeline_action_list = beeline_plan[1:]
        return (new_agent, beeline_action)

    # Build a probabilistic model for wumpus and stench locations

    def create_model_wumpus(self):

        # List of all locations
        all_cells = list_all_locations(self.grid_width, self.grid_height)

        # Discrete distribution for wumpus
        wumpus_initial_probs = {}
        for cell in all_cells:
            if cell.x == 0 and cell.y == 0:
                wumpus_initial_probs[cell] = 0.0
            else:
                wumpus_initial_probs[cell] = 1.0 / (self.grid_width * self.grid_height - 1)
        wumpus_location_dist = DiscreteDistribution(wumpus_initial_probs)

        # Dictionary with wumpus CPDs (a CPD for each cell - probability of wumpus being at this cell and not at other cells)
        dict_wumpus_probs = {}
        for cell in all_cells:
            wumpus_probs = []
            for cell_2 in all_cells:
                if cell_2 != cell:
                    wumpus_probs.append([cell_2, True, 0.0])
                    wumpus_probs.append([cell_2, False, 1.0])
                else:
                    wumpus_probs.append([cell_2, True, 1.0])
                    wumpus_probs.append([cell_2, False, 0.0])
            dict_wumpus_probs[cell] = ConditionalProbabilityTable(wumpus_probs, [wumpus_location_dist])

        #  Dictionary with stench CPDs (a CPD for each cell - probability of stench at this cell)
        dict_stench_probs = {}
        dict_neighbors = {}  # dict where keys and values are cells and their neighbors respectively
        for cell in all_cells:
            neighbors = cell.adjacent_cells(self.grid_width, self.grid_height)
            dict_neighbors[cell] = neighbors
            if len(neighbors) == 2:
                dict_stench_probs[cell] = ConditionalProbabilityTable([[0, 0, 0, 1.0],
                                                                       [0, 0, 1, 0.0],
                                                                       [0, 1, 0, 0.0],
                                                                       [0, 1, 1, 1.0],
                                                                       [1, 0, 0, 0.0],
                                                                       [1, 0, 1, 1.0],
                                                                       [1, 1, 0, 0.0],
                                                                       [1, 1, 1, 1.0]],
                                                                      [dict_wumpus_probs[neighbors[0]],
                                                                       dict_wumpus_probs[neighbors[1]]])
            elif len(neighbors) == 3:
                dict_stench_probs[cell] = ConditionalProbabilityTable([[0, 0, 0, 0, 1.0],
                                                                       [0, 0, 0, 1, 0.0],
                                                                       [0, 0, 1, 0, 0.0],
                                                                       [0, 0, 1, 1, 1.0],
                                                                       [0, 1, 0, 0, 0.0],
                                                                       [0, 1, 0, 1, 1.0],
                                                                       [0, 1, 1, 0, 0.0],
                                                                       [0, 1, 1, 1, 1.0],
                                                                       [1, 0, 0, 0, 0.0],
                                                                       [1, 0, 0, 1, 1.0],
                                                                       [1, 0, 1, 0, 0.0],
                                                                       [1, 0, 1, 1, 1.0],
                                                                       [1, 1, 0, 0, 0.0],
                                                                       [1, 1, 0, 1, 1.0],
                                                                       [1, 1, 1, 0, 0.0],
                                                                       [1, 1, 1, 1, 1.0]],
                                                                      [dict_wumpus_probs[neighbors[0]],
                                                                       dict_wumpus_probs[neighbors[1]],
                                                                       dict_wumpus_probs[neighbors[2]]])
            else:  # four neighbors
                dict_stench_probs[cell] = ConditionalProbabilityTable([[0, 0, 0, 0, 0, 1.0],
                                                                       [0, 0, 0, 0, 1, 0.0],
                                                                       [0, 0, 0, 1, 0, 0.0],
                                                                       [0, 0, 0, 1, 1, 1.0],
                                                                       [0, 0, 1, 0, 0, 0.0],
                                                                       [0, 0, 1, 0, 1, 1.0],
                                                                       [0, 0, 1, 1, 0, 0.0],
                                                                       [0, 0, 1, 1, 1, 1.0],
                                                                       [0, 1, 0, 0, 0, 0.0],
                                                                       [0, 1, 0, 0, 1, 1.0],
                                                                       [0, 1, 0, 1, 0, 0.0],
                                                                       [0, 1, 0, 1, 1, 1.0],
                                                                       [0, 1, 1, 0, 0, 0.0],
                                                                       [0, 1, 1, 0, 1, 1.0],
                                                                       [0, 1, 1, 1, 0, 0.0],
                                                                       [0, 1, 1, 1, 1, 1.0],
                                                                       [1, 0, 0, 0, 0, 0.0],
                                                                       [1, 0, 0, 0, 1, 1.0],
                                                                       [1, 0, 0, 1, 0, 0.0],
                                                                       [1, 0, 0, 1, 1, 1.0],
                                                                       [1, 0, 1, 0, 0, 0.0],
                                                                       [1, 0, 1, 0, 1, 1.0],
                                                                       [1, 1, 0, 0, 0, 0.0],
                                                                       [1, 1, 0, 0, 1, 1.0],
                                                                       [1, 0, 1, 1, 0, 0.0],
                                                                       [1, 0, 1, 1, 1, 1.0],
                                                                       [1, 1, 0, 1, 0, 0.0],
                                                                       [1, 1, 0, 1, 1, 1.0],
                                                                       [1, 1, 1, 0, 0, 0.0],
                                                                       [1, 1, 1, 0, 1, 1.0],
                                                                       [1, 1, 1, 1, 0, 0.0],
                                                                       [1, 1, 1, 1, 1, 1.0]],
                                                                      [dict_wumpus_probs[neighbors[0]],
                                                                       dict_wumpus_probs[neighbors[1]],
                                                                       dict_wumpus_probs[neighbors[2]],
                                                                       dict_wumpus_probs[neighbors[3]]])
        # Create states
        wumpus_state = State(wumpus_location_dist)

        wumpus_cpd_states = {}
        for cell in all_cells:
            wumpus_cpd_states[cell] = State(dict_wumpus_probs[cell])

        stench_cpd_states = {}
        for cell in all_cells:
            stench_cpd_states[cell] = State(dict_stench_probs[cell])

        # Model
        model_wumpus = BayesianNetwork("model_wumpus_stenches")

        # Add states
        model_wumpus.add_state(wumpus_state)
        for cell in all_cells:
            model_wumpus.add_state(wumpus_cpd_states[cell])
        for cell in all_cells:
            model_wumpus.add_state(stench_cpd_states[cell])

        # Add edges
        for cell in all_cells:
            model_wumpus.add_edge(wumpus_state, wumpus_cpd_states[cell])
        for cell in all_cells:
            for n in dict_neighbors[cell]:
                model_wumpus.add_edge(wumpus_cpd_states[n], stench_cpd_states[cell])

        model_wumpus.bake()
        return model_wumpus

    # Build a probabilistic model for pit and breeze locations

    def create_model_pits(self):
        # All locations in the grid
        all_cells = list_all_locations(self.grid_width, self.grid_height)

        # Dictionary with discrete distributions for pits (a discrete distribution for each cell)
        dict_pit_probs = {}
        for cell in all_cells:
            if cell.x == 0 and cell.y == 0:
                dict_pit_probs[cell] = DiscreteDistribution({True: 0.0, False: 1.0})
            else:
                dict_pit_probs[cell] = DiscreteDistribution({True: self.pit_prob, False: 1 - self.pit_prob})

        # Dictionary with breeze CPDs (a CPD for each cell - probability of breeze at this cell)
        dict_breeze_probs = {}
        dict_neighbors = {}  # dict where keys and values are cells and their neighbors respectively
        for cell in all_cells:
            neighbors = cell.adjacent_cells(self.grid_width, self.grid_height)
            dict_neighbors[cell] = neighbors
            if len(neighbors) == 2:
                dict_breeze_probs[cell] = ConditionalProbabilityTable([[0, 0, 0, 1.0],
                                                                       [0, 0, 1, 0.0],
                                                                       [0, 1, 0, 0.0],
                                                                       [0, 1, 1, 1.0],
                                                                       [1, 0, 0, 0.0],
                                                                       [1, 0, 1, 1.0],
                                                                       [1, 1, 0, 0.0],
                                                                       [1, 1, 1, 1.0]], [dict_pit_probs[neighbors[0]],
                                                                                         dict_pit_probs[neighbors[1]]])
            elif len(neighbors) == 3:
                dict_breeze_probs[cell] = ConditionalProbabilityTable([[0, 0, 0, 0, 1.0],
                                                                       [0, 0, 0, 1, 0.0],
                                                                       [0, 0, 1, 0, 0.0],
                                                                       [0, 0, 1, 1, 1.0],
                                                                       [0, 1, 0, 0, 0.0],
                                                                       [0, 1, 0, 1, 1.0],
                                                                       [0, 1, 1, 0, 0.0],
                                                                       [0, 1, 1, 1, 1.0],
                                                                       [1, 0, 0, 0, 0.0],
                                                                       [1, 0, 0, 1, 1.0],
                                                                       [1, 0, 1, 0, 0.0],
                                                                       [1, 0, 1, 1, 1.0],
                                                                       [1, 1, 0, 0, 0.0],
                                                                       [1, 1, 0, 1, 1.0],
                                                                       [1, 1, 1, 0, 0.0],
                                                                       [1, 1, 1, 1, 1.0]],
                                                                      [dict_pit_probs[neighbors[0]],
                                                                       dict_pit_probs[neighbors[1]],
                                                                       dict_pit_probs[neighbors[2]]])
            else:  # four neighbors
                dict_breeze_probs[cell] = ConditionalProbabilityTable([[0, 0, 0, 0, 0, 1.0],
                                                                       [0, 0, 0, 0, 1, 0.0],
                                                                       [0, 0, 0, 1, 0, 0.0],
                                                                       [0, 0, 0, 1, 1, 1.0],
                                                                       [0, 0, 1, 0, 0, 0.0],
                                                                       [0, 0, 1, 0, 1, 1.0],
                                                                       [0, 0, 1, 1, 0, 0.0],
                                                                       [0, 0, 1, 1, 1, 1.0],
                                                                       [0, 1, 0, 0, 0, 0.0],
                                                                       [0, 1, 0, 0, 1, 1.0],
                                                                       [0, 1, 0, 1, 0, 0.0],
                                                                       [0, 1, 0, 1, 1, 1.0],
                                                                       [0, 1, 1, 0, 0, 0.0],
                                                                       [0, 1, 1, 0, 1, 1.0],
                                                                       [0, 1, 1, 1, 0, 0.0],
                                                                       [0, 1, 1, 1, 1, 1.0],
                                                                       [1, 0, 0, 0, 0, 0.0],
                                                                       [1, 0, 0, 0, 1, 1.0],
                                                                       [1, 0, 0, 1, 0, 0.0],
                                                                       [1, 0, 0, 1, 1, 1.0],
                                                                       [1, 0, 1, 0, 0, 0.0],
                                                                       [1, 0, 1, 0, 1, 1.0],
                                                                       [1, 1, 0, 0, 0, 0.0],
                                                                       [1, 1, 0, 0, 1, 1.0],
                                                                       [1, 0, 1, 1, 0, 0.0],
                                                                       [1, 0, 1, 1, 1, 1.0],
                                                                       [1, 1, 0, 1, 0, 0.0],
                                                                       [1, 1, 0, 1, 1, 1.0],
                                                                       [1, 1, 1, 0, 0, 0.0],
                                                                       [1, 1, 1, 0, 1, 1.0],
                                                                       [1, 1, 1, 1, 0, 0.0],
                                                                       [1, 1, 1, 1, 1, 1.0]],
                                                                      [dict_pit_probs[neighbors[0]],
                                                                       dict_pit_probs[neighbors[1]],
                                                                       dict_pit_probs[neighbors[2]],
                                                                       dict_pit_probs[neighbors[3]]])

        # Create states
        pit_states = {}
        for cell in all_cells:
            pit_states[cell] = State(dict_pit_probs[cell])

        breeze_cpd_states = {}
        for cell in all_cells:
            breeze_cpd_states[cell] = State(dict_breeze_probs[cell])

        # Model
        model_pits = BayesianNetwork("model_pits_breezes")

        # Add states
        for cell in all_cells:
            model_pits.add_state(pit_states[cell])
        for cell in all_cells:
            model_pits.add_state(breeze_cpd_states[cell])

        # Add edges
        for cell in all_cells:
            for n in dict_neighbors[cell]:
                model_pits.add_edge(pit_states[n], breeze_cpd_states[cell])

        model_pits.bake()
        return model_pits

    def select_action(self, percept):

        # List of all locations
        all_cells = list_all_locations(self.grid_width, self.grid_height)

        # Dictionary where keys and values are cells and their neighbors respectively
        dict_neighbors = {cell: cell.adjacent_cells(self.grid_width, self.grid_height) for cell in all_cells}

        # Update agent's variables
        visiting_new_location = self.agent_state.location not in self.visited_locations
        if visiting_new_location:
            self.visited_locations.add(self.agent_state.location)
        if percept.breeze:
            self.breeze_locations.add(self.agent_state.location)
        if percept.stench:
            self.stench_locations.add(self.agent_state.location)
        new_heard_scream = self.heard_scream or percept.scream
        self.heard_scream = new_heard_scream
        self.perceives_glitter = percept.glitter
        self.perceives_bump = percept.bump

        board_tensor = self.encode_belief_state()  # encode belief state
        if self.collector is not None:  # record the state if collecting experience
            self.collector.record_state(state=board_tensor)

        # self.show() # print the agent_state, beeline_action_list and other details before selecting the action

        # Predict wumpus probabilities for each cell if visiting a new location or if just shot an arrow and killed the wumpus

        update_wumpus_probs = visiting_new_location or (not visiting_new_location and percept.scream)
        if update_wumpus_probs:
            if new_heard_scream:  # if wumpus is not alive, all probabilities are 0
                new_inferred_wumpus_probs = {cell: 0.0 for cell in all_cells}
            else:  # create a prob model and perform inference
                model_wumpus = self.create_model_wumpus()

                # Observations of wumpus and stenches
                observations_wumpus = [None]
                for cell in all_cells:
                    if cell in self.visited_locations:
                        observations_wumpus.append(False)
                    else:
                        observations_wumpus.append(None)
                for cell in all_cells:
                    if cell in self.stench_locations:
                        observations_wumpus.append(True)
                    elif cell not in self.visited_locations:
                        observations_wumpus.append(None)
                    else:  # a visited location but no stench was observed
                        observations_wumpus.append(False)

                # Compute the probabilities of wumpus
                predict_wumpus_probs = model_wumpus.predict_proba([observations_wumpus])
                new_inferred_wumpus_probs = predict_wumpus_probs[0][0].parameters[0]
            self.inferred_wumpus_probs = new_inferred_wumpus_probs  # update agent's inferred_wumpus_probs
        else:
            new_inferred_wumpus_probs = self.inferred_wumpus_probs

        # Predict probabilities of there being a pit at each cell
        # Create a prob model and perform inference if visiting a new location

        update_pit_probs = visiting_new_location
        if update_pit_probs:
            model_pits = self.create_model_pits()

            # Observations of pits and breezes
            observations_pits = []
            for cell in all_cells:
                if cell in self.visited_locations:
                    observations_pits.append(False)
                else:
                    observations_pits.append(None)
            for cell in all_cells:
                if cell in self.breeze_locations:
                    observations_pits.append(True)
                elif cell not in self.visited_locations:
                    observations_pits.append(None)
                else:  # a visited location but no breeze was observed
                    observations_pits.append(False)

            # Compute the new pit probabilities
            predict_pit_probs = model_pits.predict_proba([observations_pits])
            new_inferred_pit_probs = {}
            for i, cell in enumerate(all_cells):
                if isinstance(predict_pit_probs[0][i], Distribution):
                    new_inferred_pit_probs[cell] = predict_pit_probs[0][i].parameters[0][True]
                else:  # there was observation of False at this cell
                    new_inferred_pit_probs[cell] = 0.0
            self.inferred_pit_probs = new_inferred_pit_probs  # update agent's inferred_pit_probs
        else:
            new_inferred_pit_probs = self.inferred_pit_probs

        # Find safe locations where probabilities of wumpus and pits are lower than the tolerance value

        def safe_locations_list(tolerance, locations_list, pit_probs, wumpus_probs):
            safe_locations = [loc for loc in locations_list if
                              (pit_probs[loc] < tolerance and wumpus_probs[loc] < tolerance)]
            return safe_locations

        # Safe locations for beeline home or to reach a new location
        safe_locations_beeline = safe_locations_list(0.01, all_cells, new_inferred_pit_probs, new_inferred_wumpus_probs)

        # Safe locations to explore the grid
        safe_locations_search = safe_locations_list(0.4, all_cells, new_inferred_pit_probs, new_inferred_wumpus_probs)

        # print("safe_locations(tol=0.01):", safe_locations_beeline)
        # print("safe_locations(tol=0.4):", safe_locations_search)

        # Safe locations adjacent to the agent's location (tolerance=0.4)
        adjacent_safe_locations = [loc for loc in
                                   self.agent_state.location.adjacent_cells(self.grid_width, self.grid_height) \
                                   if loc in safe_locations_search]

        # Locations where prob of wumpus is greater than 0.49 (agent can try to shoot an arrow there)
        likely_wumpus_locations = [loc for loc in all_cells if new_inferred_wumpus_probs[loc] > 0.49]
        # Locations where prob of wumpus is greater than 0.49 that can be reached via cells in safe_locations_beeline
        reachable_likely_wumpus_locations = [loc for loc in likely_wumpus_locations \
                                             if any(
                neighbor in safe_locations_beeline for neighbor in dict_neighbors[loc])]

        # Select the next action

        if self.agent_state.has_gold:  # agent with gold
            if self.agent_state.location == Coords(0, 0):  # climb with gold
                return (self, Action.climb())
            else:  # beeline home with gold
                beeline_home_plan = self.construct_beeline_plan(Coords(0, 0), safe_locations_beeline) \
                    if self.beeline_action_list == [] else self.beeline_action_list
                (new_agent, beeline_action) = self.beeline(beeline_home_plan)
                return (new_agent, beeline_action)
        else:  # agent without gold
            if percept.glitter:  # grab the gold if glitter
                new_agent = copy.deepcopy(self)
                new_agent.agent_state.has_gold = True
                return (new_agent, Action.grab())
            elif self.beeline_action_list != []:  # continue beelining to reach a new location / get home without gold / shoot
                (new_agent, beeline_action) = self.beeline(self.beeline_action_list)
                return (new_agent, beeline_action)
            elif reachable_likely_wumpus_locations != [] and self.agent_state.has_arrow:  # shoot an arrow at a likely wumpus loc
                target_location = random.choice(reachable_likely_wumpus_locations)
                locations_beeline_shoot = safe_locations_beeline.copy()
                locations_beeline_shoot.append(target_location)  # add the target location to locations for beelining
                beeline_shoot_plan = self.construct_beeline_plan(target_location, locations_beeline_shoot)
                del beeline_shoot_plan[-1]  # remove the last action which is a move forward to a likely wumpus location
                beeline_shoot_plan.append(Action.shoot())  # add the shoot action to the end of the list
                (new_agent, beeline_action) = self.beeline(beeline_shoot_plan)
                return (new_agent, beeline_action)
            elif self.agent_state.location == Coords(0, 0) and adjacent_safe_locations == []:  # unsafe to explore
                if not percept.breeze and self.agent_state.has_arrow:  # try to kill wumpus if low probability of pits around
                    new_agent = copy.deepcopy(self)
                    new_agent.agent_state = new_agent.agent_state.use_arrow()
                    return (new_agent, Action.shoot())
                else:  # climb without gold
                    return (self, Action.climb())
            else:  # search for gold
                # Not visited locations adjacent to all previously visited locations
                potential_visit_locations_set = {adj_loc for loc in self.visited_locations \
                                                 for adj_loc in loc.adjacent_cells(self.grid_width, self.grid_height) \
                                                 if adj_loc not in self.visited_locations}
                potential_visit_locations_list = list(potential_visit_locations_set)
                safe_potential_visit_locations = [loc for loc in potential_visit_locations_list if
                                                  loc in safe_locations_search]
                if safe_potential_visit_locations != []:  # new safe locations exist; choose one and create a beeline plan to it
                    search_coords_list = []
                    search_wumpus_probs = []
                    for loc in safe_potential_visit_locations:
                        search_coords_list.append(loc)
                        search_wumpus_probs.append(new_inferred_wumpus_probs[loc])
                    next_location_index = search_wumpus_probs.index(
                        min(search_wumpus_probs))  # find cell with min wumpus prob
                    next_location = search_coords_list[next_location_index]
                    locations_beeline_search = safe_locations_beeline.copy()
                    locations_beeline_search.append(next_location)  # add the chosen location to locations for beelining
                    beeline_search_plan = self.construct_beeline_plan(next_location, locations_beeline_search)
                    (new_agent, beeline_action) = self.beeline(beeline_search_plan)
                    return (new_agent, beeline_action)
                else:  # no new safe locations to explore, beeline home without gold
                    beeline_home_plan = self.construct_beeline_plan(Coords(0, 0), safe_locations_beeline)
                    beeline_home_plan.append(Action.climb())
                    (new_agent, beeline_action) = self.beeline(beeline_home_plan)
                    return (new_agent, beeline_action)

    @classmethod
    def new_agent(cls, grid_width, grid_height, pit_prob):
        return ProbAgent(grid_width, grid_height, pit_prob, AgentState(), [], set(), set(), set(), False, {}, {}, False,
                         False)

    # Encode belief state using 13 feature planes (each plane is a grid_height x grid_width matrix)
    # The state shape is (13, grid_height, grid_width)

    def encode_belief_state(self):
        board_tensor = np.zeros((13, self.grid_height, self.grid_width))
        all_cells = list_all_locations(self.grid_width, self.grid_height)

        # The first plane has a 1 for agent's location and 0s for other locations
        board_tensor[0][self.agent_state.location.y][self.agent_state.location.x] = 1

        for cell in all_cells:
            if cell in self.visited_locations:
                board_tensor[1][cell.y][cell.x] = 1  # 1s for visited locations
            if cell in self.stench_locations:
                board_tensor[2][cell.y][cell.x] = 1  # 1s for stench locations
            if cell in self.breeze_locations:
                board_tensor[3][cell.y][cell.x] = 1  # 1s for breeze locations

        if self.agent_state.orientation == Orientation.north:  # a plane filled with 1s if Orientation.north
            board_tensor[4] = 1
        elif self.agent_state.orientation == Orientation.south:  # a plane filled with 1s if Orientation.south
            board_tensor[5] = 1
        elif self.agent_state.orientation == Orientation.east:  # a plane filled with 1s if Orientation.east
            board_tensor[6] = 1
        else:  # a plane filled with 1s if Orientation.west
            board_tensor[7] = 1

        if self.agent_state.has_gold:  # a plane filled with 1s if agent has gold, and 0s otherwise
            board_tensor[8] = 1
        if self.perceives_glitter:  # a plane filled with 1s if agent perceives glitter, and 0s otherwise
            board_tensor[9] = 1
        if self.agent_state.has_arrow:  # a plane filled with 1s if agent has arrow, and 0s otherwise
            board_tensor[10] = 1
        if self.heard_scream:  # a plane filled with 1s if wumpus is not alive, and 0s otherwise
            board_tensor[11] = 1
        if self.perceives_bump:  # a plane filled with 1s if agent perceives bump, and 0s otherwise
            board_tensor[12] = 1

        return board_tensor


if __name__ == '__main__':
    n_games = 100
    total_moves = 0
    n_games_reward = 0
    wins = 0

    collector = ExperienceCollector()

    for i in range(n_games):
        agent = ProbAgent.new_agent(4, 4, 0.2)
        (env, percept) = Environment.new_game(4, 4, 0.2, True)
        total_reward = 0
        num_moves = 0

        while not percept.is_terminated:
            agent.set_collector(collector)
            (agent, next_action) = agent.select_action(percept)
            next_action_int = encode_action_to_int(next_action)  # encode action to int
            collector.record_action(next_action_int)  # add encoded action to collector
            (env, percept) = env.apply_action(next_action)
            collector.record_reward(percept.reward)  # add reward to collector
            total_reward += percept.reward
            num_moves += 1

        if agent.agent_state.has_gold:
            wins += 1
        n_games_reward += total_reward
        total_moves += num_moves

    print("Number of games: ", n_games)
    print("Total number of moves: ", total_moves)
    print("n_games_reward:", n_games_reward)
    print("avg_reward_per_game: %.2f" % (n_games_reward / n_games))
    print("win_percent: %.2f" % (wins / n_games))

