###################################################
## Arquivo adaptado para baixar dados do         ##
## NASA Center for Climate Simulation            ##
## High Performance Computing for Science        ##
## Dados: CO2                                    ##
## Demanda: Mabel Simm Milan Bueno               ##
## Adaptado por: Matheus Ferreira de Souza       ##
##               e Everton Weber Galliani        ##
## Data: 30/06/2025                              ##
###################################################

##### Bibliotecas correlatas ####################################################
#from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
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

##### FUNÇÕES ####################################################################
def avisos_sinfon(entrada):
	print(f"\n{green} ARQUIVO UTILIZADO INTEGRALMENTE:\n{cyan}{entrada}{reset}\n")
	tempo_inicio = time.time()
	summary = cdo.sinfon(input = entrada)
	print(summary)
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")

def clima_dia(entrada, saida):
	avisos(entrada)
	tempo_inicio = time.time()
	cdo.ydaymean(input = entrada, output = saida)
	print(f"\n{green}ARQUIVO SALVO:\n{reset}{saida}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def clima_mes(entrada, saida):
	avisos(entrada)
	tempo_inicio = time.time()
	cdo.ymonmean(input = entrada, output = saida)
	print(f"\n{green}ARQUIVO SALVO:\n{reset}{saida}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def cdo_mergetime(entrada, saida):
	cdo.mergetime(input = entrada, output = saida)

def cdo_sel_AS(entrada):
	lat_max = 15
	lat_min = -60
	lon_max = -30
	lon_min = -90
	try:
		cdo.sellonlatbox(lon_min, lon_max, lat_min, lat_max,
					input = f"caminho_dados{entrada}",
					output = f"caminho_dados{entrada}_AS")
		print(f"{cyan}América do Sul\n{green}Seleção realizada com sucesso:\n{caminho_dados}{entrada}_AS\n{reset}")
		os.remove(caminho_arquivo)
		print(f"{red}Remoção realizada com sucesso:\n{caminho_dados}{entrada}\n{reset}")
	except:
		print(f"{red}NÃO HÁ ARQUIVOS PARA FAZER SELEÇÃO DE ÁREA:\n{caminho_dados}{entrada}\n{reset}")

def abrindo_nc(entrada):
	tempo_inicio = time.time()
	entrada = xr.open_dataset(entrada)
	print(f"\n{green}ARQUIVO DE ENTRADA:\n{reset}{entrada}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return entrada

def tratando_nan(entrada, str_var):
	tempo_inicio = time.time()
	print(f"\n{green}ARQUIVO DE ENTRADA:\n{reset}{entrada}")
	metodo = input(f"{magenta}Escolha uma forma de tratamento de NaN\n'i' - interpolar\n'm' - preencher com média\n'd' - deletar NaN\n...\n{reset}")
	if metodo == "i":
		entrada = entrada[str_var].interpolate_na(method = "linear")
		print(f"\n{green}Tratamento de NaN por Interpolação:\n{reset}{entrada}")	
	elif metodo == "m":
		media = entrada[str_var].mean(skipna = True)
		entrada = entrada[str_var].fillna(media)
		print(f"\n{green}Tratamento de NaN por Preenchimento de Média:\n{reset}{entrada}")	
	elif metodo == "d":
		entrada = entrada[str_var].dropna()
		print(f"\n{green}Tratamento de NaN por Deleção:\n{reset}{entrada}")	
	else:
		print(f"\n{red}Escolha algum método de tratamento válido\n{reset}")		
	entrada = xr.open_dataset(entrada)
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return entrada

def plot_temporal(entrada, str_var, latitude, longitude, nivel = None, escala_temporal = None):
	tempo_inicio = time.time()
	ponto = entrada[str_var].sel(lat = latitude, lon = longitude, method = "nearest")
	ponto = ponto / 1000000
	if nivel != None:
		if isinstance(nivel, str):
			ponto_medio = ponto.mean(dim = "lev", skipna = True)
		elif isinstance(nivel, int):
			ponto_medio = ponto.sel(lev = nivel, method = "nearest")
	else:
		print("VAI DAR ERRO")	
	plt.figure(figsize = (12, 6), layout = "tight", frameon = False)
	ponto_medio.plot.line(x = "time", label = str_var, color = "red")
	plt.gca().patch.set_facecolor("honeydew")
	if isinstance(nivel, str):
		plt.title(f"Série de {str_var}, média dos {len(entrada.lev)} níveis no ponto de latitude ({latitude}) e longitude ({longitude})")
	elif isinstance(nivel, int):
		plt.title(f"Série de {str_var}, no ponto de altitude ({nivel}), latitude ({latitude}) e longitude ({longitude})")
	plt.grid(True)
	plt.legend()
	if escala_temporal == None:
		plt.xlabel("Tempo")
	else:
		plt.xlabel(f"Tempo ({escala_temporal})")
	plt.ylabel(str_var)
	plt.tight_layout()
	plt.show()
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return ponto_medio

def salvar_csv(caminho, entrada, nome_arquivo):
	_SALVAR = input(f"\n{magenta}Deseja salvar a série temporal em arquivo.csv? Se sim, digite 's': \n{reset}")
	if _SALVAR == "s":
		entrada_csv = entrada.to_dataframe().reset_index()
		entrada_csv.to_csv(f"{caminho_dados}{nome_arquivo}", index = False)
		print(f"\n{green}SALVANDO:\n{reset}{entrada_csv}\n")
	else:
		print(f"\n{green}Arquivo (.csv) NÃO salvo:\n{reset}{entrada}")	
	

##### EXECUÇÕES ##################################################################
#clima_dia = clima_dia(caminho_arquivo, f"{caminho_dados}climatologia_diaria.nc4")
#clima_mes = clima_mes(caminho_arquivo, f"{caminho_dados}climatologia_mensal.nc4")
#clima_dia =  abrindo_nc(clima_dia)

# Série Histórica (geos.chm.co2.201403_202412.nc4)
avisos_sinfon(f"{caminho_dados}geos.chm.co2.201403_202412.nc4")
serie_temporal =  abrindo_nc(f"{caminho_dados}geos.chm.co2.201403_202412.nc4")

remover_tempos = [ "2014-08-10 00:00:00", "2016-08-14 21:00:00",
					"2018-12-21 00:00:00", "2018-12-21 03:00:00"]
remover_tempos = np.array(remover_tempos, dtype = "datetime64")
serie_temporal = serie_temporal.sel(time = ~serie_temporal.time.isin(remover_tempos))
"""
print(f"\n{green}Série Temporal:\n{reset}{serie_temporal}")
plot_temporal(serie_temporal, "CO2", -27, -48, 1, "serie")
plot_temporal(serie_temporal, "CO2", -27, -48, "média", "serie")
"""
mudanca_metodologia = np.datetime64("2017-01-25 00:00:00")
serie_temporal_mudada = serie_temporal.sel(time = serie_temporal.time >= mudanca_metodologia)
"""
print(f"\n{green}Série Temporal (após mudança de metodologia):\n{reset}{serie_temporal_mudada}")
plot_temporal(serie_temporal_mudada, "CO2", -27, -48, 1, "serie (após mudança de metodologia)")
avisos_sinfon(f"{caminho_dados}geos.chm.co2.201403_202412.nc4")
"""
print(f"\n{green}Série Temporal (após mudança de metodologia):\n{reset}{serie_temporal_mudada}")
plot_temporal(serie_temporal_mudada, "CO2", -27, -48, "média", "serie (após mudança de metodologia)")
avisos_sinfon(f"{caminho_dados}geos.chm.co2.201403_202412.nc4")

# Climatologia Diária
avisos_sinfon(f"{caminho_dados}climatologia_diaria.nc4")
clima_dia =  abrindo_nc(f"{caminho_dados}climatologia_diaria.nc4")
print(f"\n{green}Climatologia Diária:\n{reset}{clima_dia}")
ponto_medio_dia = plot_temporal(clima_dia, "CO2", -27, -48, 1, "dias") #lev = "SIM"
#salvar_csv(f"{caminho_dados}", ponto_medio_dia, "climatologia_diaria.csv") 
ponto_medio_dia = plot_temporal(clima_dia, "CO2", -27, -48, "média", "dias") 
# Climatologia Mensal
avisos_sinfon(f"{caminho_dados}climatologia_mensal.nc4")
clima_mes =  abrindo_nc(f"{caminho_dados}climatologia_mensal.nc4")
print(f"\n{green}Climatologia Mensal:\n{reset}{clima_mes}")
ponto_medio_mes = plot_temporal(clima_mes, "CO2", -27, -48, 1, "meses")
#salvar_csv(f"{caminho_dados}", ponto_medio_mes, "climatologia_mensal.csv") 
ponto_medio_mes = plot_temporal(clima_mes, "CO2", -27, -48, "média", "meses")
#sys.exit()
#clima_dia.plot()











