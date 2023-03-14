import gym
from gym import spaces
from time import sleep
import numpy as np

from utils.monitor import Monitor
from utils.unit_matcher import *

from scheduler.scheduler import Scheduler

class RealKubeEnv(gym.Env):
    def __init__(self):
        super(RealKubeEnv, self).__init__()
        self.monitor = Monitor()
        self.scheduler = Scheduler()

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
        self.pod_observation_space = spaces.Box(low=0, high=100, shape=(2,), dtype=int)

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
                "cpu": 100 - _util["cpu"][0] / _util["cpu"][1] * 100,
                "memory": 100 - _util["memory"][0] / _util["memory"][1] * 100
            }

        # AvgUtil = mean of cpu and mem utilization of all node
        avg_cpu = round(np.mean([util[node]["cpu"] for node in self.node_list]),3)
        avg_mem = round(np.mean([util[node]["memory"] for node in self.node_list]),3)
        avg_util = round((avg_cpu + avg_mem) / 2 , 3)
        if debug:
            print("AvgCPU: " + str(avg_cpu))
            print("AvgMemory: " + str(avg_mem))
            print("AvgUtil: " + str(avg_util))

        # ImBalance = summation of standard deviation of each resource in all nodes
        std_cpu = round(np.std([util[node]["cpu"] for node in self.node_list]),3)
        std_mem = round(np.std([util[node]["memory"] for node in self.node_list]),3)
        imbalance = std_cpu + std_mem
        if debug:
            print("StdCPU: " + str(std_cpu))
            print("StdMem: " + str(std_mem))
            print("Imbalance: " + str(imbalance))

        # Reward = a*AvgUtil - b*ImBalance
        a = 1
        b = 1
        reward = round(a * avg_util - b * imbalance, 3)

        print("Reward: " + str(reward))

        return reward
    
    def observe_state(self, debug=False):
        # Node cpu, memory capacity
        node_cpu_cap = self.monitor.get_node_rsrc(self.node_list[0])["cpu"][1]
        node_memory_cap = self.monitor.get_node_rsrc(self.node_list[0])["memory"][1]
        if debug:
            print("Node CPU Capacity: " + str(node_cpu_cap))
            print("Node Memory Capacity: " + str(node_memory_cap))

        # Get the most recent pending pod
        pending_pods_names = self.monitor.get_pending_pods()[0]
        if debug:
            print("Pending Pod: " + str(pending_pods_names))
        if len(pending_pods_names) == 0:
            pending_pod_obs = np.array([0, 0])
        else:
            pending_pod_name = pending_pods_names[0]
            if debug:
                print("Pending Pod Name: " + str(pending_pod_name))
            pending_pod_rqsts = self.monitor.get_pod_rqsts(pending_pod_name)

            if debug:
                print("Pending Pod Requests: " + str(pending_pod_rqsts))

            pending_pod_cpu_rqst = max(int(pending_pod_rqsts["cpu"] / node_cpu_cap * 100), 1)
            pending_pod_memory_rqst = max(int(pending_pod_rqsts["memory"] / node_memory_cap * 100), 1)

            pending_pod_obs = np.array([pending_pod_cpu_rqst, pending_pod_memory_rqst])
            if debug:
                print("Pending Pod Observation: " + str(pending_pod_obs))

        # Get the resource utilization of each node
        node_obs = []
        for node in self.node_list:
            node_rsrc = self.monitor.get_node_rsrc(node)

            node_cpu_util = node_rsrc["cpu"][2]
            node_memory_util = node_rsrc["memory"][2]

            node_obs.append([node_cpu_util, node_memory_util])

        if debug:
            print("Node Observation: " + str(node_obs))

        state = (node_obs, pending_pod_obs)

        if debug:
            print("State: " + str(state))

        return state

    def step(self, action):
        # Take an action in the environment based on the provided action
        pod_name, node_name = action
        self.scheduler.scheduling(pod_name, node_name)

        sleep(10)

        # Observe the state of the environment
        state = self.observe_state()

        # Calculate the reward
        reward = self.calc_reward()

        # Check if the episode is done ===> Set to False for now
        done = False

        # Return the state, reward, and done
        return state, reward, done, {}

    def reset(self):
        pass




