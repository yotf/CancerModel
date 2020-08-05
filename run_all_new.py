from rob_ev import *
import pandas as pd
from model import *
from parameters import *
import threading


run_model_and_get_results(SAMPLE_SIZE,CureAgent,STEPS,None,False,0.001,0.5,False)


for NA in [CureAgent,MutationBlindNanoAgent,InfiniteFixedCureAgent]:
    print (NA.__name__)
    for modifier_fraction in [0.2,0.3,0.4,0.5]:
        tt = threading.Thread(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,modifier_fraction,False))
        tf = threading.Thread(target=run_model_and_get_results,args=(SAMPLE_SIZE,NA,STEPS,None,False,0.001,modifier_fraction,True))
        tt.start()
        tf.start()


    # for i,r in enumerate(rez):
    #     r.to_csv("rez_%s-%sSTEPS-%s-NO_CC_MUTATION.csv" %(NA.__name__,STEPS,i))