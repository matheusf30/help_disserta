##### Bibliotecas correlatas ####################################################
import os, sys, glob
import time
from datetime import datetime
from cdo import Cdo
cdo = Cdo()

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

##### Tempos ####################################################################
ano_atual = str(datetime.today().year)
hoje = datetime.today().strftime("%Y-%m-%d")
_ANOS = list(range(2014, 2026, 1))#list(range(2014, 2025, 1))
_MESES = [f"{m:02d}" for m in range(1, 13, 1)]
_DIAS = [f"{d:02d}" for d in range(1, 32, 1)]
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

_ANO = 2014
_MES = "08"
_DIA = "05"
_ZULU = "00"
_DIAS = [f"{d:02d}" for d in range(6, 32, 1)]
##### Funções ####################################################################
def cdo_sel_AS():
	caminho_dados = f"/dados3/operacao/geos_fp/{_ANO}/{_MES}/{_DIA}/"
	nome_arquivo = f"geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	caminho_arquivo = f"{caminho_dados}{nome_arquivo}"
	caminho_arquivo_AS = f"{caminho_dados}AS_geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	caminho_arquivo_AS_novo = f"{caminho_dados}novoAS_geos.chm.{_ANO}{_MES}{_DIA}{_ZULU}.nc4"
	lat_max = 15
	lat_min = -60
	lon_max = -30.3125
	lon_min = -90
	try:
		cdo.sellonlatbox(lon_min, lon_max, lat_min, lat_max,
					input = caminho_arquivo_AS,
					output = caminho_arquivo_AS_novo)
		print(f"{cyan}América do Sul\n{green}Seleção realizada com sucesso:\n{caminho_arquivo_AS_novo}\n{reset}")
		os.remove(caminho_arquivo_AS)
		print(f"{red}Remoção realizada com sucesso:\n{caminho_arquivo_AS}\n{reset}")
		os.rename(caminho_arquivo_AS_novo, caminho_arquivo_AS)
		print(f"""
{green}Renomeação realizada com sucesso:
{purple}{caminho_arquivo_AS_novo}
{green}>>>>>>>>>>>>>>>
{cyan}{caminho_arquivo_AS}\n{reset}""")
	except:
		print(f"{red}NÃO HÁ ARQUIVOS PARA FAZER SELEÇÃO DE ÁREA:\n{caminho_arquivo_AS}\n{reset}")

##### Execuções ####################################################################
for _DIA in _DIAS:
#_ZULUS = [18, 21] # 2022/04/05 # > 2022/04/06
for _ZULU in _ZULUS:
	cdo_sel_AS()
"""
	remover = glob.glob(f"{caminho_dados}geos.chm.201412*.nc4")
	print(remover)
	os.remove("".join(remover))
"""


