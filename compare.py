import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import pandas as pd
from parameters import *
rezs = {}
agent_types = [InfiniteFixedCureAgent,CureAgent,MutationBlindNanoAgent]

for agent_type in agent_types:
    dfs=[]
    for i in range(SAMPLE_SIZE):
        dfs.append(pd.read_csv("rez_%s-%sSTEPS-%s.csv"%(agent_type.__name__,STEPS,i)))
    rezs[agent_type] = pd.concat(dfs).groupby(level=0).mean()

        
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
plt.ylabel("CancerStemCell Number")

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
    plt.plot(rezs[at]["CancerStemCell Number"],label = at.__name__)
    plt.plot(rezs[at]["CSC Specialized Agents"],label = at.__name__)
    plt.title("CSC growth VS CSC Specialized Agents : %s "%at.__name__)
    plt.xlabel("Steps")
    plt.legend()
    plt.show()




