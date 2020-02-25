from model import *
from mesa.visualization.modules import CanvasGrid,ChartModule
from mesa.visualization.ModularVisualization import ModularServer

import math

KOLICINA_CELIJA = 300
DIMENZIJA_TABLE = math.ceil(math.sqrt(KOLICINA_CELIJA*4))
BROJ_LEKOVA = 500
#RADOZNALOST_LEKOVA = 0.05 #bice random choice
eat_values = {CancerCell:1,HealthyCell:-1,CancerStemCell:5}
VEROVATNOCA_MUTACIJE = 0.1 #TODO za sad samo rak mutira, ne zdrave celije
RADOZNALOST_LEKOVA = 1 #ovo se mnozi sa verovatnocom internalizacije
#KORACI_EVOLUCIJE = 10 TODO
#MAX_ENERGY = 50 #TODO ubaciti


def agent_portrayal(agent):
    portrayal= {"Shape":"circle",
                "Filled":"true",
                "Layer":1,
                "Color":agent.color,
                "r":agent.size
                 }
    return portrayal

grid = CanvasGrid(agent_portrayal,DIMENZIJA_TABLE,DIMENZIJA_TABLE,500,500)

chart = ChartModule([{"Label": "FitnessFunction",
                      "Color": "black"}],
                    data_collector_name='datacollector')

chart_speed = ChartModule([{"Label": "SpeedSum",
                      "Color": "black"}],
                    data_collector_name='datacollector')

chart_smart = ChartModule([{"Label": "SmartMedicine",
                      "Color": "black"}],
                    data_collector_name='datacollector')

chart_rad = ChartModule([{"Label": "RadoznalostSum",
                      "Color": "black"}],
                    data_collector_name='datacollector')



server = ModularServer(CancerModel,[grid,chart,chart_speed,chart_smart,chart_rad],"Cancer Model",
                    {"cancer_cells_number":KOLICINA_CELIJA,"cure_number":BROJ_LEKOVA,
                     "eat_values":eat_values,"verovatnoca_mutacije":VEROVATNOCA_MUTACIJE,"radoznalost":RADOZNALOST_LEKOVA})
server.port = 8523
server.launch()




#1. popunjavamo sve delove sa healthy cells check_input
#2. implementiramo brzine, random choice brzine
#### lista brzina i onda svaki agent kojeg stavljamo ima random brzinu
#### mislim da je to ok svakako cemo do nekog balansa doci

# sad treba da mutiramo i eliminiramo u svakom koraku
#znaci u steps bude da se izracuna ta fitness funkcija, a ko proguta otrov ce dobiti nagradu
# za sada cemo samo ubijati npr 5% najgorih tj. 5% najboljih cemo umnoziti







