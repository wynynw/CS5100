from gym.envs.registration import register

register(
	id = 'maze-v0',
	entry_point = 'MazeEnv.MazeEnv:Maze'
)
