from rob_ev import *
import pandas as pd
from parameters import *
print (NA.__name__)
rez = run_model_and_get_results(SAMPLE_SIZE,NA,STEPS)
for i,r in enumerate(rez):
    r.to_csv("rez_%s-%sSTEPS-%s.csv" %(NA.__name__,STEPS,i))
print(rez)
