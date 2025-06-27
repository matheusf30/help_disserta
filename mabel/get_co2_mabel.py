"""
>>> crontab -e
>>> 0 0 * * 0 /usr/bin/python3 /home/sifapsc/scripts/matheus/dengue/get_dengue.py >> /home/sifapsc/scripts/matheus/dengue/get_dengue.log 2>&1
>>> crontab -l

# Nasa NCCS GEOS-FP
https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/das/
# CDO
https://code.mpimet.mpg.de/projects/cdo/wiki/Cdo%7Brbpy%7D
https://pypi.org/project/cdo/
https://www.ecmwf.int/sites/default/files/elibrary/2018/18722-cdos-python-bindings.pdf
"""

##### Bibliotecas correlatas ####################################################
#from bs4 import BeautifulSoup
#import pandas as pd
#import schedule
import os, sys
import time
from datetime import datetime
import requests
from tqdm import tqdm
#import cfgrib
import xarray as xr
import netCDF4
import glob
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
#################################################################################

ano_atual = str(datetime.today().year)
hoje = datetime.today().strftime("%Y-%m-%d")
_ANOS = list(range(2014, 2026, 1))#list(range(2014, 2025, 1))
_MESES = [f"{m:02d}" for m in range(1, 13, 1)]
_DIAS = [f"{d:02d}" for d in range(13, 32, 1)]
_ZULUS = [f"{z:02d}" for z in range(0, 24, 3)]
'''
_ANOS = sorted(_ANOS, reverse = True)
_MESES = sorted(_MESES, reverse = True)
_DIAS = sorted(_DIAS, reverse = True)
'''
print(f"""
{green}\nANOS: {reset}{_ANOS}
{green}\nMESES: {reset}{_MESES}
{green}\nDIAS: {reset}{_DIAS}
{green}\nHORAS: {reset}{_ZULUS}\n""")

_ANO = 2022
_MES = "04"
_DIA = "05"
_ZULU = "00"

#sys.exit()
#### Definindo Função ###########################################################

def download_co2():
	print(f"""
{green}\nANO: {reset}{_ANO}
{green}\nMÊS: {reset}{_MES}
{green}\nDIA: {reset}{_DIA}
{green}\nHORA: {reset}{_ZULU}\n""")
	#https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/das/Y2014/M12/D08/
	#### Definindo Variáveis
	url_nasa = "https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/das/"
	filtro_crono = f"Y{_ANO}/M{_MES}/D{_DIA}/"
	arquivo = f"GEOS.fp.asm.inst3_3d_chm_Nv.{_ANO}{_MES}{_DIA}_{_ZULU}00.V01.nc4"
	url_nccs = f"{url_nasa}{filtro_crono}{arquivo}"

	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/novo/"
	nome_arquivo = f"geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	caminho_arquivo = f"{caminho_dados}{nome_arquivo}"
	caminho_arquivo_AS = f"{caminho_dados}AS_geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"

	if os.path.exists(caminho_arquivo_AS):
		tamanho_recortado = os.path.getsize(caminho_arquivo_AS)
		print(f"{reset}\n\n{tamanho_recortado}{cyan} =~= {reset}{int(tamanho_recortado/1000000)}M\n\n")
		tamanho_recortado = int(tamanho_recortado/1000000)
		if tamanho_recortado == 67:
			print(f"{reset}\n\n{cyan} Tamanho do Arquivo =~= {reset}{tamanho_recortado}M\n\n")
			print(f"{cyan}\nARQUIVO EXISTENTE:\n{reset}{caminho_arquivo}")
			return
		else:
			resposta = requests.get(url_nccs, stream = True)
			tamanho_original = int(resposta.headers.get("content-length", 0))
			print(f"{reset}\n\n{tamanho_original/1000000}{red} =!= {reset}{tamanho_recortado}\n\n")
			print(f"{red}\nARQUIVO INCOMPLETO:\n{reset}{caminho_arquivo}")
			print(f"{cyan}\n\nREINICIANDO DOWNLOAD!\n\n{reset}")
			try:
				resposta = requests.get(url_nccs, stream = True)
				resposta.raise_for_status()
				tamanho_original = int(resposta.headers.get("content-length", 0))
				progresso = tqdm(total = tamanho_original, unit = "B", unit_scale = True,
									desc = os.path.basename(caminho_arquivo))
				if resposta.status_code == 200:
					os.makedirs(caminho_dados, exist_ok = True)
					with open(caminho_arquivo, "wb") as file:
						for chunk in resposta.iter_content(chunk_size = 1024*1024):
							file.write(chunk)
							progresso.update(len(chunk))
					progresso.close()
					print(f"{green}\nDownload realizado com sucesso e salvo como:\n{caminho_dados}\n{nome_arquivo}\n{reset}")
				else:
					print(f"""
			{red}Falha ao realizar download do arquivo diretamente de: {url_nccs}
			{resposta.status_code}
			{resposta.text}
			{nome_arquivo}\n{reset}""")
			except requests.exceptions.RequestException as e:
				print(f"\n{red}RequestException:\n\n{e}\n\n{url_nccs}\n{reset}")		
	else:
		resposta = requests.get(url_nccs, stream = True)
		tamanho_original = int(resposta.headers.get("content-length", 0))
		print(f"{reset}\n\n{tamanho_original/1000000}{red} !!!{reset}\n\n")
		print(f"{red}\nARQUIVO NUNCA BAIXADO:\n{reset}{caminho_arquivo}")
		print(f"{cyan}\n\nINICIANDO DOWNLOAD!\n\n{reset}")
		try:
			resposta = requests.get(url_nccs, stream = True)
			resposta.raise_for_status()
			tamanho_original = int(resposta.headers.get("content-length", 0))
			progresso = tqdm(total = tamanho_original, unit = "B", unit_scale = True,
								desc = os.path.basename(caminho_arquivo))
			if resposta.status_code == 200:
				os.makedirs(caminho_dados, exist_ok = True)
				with open(caminho_arquivo, "wb") as file:
					for chunk in resposta.iter_content(chunk_size = 1024*1024):
						file.write(chunk)
						progresso.update(len(chunk))
				progresso.close()
				print(f"{green}\nDownload realizado com sucesso e salvo como:\n{caminho_dados}\n{nome_arquivo}\n{reset}")
			else:
				print(f"""
		{red}Falha ao realizar download do arquivo diretamente de: {url_nccs}
		{resposta.status_code}
		{resposta.text}
		{nome_arquivo}\n{reset}""")
		except requests.exceptions.RequestException as e:
			print(f"\n{red}RequestException:\n\n{e}\n\n{url_nccs}\n{reset}")

def cdo_mergetime():
	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/novo/"
	nome_arquivo = f"geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	caminho_arquivo = f"{caminho_dados}{nome_arquivo}"
	entrada = glob.glob(f"{caminho_dados}geos.chm.201412*.nc4")
	cdo.mergetime(input = entrada, output = f"{caminho_dados}geos.chm.{_ANO}{_MES}.nc4")
	#os.remove(entrada)

def cdo_sel_AS():
	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/novo/"
	nome_arquivo = f"geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	caminho_arquivo = f"{caminho_dados}{nome_arquivo}"
	caminho_arquivo_AS = f"{caminho_dados}AS_geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
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

#################################################################################
#for _DIA in _DIAS:
for _ZULU in _ZULUS:
	download_co2()
	cdo_sel_AS()
sys.exit()
#### Automatizando totais de arquivos do dia em diferentes horários #############
for _ANO in _ANOS:
	for _MES in _MESES:
		for _DIA in _DIAS:
			for _ZULU in _ZULUS:
				download_co2()
				cdo_sel_AS()
"""
remover = glob.glob(f"{caminho_dados}geos.chm.201412*.nc4")
print(remover)
os.remove("".join(remover))
"""
#################################################################################
