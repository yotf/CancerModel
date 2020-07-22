from model import *
from mesa.visualization.modules import CanvasGrid,ChartModule
from mesa.visualization.ModularVisualization import ModularServer

import math

KOLICINA_CELIJA = 320
DIMENZIJA_TABLE = math.ceil(math.sqrt(KOLICINA_CELIJA*4))
BROJ_LEKOVA = 500
RADOZNALOST_LEKOVA = 0.5 

def agent_portrayal(agent):
    portrayal= {"Shape":"circle",
                "Filled":"true",
                "Layer":1,
                "Color":agent.color,
                "r":1
                 }
    return portrayal

grid = CanvasGrid(agent_portrayal,DIMENZIJA_TABLE,DIMENZIJA_TABLE,500,500)

chart = ChartModule([{"Label": "FitnessFunction",
                      "Color": "black"}],
                    data_collector_name='datacollector')


server = ModularServer(CancerModel,[grid,chart],"Cancer Model",
                       {"cancer_cells_number":KOLICINA_CELIJA,"cure_number":BROJ_LEKOVA,"radoznalost":RADOZNALOST_LEKOVA,"cure_agent_type":CureAgent})
server.port = 8523
server.launch()

