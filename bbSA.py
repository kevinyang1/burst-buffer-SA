from __future__ import division
import subprocess
import random
import math
import csv


SBATCH_PATH = "/global/homes/k/k_yang/ior/src"
SBATCH_TEMPLATE_PATH = "/Users/k_yang/Documents/IORtemplate.txt"
SBATCH_NEW_SCRIPT_PATH = "/Users/k_yang/Documents/newIOR.sbatch"
LOG_PATH = "/Users/k_yang/Documents/test_log.csv"

SSD_SIZE = 20
DW_BLOCK_SIZE = 8 #8 MiB
NUM_NODES = 1
HASWELL_KNL = "haswell"
MAX_TASKS_PER = 32 if HASWELL_KNL == "haswell" else 272
CPUS_PER = 2 if HASWELL_KNL == "haswell" else 4
DATA_INDICES = [2, 27, 6, 31]

def generateIOR(configs):
    with open(SBATCH_TEMPLATE_PATH, 'r') as template:
        text = template.read()
        text = text.format(NUM_NODES,
                      NUM_NODES * configs["num_tasks_per_node"],
                      configs["num_tasks_per_node"],
                      HASWELL_KNL,
                      str(configs["capacity"] * SSD_SIZE) + "GiB",
                      str(configs["transfer_size"]) + "M",
                      str(configs["block_size"]) + "G")
    with open(SBATCH_NEW_SCRIPT_PATH, 'w+') as destination:
        destination.write(text)

def neighbor(configs):
    rand_key = random.choice(list(configs.keys()))
    new_config = configs.copy()
    new_config[rand_key] = jitter(configs, rand_key)
    return new_config

def jitter(configs, key):
    new_val = configs[key]
    total_tasks = configs["num_tasks_per_node"] * NUM_NODES
    loop_count = 0
    while configs[key] == new_val and loop_count < 5:
        if key == "num_tasks_per_node":
            max_constraint = math.floor((configs["capacity"] * SSD_SIZE) / (configs["block_size"] * NUM_NODES))
            min_of_max = min(MAX_TASKS_PER, max_constraint)
            if (abs(new_val - min_of_max)) <= 1:
                return new_val
            new_val = random.choice(range(1, min_of_max))
        elif key == "capacity":
            new_val = random.choice(range(int(math.ceil((total_tasks * configs["block_size"]) / SSD_SIZE)), NUM_NODES * MAX_TASKS_PER))
        elif key == "transfer_size":
            block_size_MIB = int(configs["block_size"] * 1024)
            possible_transfer_size = list(range(1, block_size_MIB))
            new_val = random.choice(possible_transfer_size)
            while block_size_MIB % new_val != 0:
                new_val = random.choice(possible_transfer_size)
        else:
            #Following branches make sure that block size is a multiple of DW_BLOCK_SIZE and transfer_size
            largest_trans_multiple = int(math.floor((((SSD_SIZE * configs["capacity"]) / total_tasks) * 1024) / configs["transfer_size"])) #
            if configs["transfer_size"] % 8 == 0:
                new_val = random.randrange(1, largest_trans_multiple + 1) * configs["transfer_size"]
            elif configs["transfer_size"] % 4 == 0:
                new_val = random.randrange(1, largest_trans_multiple // 2 + 1) * configs["transfer_size"] * 2
            elif configs["transfer_size"] % 2 == 0:
                new_val = random.randrange(1, largest_trans_multiple // 4 + 1) * configs["transfer_size"] * 4
            else:
                new_val = random.randrange(1, largest_trans_multiple // 8 + 1) * configs["transfer_size"] * 8
            new_val /= 1024.0
        loop_count += 1
    return new_val

def getSpeed(configs):
    generateIOR(configs)
    job_number = subprocess.getoutput("sbatch " + SBATCH_NEW_SCRIPT_PATH).split()[3]
    job_status = subprocess.getoutput("squeue | grep k_yang")

    while job_status:
        job_status = subprocess.getoutput("squeue | grep k_yang")

    with open ("slurm-{0}.out".format(job_number)) as outputfile:
        text = outputfile.read()

    output_list = text.split()
    data_index = output_list[::-1].index("write")
    output_list = output_list[-data_index:]
    collected_data = [output_list[i] for i in DATA_INDICES]

    logData(configs, collected_data)

    return float(collected_data[0]) + float(collected_data[1])
    # TODO: Save data and corresponding configurations as csv

def logData(configs, slurm_data):
    log_data = [NUM_NODES,
                NUM_NODES * configs["num_tasks_per_node"],
                configs["num_tasks_per_node"],
                1 if HASWELL_KNL == "haswell" else 0,
                configs["capacity"] * SSD_SIZE,
                configs["transfer_size"],
                configs["block_size"] * 1024,
                CPUS_PER,
                slurm_data[0],
                slurm_data[1],
                slurm_data[2],
                slurm_data[3]
                ]
    with open(LOG_PATH, 'a', newline='') as logcsv:
        writer = csv.writer(logcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(log_data)

def simulatedAnneal(alpha, configs):
    """
    :param alpha: Learning rate, must be less than 1
    :param configs: Dictionary containing keys num_tasks_per_node, capacity, transfer_size, block_size
    :return: optimum configurations, associated speed
    """
    temp = 1.0
    num_iterations_stuck = 0
    curr_speed = getSpeed(configs)

    while num_iterations_stuck < 30 and temp > 0.00001:
        new_config = neighbor(configs)
        new_speed = getSpeed(new_config)
        if new_speed > curr_speed:
            configs = new_config
            curr_speed = new_speed
        elif math.exp((new_speed - curr_speed) / temp) > random.random():
            configs = new_config
            curr_speed = new_speed
        temp *= alpha

    return curr_speed, configs



