import bbSA
import random

# Modify NUM_NODES and CONFIGS when testing. CONFIGS must be initialized with valid constraints.
NUM_NODES = 4
bbSA.NUM_NODES = NUM_NODES
HASWELL_KNL = "haswell"
MAX_TASKS_PER = 32 if HASWELL_KNL == "haswell" else 272
SSD_SIZE = 20

configs = {"num_tasks_per_node" : 8,
          "capacity" : 12,
          "transfer_size" : 8,
          "block_size" : 1024}
#bbSA.generateIOR(configs)
bbSA.jitter(configs, "block_size")

def test_neighbor_jitter(configs, reps):

    for i in range(reps):
        print(i)
        key = random.choice(list(configs.keys()))
        configs[key] = bbSA.neighbor_jitter(configs, key)
        total_tasks = configs["num_tasks_per_node"] * NUM_NODES
        assert configs["capacity"] >= (total_tasks * configs["block_size"]/ 1024 / SSD_SIZE)
        assert configs["num_tasks_per_node"] <= MAX_TASKS_PER
        assert configs["num_tasks_per_node"] > 0
        assert configs["transfer_size"] <= configs["block_size"]
        assert configs["block_size"] % configs["transfer_size"] == 0
        assert configs["block_size"] % 8 == 0
        assert configs["block_size"] / 1024 <= (SSD_SIZE * configs["capacity"]) / total_tasks
    print("All jitter tests passed")

def test_jitter(configs, reps):

    for i in range(reps):
        print(i)
        key = random.choice(list(configs.keys()))
        configs[key] = bbSA.jitter(configs, key)
        total_tasks = configs["num_tasks_per_node"] * NUM_NODES
        assert configs["capacity"] >= (total_tasks * configs["block_size"]/ 1024 / SSD_SIZE)
        assert configs["num_tasks_per_node"] <= MAX_TASKS_PER
        assert configs["num_tasks_per_node"] > 0
        assert configs["transfer_size"] <= configs["block_size"]
        assert configs["block_size"] % configs["transfer_size"] == 0
        assert configs["block_size"] % 8 == 0
        assert configs["block_size"] / 1024 <= (SSD_SIZE * configs["capacity"]) / total_tasks
    print("All jitter tests passed")

def test_neighbor(configs):
    new_config = bbSA.neighbor(configs)
    print(new_config)


if __name__ == "__main__":
    test_jitter(configs, 10000)
    #bbSA.getSpeed(configs)
#test_neighbor(configs)
#bbSA.generateIOR(configs)
#print(configs.values())
#bbSA.logData(configs, [10000, 20000, 3000, 4000])

