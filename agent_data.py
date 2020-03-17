# super, divno. Koliko vidim rezultati se uklapaju u ocekivanja.  Prema
# consistency analysis cini se da cemo morati da idemo na sample size 50.
# Moracemo na slikama da doradimo legendu i ose, ali to je otprilike to.
# Da li mozes da uradis sledece: tokom 0b evolucije da se u svakom
# vremenskom koraku izvuku p_a, p_d, p_i, speed vrednosti za svakog
# pojedinacno agenta.
# Onda se izbroji koliko NA agenata ima koji speed i dobijamo anatomiju
# evolucije brzina
# Isto to i za p_a, p_d, p_i
# Idealno bi bilo ako bi na kraju dobili jasno grupisanje, npr

# 58 NA agenata ima p_a/p_d/p_i/speed vrednosti x/y/z/q
# 28 NA agenata ima p_a/p_d/p_i/speed vrednosti a/b/c/d
# ...

# Ako to moze, onda bi mogli da uzmemo sample nakon npr 200 i 1000
# evolutivnih koraka, izdvojimo homogene grupe unutar te dve populacije i
# posaljemo englezima da njih injektuju u STEPS simulator (koji detaljno
# gleda nivo od nekoliko celija) i vide sta ce se desiti.
# Cuo sam se sa njima i za to bi im, od kada dobiju podatke trebalo
# dan-dva.

# Ja cu sada spram ovih slika nastaviti da pisem pa kada budem imao
# koherentan tekst i javljam ti da proveris.


from model import *
CC_NUM = 300
NA_NUM = 500
CANCER_MUTATION_PROBABILITY = 0.1
NA_CURIOSITY = 1
def run_model_and_get_agent_data(nanoagent_type,steps):
    print(steps)
    model = CancerModel(cancer_cells_number=CC_NUM,cure_number = NA_NUM,
                            verovatnoca_mutacije=CANCER_MUTATION_PROBABILITY,
                            radoznalost=NA_CURIOSITY,cure_agent_type = nanoagent_type)
    for i in range(steps):
            model.step()
    rez = model.datacollector.get_agent_vars_dataframe()
    print(rez)
    assert(False)
    results.append(rez)
    return results


if __name__ =="__main__":
    run_model_and_get_agent_data(CureAgent,200)
