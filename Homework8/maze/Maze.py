import gym
import MazeEnv
import random
import time
import numpy as np

# Hyperparameters
#alpha = 0.1
gamma = 0.8

env=gym.make('maze-v0')
q_table = np.zeros((6, 6))
reward_table = np.array([[-1, -1, -1, -1, 0, -1],
                        [-1, -1, -1, 0, -1, 100],
                        [-1, -1, -1, 0, -1, -1],
                        [-1, 0, 0, -1, 0, -1],
                        [0, -1, -1, 0, -1, 100],
                       [-1, 0, -1, -1, 0, 100]])

print('Q_table',q_table)
print('reward_table',reward_table)


reward_final=0
random_state = np.random.RandomState(100)
eps = 0.06
curr_state=0
env.reset()
flag=False
for i in range(100):
    states = list(range(6))
    random_state.shuffle(states)
    if flag == False:
            #action = np.argmax(q_table[state])
            #env.render()
            legal = reward_table[env.state] >= 0
            actions = np.array(list(range(6)))
            legal_actions = actions[legal == True]
            print('legal actions in', env.state, legal_actions)
            if random_state.rand() < eps:
                action = int(legal_actions[0])
            else:
                if np.sum(q_table[env.state]) > 0:
                    action = np.argmax(q_table[env.state])
                else:
                    action = env.actions[int(random.random() * len(env.actions))]
            next_state, r, is_terminal, info = env.step(action)
            if r >0:
                reward_final += r
            # print("now agent in " + str(env.state), ", next step is go " + str(action) + " to " + str(next_state))
            # print("reward is:", reward_final)
            reward = reward_table[env.state, next_state]
            compute = reward + gamma * max(q_table[next_state, :])
            q_table[env.state, next_state] = compute
            normalize = q_table[env.state][q_table[env.state] > 0] / np.argmax(q_table[env.state])
            q_table[env.state][q_table[env.state] > 0] = normalize
            if is_terminal == True:
                curr_state=next_state
                flag=True

print('Final state:',curr_state)
print("Final reward:", reward_final)
print('Final Q_table:')
print(q_table)
env.close()

