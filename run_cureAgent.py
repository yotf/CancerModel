from rob_ev import *
import pandas as pd
from parameters import *


rez = run_model_and_get_results(SAMPLE_SIZE,CureAgent,STEPS,agent_memory_type=None)

for i,r in enumerate(rez):
    r.to_csv("rez_CureAgent-RandomMemory5-%sSTEPS-%s.csv" %(STEPS,i))
