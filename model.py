from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from numpy.random import choice
import numpy as np
KILLING_PROBABILITY = 0.2
def percentage(percent, whole):
    return (percent * whole) / 100.0


class Cell(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        
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
#U ovom glavnom brisemo glupave, i onda preko parametra mogu da imaju 0 memoriju, 0 memoriju do 2
# agente mozemo da pustimo kojima je samo memorija nula
        
class CancerCell(Cell):
    def __init__(self,unique_id,model,value):
        super().__init__(unique_id,model)
        self.color = "#d3d3d3"
        self.points_if_eaten = value
    def stress(self):
        mutate = choice([True,False],1,p=[0.1,0.9])
        self.color = self.color if not mutate else self.mutate_color(self.color)
        print(self.color)

    

    def mutate_color(self,color_hex,by=5):
        r,g,b = get_rgb_from_hex(color_hex)
        print (r,g,b)
        r,g,b = [add_to_color(c,-20) for c in [r,g,b]]
        return "#{}{}{}".format(r,g,b)


       # TODO mutiramo 5% srednjih, ili speed ili radoznalost za jedan stepen
       # TODO budu veci ovi sto znaju vise
       # velicina memorije je stvar koja se selektuje
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
    def __init__(self,unique_id,model,speed,radoznalost):
        super(CureAgent,self).__init__(unique_id,model)
        import numpy as np
        self.points = 0
        original_color = "#ffd700"
        r,g,b = get_rgb_from_hex(original_color)
        self.color = "#{}{}{}".format(r,add_to_color(g,-(speed*5)),b)
        self.energy = np.inf
        self.speed = speed
        self.radoznalost = radoznalost


    


    def step(self):
        self.move()
        self.eat_or_not()
        self.energy-=1 
        if self.energy==0:
            self.kill_self()


    def move(self):
        """The agents will move in a random direction and lose specified energy"""

        for i in range(self.speed):
            possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self,new_position)

    def eat_function(self,c,verovatnoca):
        """Odredjuje kako koji agent jede, tj. logiku odlicivanja"""
        return choice([True,False],1,p=[verovatnoca,1-verovatnoca])

    def eat_or_not(self):
        cells = [f for f in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(f,Cell)]
        for c in cells:
            eat = self.eat_function(c,self.radoznalost)
            if eat:
                self.points+= c.points_if_eaten
                self.model.grid.remove_agent(c)
                self.model.schedule.remove(c)
            else:
                c.stress()
#            self.kill_self()
    def kill_self(self):
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)


#TODO ogranicenje memorije,
# TODO proverava da li je u memoriji
#TODO mozda nam nije potreban smart cure, vec da imamo memoriju od 0 pa na dalje
class SmartCureAgent(CureAgent):
    def __init__(self,unique_id,model,speed,radoznalost):
        super(SmartCureAgent,self).__init__(unique_id,model,speed,radoznalost)
        self.memorija = {}
        self.radoznalost = radoznalost
        self.color = "#8878c3"
        g = self.color[3:5]
        r = self.color[1:3]
        b= self.color[5:] #napravi ovo da bude neka funkcija u parent klasi TODO
        self.color = "#{}{}{}".format(r,add_to_color(g,-(speed*5)),b)

    def eat_function(self,celija,_):
        """Samo je ovo drugcije u odnosu na pretka"""
        mem = self.memorija.get(celija.color,0) 
        if mem>=0:
            self.memorija[celija.color] = celija.points_if_eaten
            verovatnoca =KILLING_PROBABILITY if mem>0 else self.radoznalost
            return super().eat_function(None,verovatnoca) 
        else:
            self.memorija[celija.color] = celija.points_if_eaten
            return False

import math
import uuid
class CancerModel(Model):
    def __init__(self,cancer_cells_number,cure_number,eat_values, verovatnoca_mutacije):
        self.counter = 0
        self.cure_number = cure_number
        radoznalosti = list(np.arange(0.01,KILLING_PROBABILITY,0.01))
        print(radoznalosti)
        self.datacollector = DataCollector(
        model_reporters = {"FitnessFunction":fitness_funkcija,
                           "SpeedSum":overall_speed,"SmartMedicine":num_of_smart_medicine,
                           "RadoznalostSum":radoznalost_sum  })
        grid_size = math.ceil(math.sqrt(cancer_cells_number*4))
        self.grid = MultiGrid(grid_size,grid_size,False)
        speeds = list(range(grid_size//2)) #popravi te boje TODO
        print(speeds)

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
            radoznalost = self.random.choice(radoznalosti)
            speed = self.random.choice(speeds)
            a = CureAgent(uuid.uuid4(),self,speed = speed,radoznalost=radoznalost) if i< cure_number//2 else SmartCureAgent(uuid.uuid4(),self,speed=speed,radoznalost = radoznalost)
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
        for a in agents:
            a_new = a.__class__(uuid.uuid4(),model=self,speed = a.speed,radoznalost = a.radoznalost) #TODO ostale parametre isto poistoveti
            self.grid.place_agent(a_new,(1,1))
            self.schedule.add(a_new)

    def step(self):
        self.datacollector.collect(self)
        self.counter+=1
        self.schedule.step()
        if self.counter%10 ==0: # TODO ovo menjamo, parameter TODO
            #TODO sredi boje i
            #TODO sredi ovo pucanje zbog nule u latin hypercube
            #TODO napravi da je R promenljivo
            self.duplicate_or_kill()
        

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
    return len([c for c in model.schedule.agents if isinstance(c,SmartCureAgent)])

def radoznalost_sum(model):
    return sum([c.radoznalost for c in model.schedule.agents if isinstance(c,CureAgent)])



