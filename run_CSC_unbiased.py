from rob_ev import *
import pandas as pd
from model import *
from multiprocessing import Process
SAMPLE_SIZE=200
STEPS=1000

for NA in [CureAgent,MutationBlindNanoAgent,InfiniteFixedCureAgent]:
    print (NA.__name__)
    s1 = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,
                                                        NA,STEPS,
                                                        None,False,
                                                        0.001,0.1,False,3,0))
    s1.start()
