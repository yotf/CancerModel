from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from numpy.random import choice
import numpy as np
from collections import OrderedDict

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
        self.size=1

    def grow(self):
        n = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        for pos in n:
            if self.model.grid.is_cell_empty(pos):
                c = self.__class__(uuid.uuid4(),value=self.points_if_eaten,model=self.model)
                self.model.grid.place_agent(c,pos)
                self.model.schedule.add(c)
        
class HealthyCell(Cell):
    def __init__(self,unique_id,model,value):
        super().__init__(unique_id,model)
        self.color="#a4d1a4"
        self.points_if_eaten = value 
        
    def stress(self):
        pass # da li i ona treba da mutira??

def get_rgb_from_hex(hex_rgb):
    r = hex_rgb[1:3]
    g= hex_rgb[3:5]
    b = hex_rgb[5:]
    return r,g,b

def add_to_color(hex_color,amount):
    minn = 0
    maxn =255
    print(hex_color)
    new_value = int(hex_color,16)+amount
    new_value = minn if new_value < minn else maxn if new_value > maxn else new_value
    return hex(new_value).lstrip("0x")
    
#TODO nasledjuju iksustvo deepcopy
#TODO robustness pustamo nepametne samo, i dobijamo rezultate. Koji je ucinak, fitness funkcija

        
class CancerCell(Cell):
    def __init__(self,unique_id,model,value):
        super().__init__(unique_id,model)
        self.color = "#d3d3d3"
        self.points_if_eaten = value
    def stress(self):
        mutate = choice([True,False],1,p=[0.1,0.9])[0]
        self.color = self.color if not mutate else self.mutate_color(self.color)
        print(self.color)


                
    

    def mutate_color(self,color_hex,by=5):
        r,g,b = get_rgb_from_hex(color_hex)
        print (r,g,b)
        r,g,b = [add_to_color(c,-20) for c in [r,g,b]]
        return "#{}{}{}".format(r,g,b)


       # TODO mutiramo 5% srednjih, ili speed ili radoznalost za jedan stepen mislim da sve ide u random
       # TODO budu veci ovi sto znaju vise
       # TODO napraviti fajl koji pusta simulacije, da bude onako kao robustness latin hyperc....
       # Na osnovu tumora i postavke da nam kaze najbolju populaciju, i pusta simulacije TODO ali kasnije
       # TODO smisslja igor kako velicina populacije da se odredi
       # TODO mutacije, nov random broj u tim okvirima 5%
       # TODO pogledati sve varijante evolutivnog algoritma, kako se razvijaju
       # TODO pogledati kako radi onaj jutjub kanal sto se tice umiranja



class CancerStemCell(CancerCell):
    def __init__(self,unique_id,model,value):
        super().__init__(unique_id,model,value)
        self.color = "#ff0000"
        self.points_if_eaten = value


class CureAgent(Agent):
    MOVING_STATE = "moving"
    STANDING_ON = "standing_on"
    ASSOCIATED_2 = "associated2"
    ASSOCIATED_1 = "associated1"

    
    def __init__(self,unique_id,model,speed,radoznalost,Pa,Pd,Pi,memory_size,memorija=None):
        super(CureAgent,self).__init__(unique_id,model)
        self.step_functions = {self.MOVING_STATE:self.step_move,
                      self.STANDING_ON:self.step_standing,
                      self.ASSOCIATED_1:self.step_associated1,
                      self.ASSOCIATED_2:self.step_associated2}
        self.memorija = FixSizeOrderedDict(max=memory_size) if memorija is None else memorija
        self.points = 0
        original_color = "#ffd700"
        r,g,b = get_rgb_from_hex(original_color)
        self.color = "#{}{}{}".format(r,add_to_color(g,-(speed*5)),b)
        self.size =0.2
        self.energy = np.inf
        self.speed = speed
        self.radoznalost = radoznalost
        self.memory_size = memory_size
        self.state = self.MOVING_STATE
        self.Pa = Pa #TODO
        self.Pd = Pd
        self.Pi = Pi

    def check_for_cells(self):
        cells = [f for f in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(f,Cell)]
        assert (len(cells)<=1)
        return cells

    
    def move(self):
        """The agents will move in a random direction and lose specified energy"""
        print(self.speed)
        for i in range(self.speed):
            possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self,new_position)

    def step(self):
        print(self.state)
        self.step_functions[self.state]()
        self.energy-=1 
        if self.energy==0:
            self.kill_self()

    def step_move(self):
        self.move()
        if self.check_for_cells():
            self.state = self.STANDING_ON

    def step_standing(self):
        cells = self.check_for_cells() #TODO ima puno ponavljano - napraviti generecno ! 
        if cells:
            cell = cells[0]
            associated = self.try_to_associate(cell)
            self.state = self.ASSOCIATED_1 if associated else self.MOVING_STATE
        else: #if it was eaten in meantime
            self.state = self.MOVING_STATE
            
    def step_associated1(self):
        cells = self.check_for_cells()
        if cells:
            cell = cells[0]
            self.state = choice([self.MOVING_STATE,self.ASSOCIATED_2],1,[self.Pd,1-self.Pd])[0]
            print("wtf")
            print(self.state)
            print(self.ASSOCIATED_2)
        else:
            self.state = self.MOVING_STATE

    def step_associated2(self):
        cells = self.check_for_cells()
        if cells:
            cell = cells[0]
            internalized = self.try_to_internalize(cell)
            self.state = self.MOVING_STATE if internalized else self.ASSOCIATED_1
        else:
            self.state = self.MOVING_STATE

    def try_to_associate(self,cell):
        """Tries to associate and refreshes memory with cell"""
        assert(self.radoznalost<=1 and self.radoznalost>=0)
        mem = self.memorija.get(cell.color,False)
        if not mem:
            Pa = self.radoznalost*self.Pa #TODO da li je OK ovako?
        elif mem>0:
            Pa = self.Pa
        elif mem<0:
            Pa= 0
        self.memorize(cell)
        associated = choice([True,False],1,[Pa,1-Pa])[0]
        print(associated)
        return associated

    def memorize(self,cell):
        self.memorija[cell.color] = cell.points_if_eaten
        self.size = 0.2 + 0.2*len(self.memorija) #jedino ce rasti, nikad se ne smanjuje
        
    def try_to_internalize(self,cell):
        internalized = choice([True,False],1,[self.Pi, 1- self.Pi])[0]
        if internalized:
            self.model.kill_cell(cell)
            self.points+=cell.points_if_eaten
        else:
            cell.stress()
        return internalized


    def kill_self(self):
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)





import math
import uuid
class CancerModel(Model):
    def __init__(self,cancer_cells_number,cure_number,eat_values, verovatnoca_mutacije,radoznalost):
        self.counter = 0
        Pi_range = np.arange(0,1,0.1)
        Pd_range = np.arange(0,1,0.1)
        Pa_range = np.arange(0,1,0.1)
        memory_range = [0,1,2,3] #TODO da li je max 3 ?
        self.cure_number = cure_number
        self.datacollector = DataCollector(
        model_reporters = {"FitnessFunction":fitness_funkcija,
                           "SpeedSum":overall_speed,"SmartMedicine":num_of_smart_medicine,
                           "RadoznalostSum":radoznalost_sum  })
        grid_size = math.ceil(math.sqrt(cancer_cells_number*4))
        self.grid = MultiGrid(grid_size,grid_size,False)
        speeds = list(range(grid_size//2)) 
        poss = self.generate_cancer_cell_positions(grid_size,cancer_cells_number)
        num_CSC = math.ceil(percentage(1,cancer_cells_number))
        pos_CSC = [self.random.choice(poss) for i in range(num_CSC)]
        self.schedule = RandomActivation(self)
        self.running = True
        for i in range(cancer_cells_number):
            pos = poss[i]
            c = CancerStemCell(uuid.uuid4(),self,value = eat_values[CancerStemCell.__class__]) if pos in pos_CSC else CancerCell(i,self,value=eat_values[CancerCell.__class__])
            self.grid.place_agent(c,pos)
            self.schedule.add(c)
        for i in range(cure_number):
            #pos = self.grid.find_empty()
            pos = (0,0)
            Pi = self.random.choice(Pi_range)
            Pd = self.random.choice(Pd_range)
            Pa = self.random.choice(Pa_range)
            speed = self.random.choice(speeds)
            memory_size = self.random.choice(memory_range)
            a = CureAgent(uuid.uuid4(),self,speed = speed,radoznalost=radoznalost,Pi=Pi,Pd=Pd,Pa=Pa,memory_size=memory_size) 
            self.grid.place_agent(a,pos)
            self.schedule.add(a)

        for (i,(contents, x,y)) in enumerate(self.grid.coord_iter()):
            if not contents:
                c = HealthyCell(uuid.uuid4(),self,eat_values[HealthyCell.__class__])
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


    def duplicate_or_kill(self):
        koliko = math.ceil(percentage(5,self.cure_number)) # TODO igor javlja kako biramo procena
        cureagents = [c for c in self.schedule.agents if isinstance(c,CureAgent)]
        sortirani = sorted(cureagents, key=lambda x: x.points, reverse=True)
        poslednji = sortirani[-koliko:]
        prvi = sortirani[:koliko]
        assert(len(prvi)==len(poslednji))
        self.remove_agents(poslednji)
        self.duplicate_agents(prvi)

    def remove_agents(self,agents):
        for a in agents:
            self.schedule.remove(a)
            self.grid.remove_agent(a)
    def duplicate_agents(self,agents):
        from copy import deepcopy
        for a in agents:
            a_new = a.__class__(uuid.uuid4(),model=self,speed = a.speed,radoznalost = a.radoznalost,Pa=a.Pa,Pd=a.Pd,Pi=a.Pi,memorija=a.memorija,memory_size = a.memory_size) 
            self.grid.place_agent(a_new,(1,1))
            self.schedule.add(a_new)

    def kill_cell(self,cell):
        self.grid.remove_agent(cell)
        self.schedule.remove(cell)
        

    def step(self):
        self.datacollector.collect(self)
        self.counter+=1
        self.schedule.step()
        if self.counter%10 ==0: # TODO ovo menjamo, parameter TODO
            #TODO sredi ovo pucanje zbog nule u latin hypercube
            #TODO napravi da je R promenljivo
            self.duplicate_or_kill()
        if self.counter%50 ==0: #TODO ovo da se zadaje
            _ = [c.grow() for c in self.schedule.agents if isinstance(c,CancerCell)]
        if self.counter%150 ==0: #TODO ovo da se zadaje
            _ = [c.grow() for c in self.schedule.agents if isinstance(c,HealthyCell)]
            
            
        

def fitness_funkcija(model):
    r = 5
    CSCs = [c for c in model.schedule.agents if isinstance(c,CancerStemCell)]
    CCs = [c for c in model.schedule.agents if isinstance(c,CancerCell)]
    HCs = [c for c in model.schedule.agents if isinstance(c,HealthyCell)]
    FF = len(HCs)/((r*len(CSCs)+ len(CCs) ))
    return FF

def overall_speed(model):
    cures = [c for c in model.schedule.agents if isinstance(c,CureAgent)]
    speeds = 0
    for c in cures:
        speeds+= c.speed

    return speeds

def num_of_smart_medicine(model):
    return sum([len(m.memorija) for m in model.schedule.agents if isinstance(m,CureAgent)])

def radoznalost_sum(model):
    return sum([c.radoznalost for c in model.schedule.agents if isinstance(c,CureAgent)])



