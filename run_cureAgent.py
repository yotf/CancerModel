from rob_ev import *
import pandas as pd
from parameters import *


rez = run_model_and_get_results(SAMPLE_SIZE,CureAgent,STEPS)

for i,r in enumerate(rez):
    r.to_csv("rez_CureAgent-RandomMemory10-%sSTEPS-%s.csv" %(STEPS,i))
