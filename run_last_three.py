from rob_ev import *
import pandas as pd
from model import *
from multiprocessing import Process
SAMPLE_SIZE=200
STEPS=5000

for NA in [CureAgent,MutationBlindNanoAgent]:
    print (NA.__name__)
    s1 = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,0.1,True,10,0.01))
    s2 = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,0.1,True,3,0.005))
    s3 = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,0.1,True,3,0.001))
    s1.start()
    s2.start()
    s3.start()
