import pandas as pd
from model import *
from collections import namedtuple
import pickle
brojevi_koraka = [50,100,250,500,1000]
sample_sizes = [1,5,50,100]

CC_NUM = 300
NA_NUM = 500
NA_CURIOSITY = 0.5
MAX_STEPS = brojevi_koraka[-1]

ConsistencyTuple = namedtuple("ConsistencyResult","br_koraka sample_size maxA")

def A_measure(dist1,dist2):
    import itertools
    sve_kombinacije = list(itertools.product(dist1,dist2))
    greater_than = sum([s1>s2 for (s1,s2) in sve_kombinacije])
    equal = sum([s1==s2 for (s1,s2) in sve_kombinacije])
    mn = len(dist1)*len(dist2)
    return greater_than/mn + 0.5*(equal/mn)

def compare_first_with_others(distributions):
    A_measures=[]
    first = distributions[0]
    for other in distributions[1:]:
        A = A_measure(first,other)
        A_measures.append(A)
    return A_measures

def get_maxA_for_steps_and_parameter(all_results_for_samplesize,steps,parameter):
    distributions = []
    for results in all_results_for_samplesize:
        distribution = []
        for result in results:
            value = result[:steps].iloc[-1][parameter]
            distribution.append(value)
        distributions.append(distribution)
    
    A_measures = compare_first_with_others(distributions)
    print (A_measures)
    assert(len(A_measures)==19)
    print (max(A_measures))
    return max(A_measures)



def run_model_and_get_results(sample_size,
                              nanoagent_type,steps,agent_memory_type,
                              turn_off_modifiers,CC_mutation_probability,
                              modifier_fraction,is_tumor_growing):
    results = []
    print(steps)
    print(locals())
    print("STATEMACHINE BRANCH")
    print("Sample size is:   %s" %sample_size)

    def make_string(i):
        string_base = "rez_%s-%sSTEPS" %(nanoagent_type.__name__,steps)
        string_base+="_RANDOM_MEMORY" if agent_memory_type==None else "_MEMORY%s" %agent_memory_type
        string_base+="_NO_MOD" if turn_off_modifiers else ""
        string_base+="_NO_CC_MUTATION" if CC_mutation_probability==0 else ""
        string_base+="__MOD-%s" %modifier_fraction
        string_base+="_TUMOR_GROWING" if is_tumor_growing else ""
        string_base+="-%s.csv" %i
        return string_base
        
    for i in range(sample_size):
        print("Running model : %s" %i)
        model = CancerModel(cancer_cells_number=CC_NUM,cure_number = NA_NUM,
                            radoznalost=NA_CURIOSITY,cure_agent_type = nanoagent_type,agent_memory_type=agent_memory_type,turn_off_modifiers=turn_off_modifiers,CC_mutation_probability=CC_mutation_probability,modifier_fraction=modifier_fraction,is_tumor_growing=is_tumor_growing)
        for j in range(steps):
            model.step()
        rez = model.datacollector.get_model_vars_dataframe()
        fname = make_string(i)
        print(fname)
        rez.to_csv(fname)
        results.append(rez)

    return results


def check_conistency(nanoagent_type,PARAMETER = "FitnessFunction"):
    results_list = []
    for ss in sample_sizes:
        all_results_for_samplesize = []
        for i in range(20):
            results = run_model_and_get_results(ss,nanoagent_type,MAX_STEPS)
            all_results_for_samplesize.append(results)
        for steps in brojevi_koraka:
            maxA = get_maxA_for_steps_and_parameter(all_results_for_samplesize,steps,PARAMETER)
            results_list.append(ConsistencyTuple(steps,ss,maxA))
        intermediate_df = pd.DataFrame(results_list,columns = ["num_steps","sample_size","maxA"])
        intermediate_df.to_csv("consistency-SS{}.csv".format(ss))

    df = pd.DataFrame(results_list,columns = ["num_steps","sample_size","maxA"])
    df.to_csv("check_consistency_%s.csv" %nanoagent_type)


if __name__=="__main__":
    nanoagent_type = CureAgent
    check_conistency(nanoagent_type)
    
