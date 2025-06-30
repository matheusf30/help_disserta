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
#import pandas as pd
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
def avisos(entrada):
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

def cdo_sel_AS():
	lat_max = 15
	lat_min = -60
	lon_max = -30
	lon_min = -90
	try:
		cdo.sellonlatbox(lon_min, lon_max, lat_min, lat_max,
					input = caminho_arquivo,
					output = caminho_arquivo_AS)
		print(f"{cyan}América do Sul\n{green}Seleção realizada com sucesso:\n{caminho_arquivo_AS}\n{reset}")
		os.remove(caminho_arquivo)
		print(f"{red}Remoção realizada com sucesso:\n{caminho_arquivo}\n{reset}")
	except:
		print(f"{red}NÃO HÁ ARQUIVOS PARA FAZER SELEÇÃO DE ÁREA:\n{caminho_arquivo}\n{reset}")

def abrindo_nc(entrada):
	tempo_inicio = time.time()
	entrada = xr.open_dataset(entrada)
	print(entrada)
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return entrada

def plot_temporal(entrada, str_var):
	tempo_inicio = time.time()
	entrada = entrada[str_var].plot.line(x = "time")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")

##### EXECUÇÕES ##################################################################
#clima_dia = clima_dia(caminho_arquivo, f"{caminho_dados}climatologia_diaria.nc4")
#clima_mes = clima_mes(caminho_arquivo, f"{caminho_dados}climatologia_mensal.nc4")
#clima_dia =  abrindo_nc(clima_dia)

avisos(f"{caminho_dados}climatologia_diaria.nc4")
clima_dia =  abrindo_nc(f"{caminho_dados}climatologia_diaria.nc4")
plot_temporal(clima_dia, "CO2")
#clima_dia.plot()











