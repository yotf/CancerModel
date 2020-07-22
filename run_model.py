from rob_ev import *
import pandas as pd
from model import *
STEPS = 1000
SAMPLE_SIZE = 200

for i in range(10):
    rez = run_model_and_get_results(SAMPLE_SIZE,CureAgent,STEPS,agent_memory_type=i)
    for s,r in enumerate(rez):
        r.to_csv("rez_%s-Memory%s-%sSTEPS-%s.csv" %(CureAgent.__name__,i,STEPS,s))
    

# for NA in [CureAgent,MutationBlindNanoAgent,InfiniteFixedCureAgent]:
#     print (NA.__name__)
#     rez = run_model_and_get_results(SAMPLE_SIZE,NA,STEPS,agent_memory_type=None)
#     for i,r in enumerate(rez):
#         r.to_csv("rez_%s-%sSTEPS-%s.csv" %(NA.__name__,STEPS,i))

