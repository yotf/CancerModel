
import os
import pandas as pd
from parameters import *
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

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


for value in ["FitnessFunction","CancerCellNumber"]:
    plot_inf(value)
    plt.legend()
    plt.show()

