import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import pandas as pd
from parameters import *
results_folder = "./RESULTS/"


import os
rezs = {}
agent_types = [InfiniteFixedCureAgent,CureAgent,MutationBlindNanoAgent]




def plot_inf(value):
    inf_dir =  "/home/tara/CancerModel/InfiniteResults"
    for setting in [1,2,3,4,5]:
        dfs = []
        for i in range(SAMPLE_SIZE):
            df = pd.read_csv(os.path.join(inf_dir,"rez_InfiniteFixedCureAgent_%s-%sSTEPS-%s.csv"%(setting,STEPS,i)))
            dfs.append(df)
        avg = pd.concat(dfs).groupby(level=0).mean()
        print(df.columns)
        plt.plot(df[value],label="%s" %setting)
    plt.title("%s for different InfniteFixedCureAgent settings" %value)
    plt.ylabel("%s" %value)
    plt.xlabel("Steps")


def plot_all_agent_types(value):
    for at in agent_types:
        plt.plot(rezs[at][value],label = at.__name__)

for agent_type in agent_types:
    dfs=[]
    for i in range(SAMPLE_SIZE):
        dfs.append(pd.read_csv(os.path.join(results_folder,"rez_%s-%sSTEPS-%s.csv"%(agent_type.__name__,STEPS,i))))
    rezs[agent_type] = pd.concat(dfs).groupby(level=0).mean()

#plot_inf("CancerCellNumber")

plot_all_agent_types("CancerCellNumber")
plt.title("CC number for all agent types and InfiniteFixedCureAgent settings")
plt.legend()
plt.show()

        
for at in agent_types:
    plt.plot(rezs[at].FitnessFunction,label = at.__name__)

plt.title("Fitness Function for all Nano Agent types")
plt.xlabel("Steps")
plt.ylabel("Fitness Function")
plt.legend()
plt.show()


for at in agent_types:
    plt.plot(rezs[at]["CancerStemCell Number"],label = at.__name__)
plt.legend()
plt.title("CancerStemCell number for all Nano Agent types")
plt.xlabel("Steps")
plt.ylabel("CancerStemCell number")
plt.show()


plt.plot(rezs[CureAgent].PopulationHeterogenity,label="Population Heterogenity")
plt.plot(rezs[CureAgent].CancerHeterogenity,label="Cancer Heterogenity")
plt.title("CureAgent Heterogenity")
plt.xlabel("Steps")

plt.legend()
plt.show()

for at in agent_types:
    plt.plot(rezs[at].MutationAmount,label = at.__name__)
plt.title("MutationAmount for all Nano Agent Types")
plt.xlabel("Steps")
plt.ylabel("Total Number the Cancer Mutated")
plt.legend()
plt.show()


for at in agent_types:
    plt.plot(rezs[at]["CancerStemCell Number"],label = "CancerStemCell Number")
    plt.plot(rezs[at]["CSC Specialized Agents"],label = "CSC Specialized Agents")
    plt.title("CSC growth VS CSC Specialized Agents : %s "%at.__name__)
    plt.xlabel("Steps")
    plt.legend()
    plt.show()




