# 1. Introduce tumour heterogeneity by randomly assigning to CC/CSC
# subpopulations ability to reduce the rate of attachment/entrance of NAs
# into them. Also, they should be able to reduce the killing probability
# of NAs.
# Implementation:
# - all tumour cells have additional property 'modifiers' which could be a
# list of 5 numeric values (corresponding to the association,
# disassociation, entrance, killing probability, stop-division
# probability). If numeric value =0 then NP's rate is not modified, if it
# is not=0 then it modifies corresponding NP's rate.
# - in general, CSC should have higher values of modifiers for killing and
# division probabilities (so far it hasn't been observed that CSC are able
# to selectively inhibit entrance of NA into them)

#1. stavljam da se bira jedan od modifier-a, tako sto se izabere random
#ime
# i onda se indeksira to, i izabere se
# posle NA ce traziti odredjeni indeks.


# 2. Differentiate the antitumour effect of NAs into cytostatic (growth
# inhibition) and cytotoxic.
# Implementation:
# - after internalization, we should add one more step where internalized
# NA can either try to block cell division with some probability or kill
# the cell with some probability


# 3. Divide host toxicity of NAs into three categories: nonselective,
# partially selective and strictly selective.
# Implementation:
# - we already have nonselective and strictly selective. However, strict
# selectivity is more an ideal case than reality. Therefore, we should
# replace current binary model (recognize=>try to enter / don't recognize
# => no entrance) with more continuous one:
#         a. At the beginning of the simulation NA’s knowledge of the environment
# is blank so they do not recognize any type of cell-agents (same as now).
#         b. Even if they do not recognize cell, they can try to associate/enter
# but with much lower probability

# 4. Make the role of CSC more prominent by making them more
# drug-resistant and able to detach tumour and leave it (simplified
# metastasis).
# Implementation:
# - maybe add as an additional numeric property "attachment": at each time
# step, this numeric values is compared to a random number and if the
# random number is smaller than 'attachment' value, CSC disappear (leave
# tumour) and is counted somewhere as metastasis score += 1



# 5. reduce the probability of receptor mutations to really small values.
# Even if they mutate NA can enter cells (point 3 above). Remove
# stress-induced mutation (experimental data on that are controversial, so
# for now we should leave it out).


#Ok, ovo sve moze sutra, bez problema. samo ga pusti i gledaj logove


# In summary, during simulation NA agents learn to:
#   - recognize tumour cells
#   - learn to choose between cell killing and division stopping
#   - tune up association/disassociation/internalization
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import numpy as np
from collections import OrderedDict


HEALTHY_CELL_COLOR = "#a4d1a4"
CANCER_CELL_COLOR =   "#d3d3d3"
CANCER_STEM_CELL_COLOR = "#ff1111"
RANDOM_COLORS = ["#ef04f6","#01fca8","#8b901d","#a12dfa","#275665","#2074d5","#305126",
                          "#5704a7","#199d29","#094e34","#0fb97a","#9a38bc","#9c7529","#a68086","#16e8d7",
                          "#30ed79","#25aeb0","#82b183","#f6018b","#a75024"]
CANCER_MUTATION_COLORS = [CANCER_CELL_COLOR,"#ef04f6","#01fca8","#8b901d","#a12dfa","#275665","#2074d5","#305126",
                          "#5704a7","#199d29","#094e34","#0fb97a","#9a38bc","#9c7529","#a68086","#16e8d7",
                          "#30ed79","#25aeb0","#82b183","#f6018b","#a75024"]+ RANDOM_COLORS*100


def nano_agent_decorator(f):  
    def log_f_as_called():
        print(f'{f} was called.')
        f()
    return log_f_as_called

class FixSizeOrderedDict(OrderedDict):
    def __init__(self, *args, max=0, **kwargs):
        self._max = max
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._max > 0:
            if len(self) > self._max:
                self.popitem(False)
                
KILLING_PROBABILITY = 0.2
def percentage(percent, whole):
    return (percent * whole) / 100.0


class Cell(Agent):
    def __init__(self,unique_id,model,value=None):
        super().__init__(unique_id,model)
        p_names = ["Pi","Pd","Pa","Pk","Psd"]
        self.modifiers = dict.fromkeys(p_names,1)

    def xprint(self,*args):
        return
        print( "%s:  " %self.unique_id+" ".join(map(str,args))+"XXX")


        
class HealthyCell(Cell):
    def __init__(self,unique_id,model,value):
        super().__init__(unique_id,model)
        self.color=HEALTHY_CELL_COLOR
        self.points_if_eaten = value
        
    def stress(self):
        pass
def get_rgb_from_hex(hex_rgb):
    r = hex_rgb[1:3]
    g= hex_rgb[3:5]
    b = hex_rgb[5:]
    return r,g,b

def add_to_color(hex_color,amount):
    minn = 0
    maxn =255
    new_value = int(hex_color,16)+amount
    new_value = minn if new_value < minn else maxn if new_value > maxn else new_value
    return hex(new_value).lstrip("0x")
    

        
class CancerCell(Cell):
    def __init__(self,unique_id,model,value,has_modifiers,mutation_probability,grows):
        super().__init__(unique_id,model)
        self.mutation_count = 0
        self.mutation_probability=mutation_probability
        self.color = CANCER_CELL_COLOR
        self.points_if_eaten = value
        p_names = ["Pi","Pd","Pa","Pk","Psd"]
        self.modifiers = dict.fromkeys(p_names,1)
        self.has_modifiers=has_modifiers
        self.grows=grows

        if has_modifiers:
            pn = self.random.choice(p_names)
            self.modifiers[pn]=self.random.uniform(0.3,0.8) 
        self.xprint("Initialized modifiers : %s" %self.modifiers)
        self.stop_division =False

    def xprint(self,*args):
        return
        print( "%s:  " %self.unique_id+" ".join(map(str,args)))

    def step(self):
        mutate = self.random.choices([True,False],[self.mutation_probability,1-self.mutation_probability])[0]
        self.xprint("It is %s that I mutated" %(mutate))
        self.mutation_count +=0 if not mutate else 1
        self.xprint("I have mutated %s times" %self.mutation_count)
        self.color = CANCER_MUTATION_COLORS[self.mutation_count]
        if self.grows:
            will_grow = self.random.choices([True,False],[0.01,1-0.01])[0]
            if will_grow: 
                self.grow()
        

    def grow(self):
        if self.stop_division:
            return
        n = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        for pos in n:
            if self.model.grid.is_cell_empty(pos):
                c = self.__class__("CANCER_CELL-"+str(uuid.uuid4()),value=self.points_if_eaten,model=self.model,has_modifiers=False,mutation_probability=self.mutation_probability,grows=self.grows)
                c.modifiers =self.modifiers
                self.xprint("Duplicated myself, new cell has modifiers: %s" %c.modifiers)
                self.xprint("I have modifiers: %s" %c.modifiers)
                assert(c.modifiers==self.modifiers)
                self.model.grid.place_agent(c,pos)
                self.model.schedule.add(c)

    # def mutate_color(self,color_hex,by=5):
    #     r,g,b = get_rgb_from_hex(color_hex)
    #     r,g,b = [add_to_color(c,-20) for c in [r,g,b]]
    #     return "#{}{}{}".format(r,g,b)



class CancerStemCell(CancerCell):
    def __init__(self,unique_id,model,value,has_modifiers,mutation_probability,grows):
        super().__init__(unique_id,model,value,has_modifiers,mutation_probability,grows)
        self.color = CANCER_STEM_CELL_COLOR
        self.points_if_eaten = value
        self.modifiers['Pi'] = self.random.uniform(0.5,0.8)
        self.modifiers["Psd"] = self.random.uniform(0.5,0.8)


    def step(self):
        super().step()
        detach = self.random.choices(population=[True,False],weights=[0.10,0.90])[0]
        if detach:
            self.model.detach_stem_cell(self)


class CureAgent(Agent):
    MOVING_STATE = "moving"
    STANDING_ON = "standing_on"
    ASSOCIATED_2 = "associated2"
    ASSOCIATED_1 = "associated1"
    INTERNALIZED_STATE = "internalized"
    probabilities_range = np.arange(0,1,0.1)
    memory_range = [0,1,2,3] #TODO proveriti uvek da li je dobar range !!! 
    STOP_DIVISION_AGENT = "STOP_DIVISION_AGENT"
    KILLING_AGENT = "KILLING AGENT"

    def xprint(self,*args):
        return
        print( "%s:  " %self.unique_id+" ".join(map(str,args)))
    
    def __init__(self,unique_id,model,speeds,radoznalost,memory_type): 
        super(CureAgent,self).__init__(unique_id,model)
        self.speeds = speeds
        self.MEMORY_TYPE = memory_type
        #on bira ovde koji je tip, i onda ce se to posle gledati
        # if type=STOP_DIVISION: self.in
        self.step_functions = {self.MOVING_STATE:self.step_move,
                      self.STANDING_ON:self.step_standing,
                      self.ASSOCIATED_1:self.step_associated1,
                      self.ASSOCIATED_2:self.step_associated2,
                        self.INTERNALIZED_STATE:self.step_internalized
        }
        self.points = 0
        self.original_color = "#ffd700"
        self.size =0.2
#        self.energy = np.inf
        self.radoznalost = radoznalost
        self.state = self.MOVING_STATE
        self.initialize_variables()




    def initialize_variables(self):
        #Kod mutacije ce ovo pokrenuti, tako da bi trebalo sve da bude u okviru onog sto mogu da urade 
        
        self.Pi,self.Pd,self.Pa  = [self.random.choice(self.probabilities_range) for i in range(3)]
        self.Pk,self.Psd = 0.50,0.5 #TODO za sada je fiksirano
        self.speed = self.random.choice(self.speeds)
        self.memory_size = self.random.choice(self.memory_range) if self.MEMORY_TYPE is None else self.MEMORY_TYPE
        self.memorija = FixSizeOrderedDict(max=self.memory_size)
        self.type = self.random.choice([self.STOP_DIVISION_AGENT,self.KILLING_AGENT])
     #   self.set_final_function_for_type()
        r,g,b = get_rgb_from_hex(self.original_color)
        self.color = "#{}{}{}".format(r,add_to_color(g,-(self.speed*5)),b)
        self.represent_self()


    def represent_self(self):
        self.xprint("My characteristcs are:")
        self.xprint("Speed: %s   Memory Size : %s   (Pa,Pd,Pi): (%s,%s,%s)" %(self.speed,self.memory_size,self.Pa,self.Pd,self.Pi))

    def check_for_cells(self):
        cells = [f for f in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(f,Cell)]
        assert (len(cells)<=1)
        return cells


    
    def move(self):
        """The agents will move in a random direction and lose specified energy"""
        for i in range(self.speed):
            possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self,new_position)

    def step(self):
        self.step_functions[self.state]()
        # self.energy-=1 
        # if self.energy==0:
        #     self.kill_self()

    def step_move(self):
        self.xprint("In moving state, about to move")
        self.xprint(self.state)
        self.move()
        cells = self.check_for_cells()
        if cells:
            self.current_cell_id=cells[0].unique_id
            self.xprint("Found cell %s going to standing on" %self.current_cell_id)
            self.state = self.STANDING_ON
            self.xprint(self.state)

    def step_standing(self):
        self.xprint("In standing state")
        self.xprint(self.state)
        cells = self.check_for_cells() 
        if cells and cells[0].unique_id==self.current_cell_id:
            self.xprint("Cell still here, will try to associate")
            cell = cells[0]
            associated = self.try_to_associate(cell)
            self.state = self.ASSOCIATED_1 if associated else self.MOVING_STATE
        else: #if it was eaten in meantime
            self.xprint("Cells been eaten in meantime, moving on")
            self.state = self.MOVING_STATE
            
    def step_associated1(self):
        #TODO ovde moze jedan decorator da bude
        cells = self.check_for_cells()
        self.xprint("In A1 state")
        self.xprint("Will disassociate with %s probability"% self.Pd)
        if cells and cells[0].unique_id==self.current_cell_id:
            cell = cells[0]
            disassociated = self.try_to_disassociate(cell)
            self.state = self.MOVING_STATE if disassociated else self.ASSOCIATED_2
            self.xprint("I am entering %s state" %self.state)
        else:
            self.xprint("The cell was killed, moving on")
            self.state = self.MOVING_STATE

    def try_to_disassociate(self,cell):
        stay_attached_probability_modified = (1-self.Pd)*cell.modifiers["Pd"] 
        self.xprint("Cell has Pd modifier: %s" %cell.modifiers["Pd"])
        modified_Pd = (1-stay_attached_probability_modified)
        self.xprint("Modified Pd: %s" %modified_Pd)
        disassociated  = self.random.choices(population=[True,False],weights=[modified_Pd,stay_attached_probability_modified])[0]
        self.xprint("It is %s that I disassociated " %disassociated)
        return disassociated
        

    def step_associated2(self):
        self.xprint("In A2 state")
        self.xprint(self.state)
        cells = self.check_for_cells()
        if cells and cells[0].unique_id==self.current_cell_id:
            cell = cells[0]
            internalized = self.try_to_internalize(cell)
            self.state = self.INTERNALIZED_STATE if internalized else self.ASSOCIATED_1
        else:
            self.xprint("The cell was killed, moving on")
            self.state = self.MOVING_STATE


    def step_internalized(self):
        self.xprint("I have internalized")
        self.xprint("I am agent of type %s" %self.type)
        cells = self.check_for_cells()
        if cells and cells[0].unique_id==self.current_cell_id:
            cell = cells[0]
            if self.type==self.KILLING_AGENT:
                executed = self.try_to_kill(cell)
            elif self.type==self.STOP_DIVISION_AGENT:
                executed= self.try_to_stop_division(cell)
            else:
                assert(False)
            
            self.state = self.MOVING_STATE if executed else self.INTERNALIZED_STATE
        else:
            self.xprint("The cell was killed in meantime, moving on")
            self.state = self.MOVING_STATE
        

    def try_to_kill(self,cell):
        self.xprint("Trying to kill")
        killed = self.random.choices(population=[True,False],weights=[self.Pk,1-self.Pk])[0]
        if killed:
            self.model.kill_cell(cell)
            self.points+=cell.points_if_eaten
        self.xprint("It us %s that I killed" %killed)
        return killed

    def try_to_stop_division(self,cell):
        self.xprint("Trying to stop division with probability %s" % self.Psd)
        stopped = self.random.choices(population=[True,False],weights=[self.Psd,1-self.Psd])[0]
        cell.stop_division=stopped
        self.points+=cell.points_if_eaten if stopped else 0 
        self.xprint("It us %s that I stopped division" %stopped)
        return stopped 
        
        

    def try_to_associate(self,cell):
        """Tries to associate and refreshes memory with cell"""

        mem = self.memorija.get(cell.color,False)
        self.memorize(cell)
        modified_Pa = self.Pa*cell.modifiers["Pa"]
        if not mem:
            Pa = self.radoznalost*modified_Pa 
            self.xprint("Cell not recognized,probability Pa is %s"%Pa)
        elif mem>0:
            Pa = modified_Pa
            self.xprint ("Found in memory")
        elif mem<0:
            self.xprint("Healthy cell recognized!")
            Pa= 0
        self.xprint("Trying to associate with probability %s from %s state" %(Pa,self.state))
        associated = self.random.choices(population = [True,False],weights=[Pa,1-Pa])[0]
        self.xprint("It is %s that I will associate" %associated)
        return associated

    def memorize(self,cell):
        if self.memory_size==0: #jbg TODO 
            return
        self.xprint("Memorizing cell")
        self.xprint("memory before")
        self.xprint(self.memorija)
        self.xprint("memory after")
        self.memorija[cell.color] = cell.points_if_eaten
        self.xprint(self.memorija)
        self.size = 0.2 + 0.2*len(self.memorija) #jedino ce rasti, nikad se ne smanjuje
        
    def try_to_internalize(self,cell):
        self.xprint("Trying to internalize with %s probability"%self.Pi)
        modified_Pi = self.Pi*cell.modifiers["Pi"]
        self.xprint("The cell has Pi_modifier: %s " %(cell.modifiers["Pi"]))
        self.xprint("Modified probability: %s" %(modified_Pi))
        internalized = self.random.choices(population = [True,False],weights = [modified_Pi, 1- modified_Pi])[0]
        self.xprint("It is %s that i internalized" %internalized)

        # else:
        #     cell.stress()
        return internalized


    ## Todo wrap some repetitive code 
   #  def trace_in(func, *args, **kwargs):
   # 2    print "Entering function",  func.__name__
   # 3 
   # 4 def trace_out(func, *args, **kwargs):
   # 5    print "Leaving function", func.__name__
   # 6 
   # 7 @wrap(trace_in, trace_out)
   # 8 def calc(x, y):
   # 9    return x + y

    def mutate(self):
        self.xprint("I am mutating")
        stara_memorija = self.memorija
        self.xprint("Old memory:")
        self.xprint(stara_memorija)
        self.initialize_variables()
        for key,value in stara_memorija.items():
            self.memorija[key] = value
        self.xprint("New memory (size: %s) : " %self.memory_size)
        self.xprint(self.memorija)


    def kill_self(self):
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)

    def copy(self):
        n=type(self)(uuid.uuid4(),self.model,speeds = self.speeds,radoznalost=self.radoznalost,memory_type=self.MEMORY_TYPE)
        n.speed = self.speed
        n.Pa = self.Pa
        n.Pi = self.Pi
        n.Pd = self.Pd
        n.Pk = self.Pk
        n.Psd = self.Psd
        n.memorija = self.memorija.copy()
        n.memory_size = self.memory_size
        n.color = self.color
        n.type = self.type
        return n


class InfiniteFixedCureAgent(CureAgent):
    def __init__(self,unique_id,model,speeds,radoznalost,memory_type):
        super(InfiniteFixedCureAgent,self).__init__(unique_id,model,speeds,radoznalost,memory_type)
        #TODO (0.8,0.4) (0.9,0.3) 0.5 (za Pd ostaje) (ovo je sve za tumor koji ne raste ) 
        # self.probabilities_CC = [0.8,0.5,0.5]
        # self.probabilities_HC = [0.5,0.5,0.5]

        # self.probabilities_CC = [0.6,0.5,0.6]
        # self.probabilities_HC = [0.5,0.5,0.5]

        self.probabilities_CC = [0.7,0.5,0.7,0.7,0.7]
        self.probabilities_HC = [0.5,0.5,0.5,0.5,0.5]

        # self.probabilities_CC = [0.8,0.5,0.8]
        # self.probabilities_HC = [0.5,0.5,0.5]

#        self.probabilities_CC = [0.9,0.5,0.9,0.9,0.9]
        
        self.memory_size = 0
        self.Pi,self.Pa,self.Pd,self.Pk,self.Psd = self.probabilities_HC

    def try_to_associate(self,cell):
        points = cell.points_if_eaten
        self.xprint(" This cell is a %s " %("Cancer Cell" if points>0 else "Healthy Cell"))
        self.Pa,self.Pd,self.Pi,self.Pk,self.Psd = self.probabilities_CC if points>0 else self.probabilities_HC
        self.xprint("Trying to associate with probability %s from %s state" %(self.Pa,self.state))
        modified_Pa = self.Pa*cell.modifiers["Pa"]
        associated = self.random.choices(population = [True,False],weights=[modified_Pa,1-modified_Pa])[0]
        self.xprint("It is %s that I will associate" %associated)
        return associated

    def mutate(self):
        self.speed = self.random.choice(self.speeds)
        self.type = self.random.choice([self.STOP_DIVISION_AGENT,self.KILLING_AGENT])
        self.represent_self()
        
        

    def copy(self):
        self.xprint("COPYING MYSELF")
        n=type(self)(uuid.uuid4(),self.model,speeds = self.speeds,radoznalost=self.radoznalost,memory_type=self.MEMORY_TYPE)
        n.speed = self.speed
        n.color = self.color
        n.type = self.type
        return n

class MutationBlindNanoAgent(CureAgent):
    def __init__(self,unique_id,model,speeds,radoznalost,memory_type):
        super(MutationBlindNanoAgent,self).__init__(unique_id,model,speeds,radoznalost,memory_type)
        self.ORIGINAL_RADOZNALOST = radoznalost
        self.radoznalost = 0 

    def memorize(self,cell):
        self.xprint("Memorizing %s with color %s" %(cell.__class__,cell.color))
        known_colors = ["#a4d1a4",
         "#d3d3d3",
        "#ff1111"]
        if cell.color in known_colors:
            self.xprint("Can memorize cell")
            super().memorize(cell)
            self.radoznalost = self.ORIGINAL_RADOZNALOST 
        else:
            self.radoznalost = 0 # ne svidja mi se logika ovoga, al ajde TODO 
            self.xprint("Cant memorize cell")


import math
import uuid
class CancerModel(Model):

    def xprint(self,*args):
        return
        print( "CANCER MODEL:  " +" ".join(map(str,args)))
    def __init__(self,cancer_cells_number,cure_number,radoznalost,cure_agent_type,agent_memory_type,turn_off_modifiers,CC_mutation_probability,modifier_fraction,is_tumor_growing):
        self.xprint("STARTING SIMULATION !!!")
        self.counter = 0
        self.metastasis_score=0
        eat_values =  {CancerCell:1,HealthyCell:-1,CancerStemCell:5}
        assert(issubclass(cure_agent_type,CureAgent))
        self.cure_number = cure_number
        self.modifier_fraction = modifier_fraction

        self.datacollector = DataCollector(
        model_reporters = {"FitnessFunction":fitness_funkcija,
                           "AverageSpeed":speed_avg,"AverageMemoryCapacity":memory_size_all_avg,
                           "PopulationHeterogenity":population_heterogenity,
                           "MutationAmount":mutation_amount,
                           "CancerStemCell Number":CSC_number,
                           "CSC Specialized Agents":CSC_specialized_agents,
                           "CancerHeterogenity1": cancer_heterogenity_1,
                           "CancerHeterogenity2":cancer_heterogenity_2,
                           "CC_Number": CC_number,
                           "HealthyCell_Number":HC_number,
                           "MetastasisScore" : "metastasis_score",
                           "CancerSize": cancer_size,
                           "TotalTumorResiliance":overall_cancer_resiliance,
                           "TumorResiliance_Pi":cancer_resiliance_Pi,
                           "TumorResiliance_Pd":cancer_resiliance_Pd,
                           "TumorResiliance_Pa":cancer_resiliance_Pa,
                           "TumorResiliance_Pk":cancer_resiliance_Pk,
                           "TumorResiliance_Psd":cancer_resiliance_Psd,
                           "NumberOfMutatedCells":mutated_CCs_num,
                           "TumorCoverage":tumor_coverage,
                           "AveragePd":average_Pd,
                           "AveragePa":average_Pa,
                           "AveragePi":average_Pi,
                           "AveragePk":average_Pk,
                           "AveragePsd":average_Psd

                            },
        agent_reporters={"Pi":get_Pi,"Pa":get_Pa,"Pd":get_Pd,"speed":get_speed,"Psd":get_Psd,"Pk":get_Pk,"memory_size":get_memory_size,"type":get_agent_type})
        grid_size = math.ceil(math.sqrt(cancer_cells_number*4))
        self.cancer_cells_number=cancer_cells_number
        self.grid = MultiGrid(grid_size,grid_size,False)
        self.speeds = list(range(1,grid_size//2))
        poss = self.generate_cancer_cell_positions(grid_size,cancer_cells_number)
        num_CSC = math.ceil(percentage(1,cancer_cells_number))
        pos_CSC = [self.random.choice(poss) for i in range(num_CSC)]
        self.schedule = RandomActivation(self)
        self.running = True
        for i in range(cancer_cells_number):
            pos = poss[i]
            has_modifiers = False if ((i < ((1-self.modifier_fraction)*cancer_cells_number)) or turn_off_modifiers is True) else True #10 % will be with modifiers
            c = CancerStemCell("CANCER_STEM_CELL-"+str(uuid.uuid4()),self,value = eat_values[CancerStemCell],has_modifiers=has_modifiers,mutation_probability=CC_mutation_probability,grows=is_tumor_growing) \
                if pos in pos_CSC else CancerCell("CANCER_CELL-"+str(uuid.uuid4()),self,value=eat_values[CancerCell],has_modifiers=has_modifiers,mutation_probability=CC_mutation_probability,grows=is_tumor_growing)
            self.grid.place_agent(c,pos)
            self.schedule.add(c)

        from itertools import cycle
        positions = cycle([(self.random.choice(range(grid_size)),self.random.choice(range(grid_size))) for i in range(5)])
        for i in range(cure_number):
            pos = next(positions)
            self.xprint(pos)
            a = cure_agent_type(uuid.uuid4(),self,speeds = self.speeds,radoznalost=radoznalost,memory_type=agent_memory_type) 
            self.grid.place_agent(a,pos)
            self.schedule.add(a)

        for (i,(contents, x,y)) in enumerate(self.grid.coord_iter()):
            if not contents:
                c = HealthyCell(uuid.uuid4(),self,eat_values[HealthyCell])
                self.grid.place_agent(c,(x,y))
                self.schedule.add(c)

    def generate_cancer_cell_positions(self,grid_size,cancer_cells_number):
        center = grid_size//2
        poss = [(center,center)]
        for pos in poss:
            poss+=[n for n in self.grid.get_neighborhood(pos,moore=True,include_center=False) if n not in poss]
            if len(set(poss))>=cancer_cells_number:
                break
        poss = list(set(poss))
        return poss


    def duplicate_mutate_or_kill(self):
        koliko = math.ceil(percentage(5,self.cure_number)) 
        cureagents = [c for c in self.schedule.agents if isinstance(c,CureAgent)]
        sortirani = sorted(cureagents, key=lambda x: x.points, reverse=True)
        poslednji = sortirani[-koliko:]
        prvi = sortirani[:koliko]
        sredina = len(sortirani)//2
        pocetak_sredine = sredina-(koliko//2)
        kraj_sredine = sredina+(koliko//2) 
        srednji = sortirani[pocetak_sredine:kraj_sredine]
        self.mutate_agents(srednji)
        assert(len(prvi)==len(poslednji))
        self.remove_agents(poslednji)
        self.duplicate_agents(prvi)

    def mutate_agents(self,agents):
        self.xprint("Mutating middle agents")
        for a in agents:
            a.mutate()
    def remove_agents(self,agents):
        for a in agents:
            self.kill_cell(a)
    def duplicate_agents(self,agents):
        for a in agents:
            a_new = a.copy()
            self.grid.place_agent(a_new,(1,1))
            self.schedule.add(a_new)
        
    def kill_cell(self,cell):
        self.grid.remove_agent(cell)
        self.schedule.remove(cell)

    def detach_stem_cell(self,cell):
        self.metastasis_score +=1
        self.kill_cell(cell)

    def step(self):
        self.datacollector.collect(self)
        self.counter+=1
        self.schedule.step()
        if self.counter%10 ==0: # TODO ovo menjamo, parameter TODO
            self.duplicate_mutate_or_kill()
        # if self.counter%100 ==0: #TODO ovo da se zadaje
        #     _ = [c.grow() for c in self.schedule.agents if isinstance(c,CancerCell)]


# Za svaku NA konfiguraciju (6 komada) treba tokom simulacije ispratiti:

def get_CCs(model):
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell)]
    return CCs

def get_modifier_sum(model,modifier_name):
    CCs = get_CCs(model)
    modifiers = [(1-c.modifiers[modifier_name]) for c in CCs]
    modifier_sum =sum(modifiers)
    return modifier_sum

def overall_cancer_resiliance(model):
    s = 0
    for p in ["Pi","Pd","Pa","Pk","Psd"]:
        s+=get_modifier_sum(model,p)
    return s 
    
    
    
def cancer_resiliance_Pi(model):
    return get_modifier_sum(model,"Pi")

def cancer_resiliance_Pd(model):
    return get_modifier_sum(model,"Pd")

def cancer_resiliance_Pa(model):
    return get_modifier_sum(model,"Pa")

def cancer_resiliance_Pk(model):
    return get_modifier_sum(model,"Pk")

def cancer_resiliance_Psd(model):
    return get_modifier_sum(model,"Psd")

def fitness_funkcija(model):
    r = 5
    CSCs = [c for c in model.schedule.agents if isinstance(c,CancerStemCell)]
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell)]
    HCs = [c for c in model.schedule.agents if isinstance(c,HealthyCell)]
    try:
        FF = len(HCs)/((r*len(CSCs)+ len(CCs) ))
    except ZeroDivisionError:
        FF = len(HCs)
    return FF

def tumor_diversity_num(model):
    tumor_colors = [c.color for c in model.schedule.agents if isinstance(c,CancerCell) ]
    different_tumors = set(tumor_colors)
    return len(different_tumors)
    
    


def tumor_coverage(model):
    """Kod InfiniteFixed ce biti jedan, posto je uvek covered""" #TODO 04
    #Heterogeni tumor koji evoluira(mutira) i jedan koji ne evoluira sa razlicitim procentima
    #rezistentnosti. 20,30,40,50 # cetiri scenarija *2 (i ovaj koji ne evoluira)
    # nek bude onih koji postoje TODO 0407
    #i onda jedan za sve tri kategorije agenata koji raste hetergon i mutira. 
    
    tumor_colors = [c.color for c in model.schedule.agents if isinstance(c,CancerCell)]
    rc = [c for c in all_recognized_colors(model) if c in tumor_colors]
    try:
        return len(rc)/tumor_diversity_num(model)
    except ZeroDivisionError:
        return 1 

def speed_avg(model):
    cures = [c for c in model.schedule.agents if isinstance(c,CureAgent)]
    speeds = 0
    for c in cures:
        speeds+= c.speed
    return speeds/len(cures)

#TODO dzinovski csv iz mean_csv foldera - svi zajedno da budu, napravi taj
#jedan dzinovski i onda da budu razliciti fajlovi za tumor scenarije a ovi ostali tu


def memory_size_all_avg(model):
    #TODO proveri da li je sve ovo legitimno za memory size. zasto tako malo raste
    #vidi koji su izabrani u logu
    cures = [c for c in model.schedule.agents if isinstance(c,CureAgent)]
    memory_sizes = [m.memory_size for m in model.schedule.agents if isinstance(m,CureAgent)]
    return sum(memory_sizes)/len(cures)


def cancer_heterogenity_1(model):
    """Ratio between CC with modifiers and all CCs"""
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell)]
    num_of_modifier_CCs = len([c for c in CCs if c.has_modifiers])
    try:
        return num_of_modifier_CCs/len(CCs)
    except ZeroDivisionError:
        return 0


def mutated_CCs_num(model):
    mutated_CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell) and c.mutation_count>0 ]
    return len (mutated_CCs)


def cancer_heterogenity_2(model):
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell) ]
    # print("Number of CCs,Number of mutated CCs")
    # print(len(CCs),len(mc))
    try:
        return mutated_CCs_num(model)/len(CCs)
    except ZeroDivisionError:
        return 0 

def all_recognized_colors(model):
    sve_memorije = [list(a.memorija.keys()) for a in model.schedule.agents if isinstance(a,CureAgent)]
    all_colors_in_memories = sum(sve_memorije,[])
    unique_colors = set(all_colors_in_memories)
    return unique_colors
    

def population_heterogenity(model):
    """ Returns the overall number of new colors in memory """
    cureagents = [a for a in model.schedule.agents if isinstance(a,CureAgent)]
    sve_memorije = [list(a.memorija.keys()) for a in model.schedule.agents if isinstance(a,CureAgent)]
    all_colors_in_memories = sum(sve_memorije,[])
    unique_colors = set(all_colors_in_memories)
    return len(unique_colors)/len(cureagents)
    # het = 0
    # NAs = [a for a in model.schedule.agents if isinstance(a,CureAgent)]
    # for a in NAs:
    #     if a.memorija:
    #         for color in a.memorija.keys():
    #             if color not in [HEALTHY_CELL_COLOR,CANCER_CELL_COLOR,CANCER_STEM_CELL_COLOR]:
    #                 het+=1
    # return het

def CSC_specialized_agents(model):
    NAs = [a for a in model.schedule.agents if isinstance(a,CureAgent)]
    num_of_CSC_in_memory = [True for a in NAs if CANCER_STEM_CELL_COLOR in a.memorija.keys()]
    # print("num of csc in memories")
    # print(num_of_CSC_in_memory)
    # print(len(num_of_CSC_in_memory))
    return len(num_of_CSC_in_memory)

def HC_number(model):
    hcs = [h for h in model.schedule.agents if isinstance(h,HealthyCell)]
    return len(hcs)
    
def CSC_number(model):
    n = len([True for c in model.schedule.agents if isinstance(c,CancerStemCell)])
    # print("CSC number")
    # print(n)
    return n
            
def mutation_amount(model):
    """Returns the total of mutations of CCs"""
    mutation_counts = [c.mutation_count for c in model.schedule.agents if isinstance(c,CancerCell)]
#    print("mutation counts")
#    print(mutation_counts)
    return sum(mutation_counts)


def get_Pi(agent):
    try:
        return agent.Pi
    except AttributeError:
        return None

def get_Pa(agent):
    try:
        return agent.Pa
    except AttributeError:
        return None
    
def get_Pd(agent):
    try:
        return agent.Pd
    except AttributeError:
        return None

def average_Pd(model):
    agents = [a for a in model.schedule.agents if isinstance(a,CureAgent)]
    Pds = [a.Pd for a in model.schedule.agents if isinstance(a,CureAgent)]
    return sum(Pds)/len(Pds)

def average_Pa(model):
    Pds = [a.Pa for a in model.schedule.agents if isinstance(a,CureAgent)]
    return sum(Pds)/len(Pds)

def average_Pi(model):
    Pds = [a.Pi for a in model.schedule.agents if isinstance(a,CureAgent)]
    return sum(Pds)/len(Pds)

def average_Pk(model):
    Pds = [a.Pk for a in model.schedule.agents if isinstance(a,CureAgent)]
    return sum(Pds)/len(Pds)

def average_Psd(model):
    Pds = [a.Psd for a in model.schedule.agents if isinstance(a,CureAgent)]
    return sum(Pds)/len(Pds)



def get_speed(agent):
    try:
        return agent.speed
    except AttributeError:
        return None


def get_Psd(agent):
    try:
        return agent.Psd
    except AttributeError:
        return None

def get_Pk(agent):
    try:
        return agent.Pk
    except AttributeError:
        return None

def get_memory_size(agent):
    try:
        return agent.memory_size
    except AttributeError:
        return None

def get_agent_type(agent):
    try:
        
        return 1 if agent.type==agent.STOP_DIVISION_AGENT else 0
    except AttributeError:
        return None

def CC_number(model):
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell) if not isinstance(c,CancerStemCell)]
    return len(CCs)

def cancer_size(model):
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell)]
    return len(CCs)









