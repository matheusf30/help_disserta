###################################################
## Arquivo adaptado para comparar dados do       ##
## NASA Center for Climate Simulation            ##
## High Performance Computing for Science        ##
## Dados: CO2 (GEOS-FP x OCO2)                   ##
## Demanda: Mabel Simm Milan Bueno               ##
## Adaptado por: Matheus Ferreira de Souza       ##
##               e Everton Weber Galliani        ##
## Data: 30/06/2025                              ##
###################################################

##### Bibliotecas correlatas ####################################################
#from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import linregress
#import schedule
import os, sys, glob
import time
from datetime import datetime
import requests
from tqdm import tqdm
#import cfgrib
import xarray as xr
import netCDF4
import matplotlib.pyplot as plt
from cdo import Cdo
cdo = Cdo()
#help(cdo.sinfov)

##### Padrão ANSI ###############################################################
bold = "\033[1m"
red = "\033[91m"
green = "\033[92m"
yellow = "\033[33m"
blue = "\033[34m"
magenta = "\033[35m"
cyan = "\033[36m"
white = "\033[37m"
reset = "\033[0m"

##### CAMINHOS ###################################################################
caminho_dados = "/dados4/operacao/geos_fp/co2/"
nome_arquivo = "geos.chm.co2.201403_202412.nc4" #sys.argv[1]
caminho_arquivo = f"{caminho_dados}{nome_arquivo}"
caminho_resultados = "/home/sifapsc/scripts/matheus/help_disserta/mabel/resultados/matheus"


### EXECUÇÕES #####################################################################
serie_floripa_oco2 = pd.read_csv("/home/sifapsc/scripts/matheus/help_disserta/mabel/serie_floripa.txt")
#, sep = "\t")
serie_floripa_geos = pd.read_csv("/dados4/operacao/geos_fp/co2/serie_temporal_mensal_floripa.csv")
print(f"\n{green}Série Floripa (OCO2) COLUNAS:\n{reset}{serie_floripa_oco2.columns}")
serie_floripa_oco2.drop(columns = ["Unnamed: 0", "Unnamed: 5", "lat", "lon"], inplace = True)
serie_floripa_oco2 = serie_floripa_oco2.rename(columns = {"date": "data", "value": "OCO2"})
serie_floripa_oco2["OCO2"] = serie_floripa_oco2["OCO2"] * 1000000
serie_floripa_oco2["data"] = pd.to_datetime(serie_floripa_oco2["data"])
serie_floripa_oco2 = serie_floripa_oco2.set_index("data").resample("M").mean()
serie_floripa_geos = serie_floripa_geos[serie_floripa_geos["bnds"] == 1]
serie_floripa_geos = serie_floripa_geos[["time", "CO2"]]
serie_floripa_geos["time"] = pd.to_datetime(serie_floripa_geos["time"]).dt.strftime("%Y-%m-%d")
serie_floripa_geos["time"] = pd.to_datetime(serie_floripa_geos["time"])
serie_floripa_geos = serie_floripa_geos.rename(columns = {"CO2": "GEOS-FP"})
serie_floripa_geos = serie_floripa_geos.set_index("time").resample("M").mean()
print(f"\n{green}Série Floripa (OCO2):\n{reset}{serie_floripa_oco2}\n{serie_floripa_oco2.info()}")
print(f"\n{green}Série Floripa (GEOS-FP):\n{reset}{serie_floripa_geos}\n{serie_floripa_geos.info()}")
serie_floripa_co2 = serie_floripa_oco2.merge(serie_floripa_geos, how = "right",
												left_index = True, right_index = True)
print(f"\n{green}Série Floripa CO2 (OCO2 x GEOS-FP):\n{reset}{serie_floripa_co2}")
print(f"\n{green}Série Floripa CO2 (OCO2 x GEOS-FP):\n{reset}{serie_floripa_co2.info()}")
#sys.exit()

########################### VISUALIZANDO SÉRIES TEMPORAIS
plt.figure(figsize = (12, 6), layout = "tight", frameon = False)
serie_floripa_co2["OCO2"].plot.line(x = "data", label = "CO2 (OCO2)", color = "orange")
serie_floripa_co2["GEOS-FP"].plot.line(x = "data", label = "CO2 (GEOS-FP)", color = "red")
plt.gca().patch.set_facecolor("honeydew")
plt.title(f"Série de CO2 (OCO2 x GEOS-FP), no ponto de  latitude (-27.5954), longitude (-48.54) e média das 72 altitudes")
plt.grid(True)
plt.legend()
plt.xlabel("Tempo (meses)")
plt.ylabel("CO2 (ppm)")
plt.tight_layout()
plt.show()
#sys.exit()

########################### AJUSTANDO REGRESSÃO LINEAR
oco2 = serie_floripa_co2.dropna(axis = 0)
oco2_tempo = oco2.index

oco2_tempo_num = mdates.date2num(oco2_tempo)
oco2_valor = oco2["OCO2"].values
#angulo, intercepto = np.polyfit(tempo_num, co2_valor, deg = 1)
oco2_angulo, oco2_intercepto, oco2_r, oco2_p_value, oco2_desvio_padrao = linregress(oco2_tempo_num, oco2_valor)
oco2_regressao = oco2_angulo * oco2_tempo_num + oco2_intercepto

geos = serie_floripa_co2["GEOS-FP"]
geos_tempo = serie_floripa_co2.index
geos_tempo_num = mdates.date2num(geos_tempo)
geos_valor = geos.values
#angulo, intercepto = np.polyfit(tempo_num, co2_valor, deg = 1)
geos_angulo, geos_intercepto, geos_r, geos_p_value, geos_desvio_padrao = linregress(geos_tempo_num, geos_valor)
geos_regressao = geos_angulo * geos_tempo_num + geos_intercepto

plt.figure(figsize = (12, 6), layout = "tight", frameon = False)
plt.plot(oco2_tempo, oco2_valor, label = "OCO2", color = "orange")
plt.plot(oco2_tempo, oco2_regressao, label = f"Regressão Linear (OCO2) [y = {oco2_angulo:.4f} * X + {oco2_intercepto:.2f}]\n(R² = {oco2_r**2:.3f}, p = {oco2_p_value})", color = "blue", linestyle = "--") #, desvio padrão = {desvio_padrao}
plt.gca().patch.set_facecolor("honeydew")
plt.plot(geos_tempo, geos_valor, label = "GEOS-FP", color = "red")
plt.plot(geos_tempo, geos_regressao, label = f"Regressão Linear (GEOS-FP) [y = {geos_angulo:.4f} * X + {geos_intercepto:.2f}]\n(R² = {geos_r**2:.3f}, p = {geos_p_value})", color = "darkblue", linestyle = "--") #, desvio padrão = {desvio_padrao}
plt.gca().patch.set_facecolor("honeydew")
plt.title(f"Série de CO2 (OCO2 x GEOS-FP) e Regressão Linear, no ponto de latitude (-27.5954), longitude (-48.54) e média das 72 altitudes")
plt.grid(True)
plt.legend()
plt.xlabel("Tempo (meses)")
plt.ylabel("CO2 (ppm)")
plt.tight_layout()
plt.show()
