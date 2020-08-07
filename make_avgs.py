import pandas as pd
import matplotlib.pyplot as plt
import os
from model import *
import seaborn as sns
sns.set()



def read_and_make_avg(fname_base,steps=1000,sample_size=200):
    STEPS = steps
    SAMPLE_SIZE=sample_size
    results_folder = "./RESULTS/"
    avg_folder = "./Mean_CSVs/"
    dfs=[]
    for i in range(SAMPLE_SIZE):
        df = pd.read_csv(os.path.join(results_folder,fname_base) %(STEPS,i))
        dfs.append(df)
    avg = pd.concat(dfs).groupby(level=0).mean()
    avg.to_csv(os.path.join(avg_folder,fname_base)%(STEPS,"AVG%s" %SAMPLE_SIZE))
    return avg


if __name__=="__main__":
    # avg0 = read_and_make_avg("rez_CureAgent-%sSTEPS-%s.csv")
    # avgf = read_and_make_avg("rez_InfiniteFixedCureAgent-%sSTEPS-%s.csv")
    # avgm = read_and_make_avg("rez_MutationBlindNanoAgent-%sSTEPS-%s.csv")
    for NA in [CureAgent,MutationBlindNanoAgent,InfiniteFixedCureAgent]:
        read_and_make_avg("rez_{}-%sSTEPS-%s-NO_MOD.csv".format(NA.__name__))
        read_and_make_avg("rez_{}-%sSTEPS-%s-NO_CC_MUTATION_NO_MOD.csv".format( NA.__name__))
        read_and_make_avg("rez_{}-%sSTEPS-%s-NO_CC_MUTATION.csv".format(NA.__name__))
        
        read_and_make_avg("rez_{}-%sSTEPS_RANDOM_MEMORY__MOD-0.1-%s.csv".format(NA.__name__),steps=100,sample_size=2)

        for mod in [0.2,0.3,0.4]:
            read_and_make_avg("rez_{}-%sSTEPS_RANDOM_MEMORY__MOD-{}-%s.csv".format(NA.__name__,mod),steps=100,sample_size=2)
            read_and_make_avg("rez_{}-%sSTEPS_RANDOM_MEMORY_NO_CC_MUTATION__MOD-{}-%s.csv".format(NA.__name__,mod),steps=100,sample_size=2)
                              
    # read_and_make_avg("rez_CureAgent-RandomMemory5-%sSTEPS-%s.csv")
    # read_and_make_avg("rez_CureAgent-RandomMemory10-%sSTEPS-%s.csv")


    # for i in range(1,10):
    #     read_and_make_avg("rez_CureAgent-Memory{}-%sSTEPS-%s.csv".format(i))
    
