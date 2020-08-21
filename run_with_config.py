import toml
from rob_ev import *
import pandas as pd
from model import *
from multiprocessing import Process
config_fname = input("Type in configuration file name:")
config = toml.load(config_fname)

regime = int(input("""Do you want to:
0- Run CureAgent\n
1- Run MutationBlindNanoAgent\n
2- Run InfiniteFixedCureAgent\n
3- Run all
"""))

agents = [CureAgent,MutationBlindNanoAgent,InfiniteFixedCureAgent]
agents = [agents[regime]] if regime<3 else agents
print (agents)

for NA in  agents:
    print (NA.__name__)
    run_model_and_get_results(config)

