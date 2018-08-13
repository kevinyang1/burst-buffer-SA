# burst-buffer-SA

This code runs a simulated annealing algorithm for IOR configuration optimization on the Cori Burst Buffer at the National Energy Research Scientific Computing Center (NERSC) and logs the data as a CSV. 

The algorithm changes four parameters: number of tasks per node, SSD capacity, transfer size, and block size. The number of nodes used is held constant. 

## Configuration

The code is pretty raw, and using it requires making changes to the code. In bbSA.py, there are a couple things that must be configured.
* USER : specify NERSC user name
* IOR_PATH : specify the location of your IOR executable
* NUM_NODES : specify number of nodes
* HASWELL_KNL : "haswell" for haswell, something else for "knl"
* initial_configs :
  * num_tasks_per_node : positive number, maximum 32 for haswell, 272 for KNL
  * capacity : burst buffer capacity requested / 20 GiB
  * transfer_size : IOR transfer size in MiB
  * block_size: IOR block size in MiB
* alpha: specifies rate at which simulated annealing temperature decays. 

The code also requires IORtemplate.txt to have at least 2 repetitions for each run. This is specified with **-i** flag.
Files should be placed in same directory as IOR.
  
## License

This code is not licensed for distribution. Do not distribute or reproduce. 
