import gym
import numpy as np

class Maze(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 2
    }

    def __init__(self):
        self.viewer = None
        self.states = [0,1,2,3,4,5]

        self.terminate_states=[5]

        self.actions = [0,1,2,3,4,5]

        self.rewards=[[-1, -1, -1, -1, 0, -1],
                  [-1, -1, -1, 0, -1, 100],
                  [-1, -1, -1, 0, -1, -1],
                  [-1, 0, 0, -1, 0, -1],
                  [0, -1, -1, 0, -1, 100],
                  [-1, 0, -1, -1, 0, 100]]


    def step(self, action):
        state = self.state
        if state in self.terminate_states:
            return state, 0, True, {}
        r = self.rewards[state][action]
        if r < 0:
            next_state=state
        else:
            next_state=action
        self.state = next_state

        is_terminal = False

        if next_state in self.terminate_states:
            is_terminal = True

        return next_state, r, is_terminal,{}

    def reset(self):
        #self.state = self.states[int(random.random() * len(self.states))]
        self.state = 2
        return self.state

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

    def render(self, mode='human'):
        from gym.envs.classic_control import rendering
        screen_width = 500
        screen_height = 400

        if self.viewer is None:

            self.viewer = rendering.Viewer(screen_width, screen_height)

            #horizontal
            self.line1 = rendering.Line((125, 100), (400, 100))
            self.line21 = rendering.Line((100, 200), (175, 200))
            self.line22 = rendering.Line((225, 200), (400, 200))
            self.line3 = rendering.Line((100, 300), (275, 300))
            #vertical
            self.line4 = rendering.Line((100, 100), (100, 300))
            self.line5 = rendering.Line((200, 125), (200, 300))
            self.line61 = rendering.Line((300, 100), (300, 175))
            self.line62 = rendering.Line((300, 200), (300, 300))
            self.line7 = rendering.Line((400, 100), (400, 200))

            self.line1.set_color(0, 0, 0)
            self.line21.set_color(0, 0, 0)
            self.line22.set_color(0, 0, 0)
            self.line3.set_color(0, 0, 0)
            self.line4.set_color(0, 0, 0)
            self.line5.set_color(0, 0, 0)
            self.line61.set_color(0, 0, 0)
            self.line62.set_color(0, 0, 0)
            self.line7.set_color(0, 0, 0)

            self.viewer.add_geom(self.line1)
            self.viewer.add_geom(self.line21)
            self.viewer.add_geom(self.line22)
            self.viewer.add_geom(self.line3)
            self.viewer.add_geom(self.line4)
            self.viewer.add_geom(self.line5)
            self.viewer.add_geom(self.line61)
            self.viewer.add_geom(self.line62)
            self.viewer.add_geom(self.line7)

        if self.state is None:
            return None

        self.x = [250, 350, 250,
                  150, 350, 150]
        self.y = [250, 150, 150,
                  150, 350, 250]

        #agent
        self.viewer.draw_circle(18, color=(0.8, 0.6, 0.4)).add_attr(
            rendering.Transform(translation=(self.x[self.state - 1], self.y[self.state - 1])))

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

