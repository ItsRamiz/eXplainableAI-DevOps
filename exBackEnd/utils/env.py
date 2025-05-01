from __future__ import annotations
import gymnasium as gym
from minigrid.core.constants import COLOR_NAMES
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Door, Goal, Key, Wall, Lava
from minigrid.manual_control import ManualControl
from minigrid.minigrid_env import MiniGridEnv
from minigrid.minigrid_env import MiniGridEnv
from minigrid.core.grid import Grid
from minigrid.core.world_object import Wall, Lava, Door, Key, Goal

# Function to load environment data from JSON
import json

def load_env_data(file_path='customEnvs/environment.json'):
    with open(file_path, 'r') as file:
        env_data = json.load(file)
    return env_data


class SimpleEnv(MiniGridEnv):
    def __init__(
            self,
            size=5,
            agent_start_pos=(1,1),
            agent_start_dir=0,
            custom_walls=None,
            custom_lava=None,
            custom_doors=None,
            custom_keys=None,
            custom_goals=None,
            max_steps: int | None = None,
            **kwargs,
    ):
        self.agent_start_pos = tuple(agent_start_pos) if agent_start_pos else None
        self.agent_start_dir = agent_start_dir

        self.custom_walls = custom_walls if custom_walls else []
        self.custom_lava = custom_lava if custom_lava else []
        self.custom_doors = custom_doors if custom_doors else []
        self.custom_keys = custom_keys if custom_keys else []
        self.custom_goals = custom_goals if custom_goals else []

        mission_space = MissionSpace(mission_func=self._gen_mission)

        if max_steps is None:
            max_steps = 4 * size ** 2

        super().__init__(
            mission_space=mission_space,
            grid_size=size,
            see_through_walls=True,
            max_steps=max_steps,
            **kwargs,
        )

    @staticmethod
    def _gen_mission():
        return "grand mission"

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)
        self.grid.wall_rect(0, 0, width, height)

        for wall in self.custom_walls:
            self.grid.set(*wall, Wall())

        for lava in self.custom_lava:
            self.grid.set(*lava, Lava())

        for door in self.custom_doors:
            color = door[3]
            locked = (door[2] == 'locked')
            self.grid.set(*door[:2], Door(color, is_locked=locked))

        # Ensure the start position is not occupied
        start_cell = self.grid.get(*self.agent_start_pos)
        if start_cell is not None:
            raise ValueError(f"Invalid agent start position at {self.agent_start_pos}. It overlaps with a {type(start_cell)}.")

        # Place other objects like keys, lava, etc., ensuring they don't overlap

        for key in self.custom_keys:
            self.grid.set(*key[:2], Key(key[2]))

        for goal in self.custom_goals:
            self.grid.set(*goal, Goal())

        self.agent_pos = self.agent_start_pos
        self.agent_dir = self.agent_start_dir
        self.mission = "Find the goal!"

def createCustomEnv(env_data, isTrain):
    env = SimpleEnv(
        size=env_data['custom_World_Width'],
        agent_start_pos=env_data['custom_Start_Pos'],
        custom_walls=env_data['custom_Walls'],
        custom_lava=env_data['custom_Lava'],
        custom_doors=env_data['custom_Doors'],
        custom_keys=env_data['custom_Keys'],
        custom_goals=env_data['custom_Goals'],
        render_mode="human" if not isTrain else None
    )
    print("Loaded Custom Environment")
    return env

def make_env(env_key, seed=None, render_mode=None, customEnv=0, isTrain=0):
    if customEnv == 0:
        env = gym.make(env_key, render_mode=render_mode)
        env.reset()
        return env
    else:
        #print("Creating Custom Environment")
        env_data = load_env_data()
        env = createCustomEnv(env_data, isTrain)
        env.reset()
        return env
