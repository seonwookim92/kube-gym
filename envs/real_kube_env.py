import gym
from gym import spaces
from time import sleep
import numpy as np

from utils.monitor import Monitor
from utils.unit_matcher import *

class RealKubeEnv(gym.Env):
    def __init__(self):
        super(RealKubeEnv, self).__init__()
        self.monitor = Monitor()

        # Nodes
        self.node_list = self.monitor.get_nodes()[0]
        # If there are controlplane and node-0, remove them
        if "controlplane" in self.node_list:
            self.node_list.remove("controlplane")
        if "node-0" in self.node_list:
            self.node_list.remove("node-0")
        self.num_nodes = len(self.node_list)

        # Initialize node observation space Should be the number of nodes x 3 matrix
        self.node_observation_space = spaces.Box(low=0, high=100, shape=(self.num_nodes, 3), dtype=int)

        # Initialize the most recent pending pod observation space
        self.pod_observation_space = spaces.Box(low=0, high=100, shape=(1,), dtype=int)

        # Initialize the observation space
        self.observation_space = spaces.Tuple((self.node_observation_space, self.pod_observation_space))

        # Map node name to index
        self.idx_to_node = {}
        for i, node_name in enumerate(self.node_list):
            self.idx_to_node[i] = node_name

        # Initialize the action space
        self.action_space = spaces.Discrete(self.num_nodes)

    def calc_reward(self, debug=False):
        # Utilization of resources on each node
        util = {}
        for node in self.node_list:
            _util = self.monitor.get_node_rsrc(node)
            if debug:
                print(_util)
            util[node] = {
                "cpu": 1 - _util["cpu"][0] / _util["cpu"][1] * 100,
                "memory": 1 - _util["memory"][0] / _util["memory"][1] * 100
            }

        # AvgUtil = mean of cpu and mem utilization of all node
        avg_cpu = -np.mean([util[node]["cpu"] for node in self.node_list])
        avg_mem = -np.mean([util[node]["memory"] for node in self.node_list])
        avg_util = (avg_cpu + avg_mem) / 2
        if debug:
            print("AvgCPU: " + str(avg_cpu))
            print("AvgMemory: " + str(avg_mem))
            print("AvgUtil: " + str(avg_util))

        # ImBalance = summation of standard deviation of each resource in all nodes
        std_cpu = np.std([util[node]["cpu"] for node in self.node_list])
        std_mem = np.std([util[node]["memory"] for node in self.node_list])
        imbalance = std_cpu + std_mem
        if debug:
            print("StdCPU: " + str(std_cpu))
            print("StdMem: " + str(std_mem))
            print("Imbalance: " + str(imbalance))

        # Reward = a*AvgUtil - b*ImBalance
        a = 1
        b = 1
        reward = a * avg_util - b * imbalance

        print("AvgUtil: " + str(avg_util))

        return reward



    def step(self, action):
        pass

    def reset(self):
        pass




