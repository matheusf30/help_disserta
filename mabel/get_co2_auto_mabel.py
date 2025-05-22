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
from datetime import datetime, timedelta
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

_ANO = str(datetime.today().year)
_MES = datetime.today().strftime("%m")
_HOJE = datetime.today().strftime("%d")
_ONTEM = datetime.today() - timedelta(days = 1)
_ANTEONTEM = datetime.today() - timedelta(days = 2)
_ANO_ONTEM = _ONTEM.strftime("%Y")
_ANO_ANTEONTEM = _ANTEONTEM.strftime("%Y")
_MES_ONTEM = _ONTEM.strftime("%m")
_MES_ANTEONTEM = _ANTEONTEM.strftime("%m")
_ONTEM = _ONTEM.strftime("%d")
_ANTEONTEM = _ANTEONTEM.strftime("%d")
_ZULUS = [f"{z:02d}" for z in range(0, 24, 3)]

_LISTA_DATAS = [_ANO_ANTEONTEM, _ANO_ONTEM, _ANO,
				_MES_ANTEONTEM, _MES_ONTEM, _MES,
				_ANTEONTEM, _ONTEM, _HOJE, _ZULUS]

print(f"""
{green}\nANO: {reset}{_ANO}
{green}\nMÊS: {reset}{_MES}
{green}\nDIA ATUAL: {reset}{_HOJE}
{green}\nHORAS: {reset}{_ZULUS}\n""")

print(f"\n{green}LISTA DE DATAS:\n{reset}{_LISTA_DATAS}\n")

#sys.exit()
#### Definindo Função ###########################################################

def download_co2(_ANO, _MES, _DIA):
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

	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/"
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
			print(f"{reset}\n\n{tamanho_original/1000000}{red} =!= {reset}{tamanho_recortado/1000000}\n\n")
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
	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/"
	nome_arquivo = f"geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	caminho_arquivo = f"{caminho_dados}{nome_arquivo}"
	entrada = glob.glob(f"{caminho_dados}geos.chm.201412*.nc4")
	cdo.mergetime(input = entrada, output = f"{caminho_dados}geos.chm.{_ANO}{_MES}.nc4")
	#os.remove(entrada)

def cdo_sel_AS(_ANO, _MES, _DIA):
	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/"
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

#### Automatizando totais de arquivos do dia em diferentes horários #############
for _ZULU in _ZULUS:
	# Hoje
	download_co2(_ANO, _MES, _HOJE)
	cdo_sel_AS(_ANO, _MES, _HOJE)
	# Ontem
	download_co2(_ANO_ONTEM, _MES_ONTEM, _ONTEM)
	cdo_sel_AS(_ANO_ONTEM, _MES_ONTEM, _ONTEM)
	# Anteontem
	download_co2(_ANO_ANTEONTEM, _MES_ANTEONTEM, _ANTEONTEM)
	cdo_sel_AS(_ANO_ANTEONTEM, _MES_ANTEONTEM, _ANTEONTEM)
"""
remover = glob.glob(f"{caminho_dados}geos.chm.201412*.nc4")
print(remover)
os.remove("".join(remover))
"""
#################################################################################
