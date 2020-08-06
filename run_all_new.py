from rob_ev import *
import pandas as pd
from model import *
from parameters import *
from multiprocessing import Process


for NA in [CureAgent,MutationBlindNanoAgent,InfiniteFixedCureAgent]:
    print (NA.__name__)
    t = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,0.1,True))
    t.start()
    for modifier_fraction in [0.2,0.3,0.4,0.5]:
        tt = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0,modifier_fraction,False))
        tf = Process(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,modifier_fraction,False))
        tt.start()
        tf.start()


    # for i,r in enumerate(rez):
    #     r.to_csv("rez_%s-%sSTEPS-%s-NO_CC_MUTATION.csv" %(NA.__name__,STEPS,i))
