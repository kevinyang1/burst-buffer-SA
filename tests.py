from __future__ import division
import bbSA
import random

NUM_NODES = 1
HASWELL_KNL = "haswell"
MAX_TASKS_PER = 32 if HASWELL_KNL == "haswell" else 272
SSD_SIZE = 20

configs = {"num_tasks_per_node" : 8,
          "capacity" : 28,
          "transfer_size" : 8,
          "block_size" : 0.5}
#bbSA.generateIOR(configs)
bbSA.jitter(configs, "block_size")

def test_jitter(configs, reps):

    for i in range(reps):
        key = random.choice(list(configs.keys()))
        configs[key] = bbSA.jitter(configs, key)
        total_tasks = configs["num_tasks_per_node"] * NUM_NODES
        block_size_MIB = configs["block_size"] * 1024
        assert configs["capacity"] > (total_tasks * configs["block_size"] / SSD_SIZE)
        assert configs["num_tasks_per_node"] < MAX_TASKS_PER
        assert configs["num_tasks_per_node"] > 0
        assert configs["transfer_size"] <= block_size_MIB
        assert block_size_MIB % configs["transfer_size"] == 0
        assert block_size_MIB % 8 == 0
        assert configs["block_size"] < (SSD_SIZE * configs["capacity"]) / total_tasks
    print("All jitter tests passed")

def test_neighbor(configs):
    new_config = bbSA.neighbor(configs)
    print(new_config)
test_jitter(configs, 1000)
#bbSA.getSpeed(configs)
test_neighbor(configs)
#bbSA.generateIOR(configs)
print(configs.values())
bbSA.logData(configs, [10000, 20000, 3000, 4000])

