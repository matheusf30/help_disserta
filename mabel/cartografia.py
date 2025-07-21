###################################################
## Arquivo adaptado para mapear informações      ##
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
from netCDF4 import Dataset
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.colors as cls
import numpy as np
import pandas as pd
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import cartopy.feature as cfeature
import cmocean
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

##### FUNÇÕES ####################################################################
def avisos_sinfon(entrada):
	print(f"\n{green} ARQUIVO UTILIZADO INTEGRALMENTE:\n{cyan}{entrada}{reset}\n")
	tempo_inicio = time.time()
	summary = cdo.sinfon(input = entrada)
	print(summary)
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")

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

def clima_dia(entrada, saida):
	avisos_sinfon(entrada)
	tempo_inicio = time.time()
	cdo.ydaymean(input = entrada, output = saida)
	print(f"\n{green}ARQUIVO SALVO:\n{reset}{saida}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def clima_mes(entrada, saida):
	avisos_sinfon(entrada)
	tempo_inicio = time.time()
	cdo.ymonmean(input = entrada, output = saida)
	print(f"\n{green}ARQUIVO SALVO:\n{reset}{saida}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def cdo_mergetime(entrada, saida):
	avisos_sinfon(entrada)
	tempo_inicio = time.time()
	cdo.mergetime(input = entrada, output = saida)
	print(f"\n{green}ARQUIVO SALVO:\n{reset}{saida}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def media_vertical(entrada, saida):
	avisos_sinfon(entrada)
	tempo_inicio = time.time()
	cdo.vertmean(input = entrada, output = saida)
	print(f"\n{green}ARQUIVO SALVO:\n{reset}{saida}")
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def selecionar_tempo_espaco(entrada, str_var, data, lat_min, lat_max, lon_min, lon_max):
	avisos_sinfon(entrada)
	tempo_inicio = time.time()
	data = np.array(data, dtype = "datetime64")
	print(f"\n{green}DATA:\n{reset}{data}\n")
	entrada["time"] = entrada["time"].strftime("%Y-%m-%d")
	saida = entrada.sel(time = f"{data}",
						lat = slice(lat_min, lat_max),
						lon = slice(lon_min, lon_max))[str_var].squeeze()
	tempo_final = time.time()
	tempo_processo = tempo_final - tempo_inicio
	print(f"\n{green}TEMPO DE PROCESSAMENTO:\n{reset}{tempo_processo:.2f} s.\n")
	return saida

def cdo_recorta_area(entrada, lon_min, lon_max, lat_min, lat_max, saida):
	try:
		cdo.sellonlatbox(lon_min, lon_max, lat_min, lat_max,
						input = entrada,
						output = saida)
		print(f"{cyan}Seleção:{lon_min},{lon_max},{lat_min},{lat_max}\n{green}Seleção realizada com sucesso:\n{caminho_dados}{entrada}_AS\n{reset}")
		_REMOVER = input(f"\n{magenta}Deseja remover o arquivo de entrada? Se sim, digite 's': \n{reset}")
		if _REMOVER == "s":
			os.remove(entrada)
			print(f"\n{green}REMOVENDO:\n{reset}{entrada}\n")
		else:
			print(f"\n{green}Arquivo NÃO removido:\n{reset}{entrada}")
	except:
		print(f"{red}NÃO HÁ ARQUIVOS PARA FAZER SELEÇÃO DE ÁREA:\n{entrada}\n{reset}")
	return saida

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
		print("VAI DAR ERRO OU NÃO")	
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
	return entrada_csv

def salvar_nc4(caminho, entrada, nome_arquivo):
	_SALVAR = input(f"\n{magenta}Deseja salvar a série temporal em arquivo.nc4? Se sim, digite 's': \n{reset}")
	if _SALVAR == "s":
		entrada_nc4 = entrada.to_netcdf(f"{caminho_dados}{nome_arquivo}", engine = "netcdf4", format = "NETCDF4")
		print(f"\n{green}SALVANDO:\n{reset}{entrada_nc4}\n")
	else:
		print(f"\n{green}Arquivo (.nc4) NÃO salvo:\n{reset}{entrada}")
	return entrada_nc4

"""
#data = "2024-06"
data=sys.argv[1] 
# Explodir a variável em ano e mês
ano, mes = data.split('-')
"""

def plotar_tempo_espaco(entrada):
	plt.figure(figsize = (12, 6), layout = "tight", frameon = False)
	maxi = entrada.max().item()
	int_max = int(maxi) + 10
	print(f"Valor máximo da variável na região selecionada: {int_max}")
	ax = plt.axes(projection = ccrs.PlateCarree())
	shp = list(shpreader.Reader("/home/sifapsc/scripts/matheus/help_disserta/mabel/BR_UF_2022.shp").geometries())
	colors = ["#b4f0f0", "#96d2fa", "#78b9fa", "#3c95f5", "#1e6deb", "#1463d2", 
		      "#0fa00f", "#28be28", "#50f050", "#72f06e", "#b3faaa", "#fff9aa", 
		      "#ffe978", "#ffc13c", "#ffa200", "#ff6200", "#ff3300", "#ff1500", 
		      "#c00100", "#a50200", "#870000", "#653b32"]
	cmap = matplotlib.colors.ListedColormap(colors)
	cmap.set_over('#000000')
	cmap.set_under('#ffffff')
	data_min = 0
	data_max = int_max
	interval = 1
	levels = np.arange(data_min, data_max + interval, interval)
	figure = entrada.plot.pcolormesh(robust = True,
									norm = cls.Normalize(vmin = 0, vmax = int_max),
									cmap = cmap, add_colorbar = False,
									levels = levels, add_labels = False)
	ax.add_geometries(shp, ccrs.PlateCarree(), edgecolor = "gray", facecolor = "none", linewidth = 0.3)
	ax.coastlines(resolution = "10m", color = "black", linewidth = 0.8)
	ax.add_feature(cartopy.feature.BORDERS, edgecolor = "black", linewidth = 0.5)
	gl = ax.gridlines(crs = ccrs.PlateCarree(), color = "white", alpha = 1.0, linestyle = "--", linewidth = 0.25, xlocs = np.arange(-180, 180, 5), ylocs = np.arange(-90, 90, 5), draw_labels = True)
	gl.top_labels = False
	gl.right_labels = False
	plt.colorbar(figure, pad = 0.05, fraction = 0.05, extend = "max", ticks = np.arange(0, int_max, 50), orientation = "vertical", label = str_var)
	plt.title(f"Precipitação Acumulada Mensal (mm) - Sul do Brasil\nPeríodo observado: {mes}/{ano}",
			fontsize = 14, ha = "center")
	plt.figtext(0.55, 0.05, "Fonte: MERGE - CPTEC", ha = "center", fontsize = 10)
	plt.savefig(f"/media/produtos/merge/monthly/2024/prec_mensal_merge_{ano}{mes}.jpg",
				transparent = True, dpi = 300, bbox_inches = "tight", pad_inches = 0.02)

	plt.show()

##### EXECUÇÕES ##################################################################
# /dados4/operacao/geos_fp/co2/geos.serie_mensal.co2.depois.nc4
# /dados4/operacao/geos_fp/co2/geos.serie_diaria.co2.depois.nc4
avisos_sinfon(f"{caminho_dados}geos.serie_diaria.co2.depois.nc4")
floripa = abrindo_nc(f"{caminho_dados}geos.serie_diaria.co2.depois.nc4")
floripa_mes = abrindo_nc(f"{caminho_dados}geos.serie_mensal.co2.depois.nc4")
lat_min, lat_max, lon_min, lon_max = -48.30, -48.75, -27.45, -27.90
"""
floripa = floripa.sel(lat = slice(lat_min, lat_max),
						lon = slice(lon_min, lon_max))

.sel(lat = slice(lat_min, lat_max),
						lon = slice(lon_min, lon_max))
floripa = cdo_recorta_area(f"{caminho_dados}serie_temporal_diaria.nc",
							lon_min, lon_max, lat_min, lat_max,
							f"{caminho_dados}serie_temporal_diaria_floripa.nc")



serie_dia = selecionar_tempo_espaco(serie_dia, "CO2", "2021-02-18",
									-48.30, -48.75, -27.45, -27.90)
plotar_tempo_espaco(serie_dia)

datas = ["2021-02-18 00:00:00", "2021-05-29 00:00:00",
		"2021-07-28 00:00:00", "2021-10-25 00:00:00"]

"""
##### DIÁRIAS
#dias = pd.to_datetime(["2021-02-18", "2021-05-29", "2021-07-28", "2021-10-25"])
fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(12, 8), frameon = False,
						subplot_kw={"projection": ccrs.PlateCarree()})
axes = axes.flatten()
dias = ["2021-02-18", "2021-05-29", "2021-07-28", "2021-10-25"]
for i, dia in enumerate(dias):
#dia = np.array("2021-02-18", dtype = "datetime64")
	co2 = floripa["CO2"].sel(time = dia).mean(dim = "lev")
	co2 = co2 * 1000000
	im = co2.plot(ax = axes[i], transform = ccrs.PlateCarree(),
					cmap = "coolwarm", add_colorbar = False) # "viridis_r" copper_r coolwarm magma inferno_r
	axes[i].coastlines()
	axes[i].gridlines(draw_labels = True, dms = True, linestyle = ":",
						x_inline = False, y_inline = False)
	axes[i].set_title(f"Concentração de CO2 (GEOS-FP v-5.16): {dia}")

fig.colorbar(im, ax = axes, orientation = "vertical",
			fraction = 0.03, pad = 0.1, label = "CO2 (ppm)")
plt.tight_layout(rect = [0, 0, 0.95, 1])
plt.suptitle("Concentração de CO2 (GEOS-FP v-5.16)", fontsize = 16, y = 1.02)
#plt.savefig('co2_maps.png')
plt.show()
plt.close(fig)

#sys.exit()

for i, dia in enumerate(dias):
	fig, ax = plt.subplots(figsize=(10, 8), frameon = False,
							subplot_kw={"projection": ccrs.PlateCarree()})
	co2 = floripa["CO2"].sel(time = dia).mean(dim = ["time", "lev"])
	co2 = co2 * 1000000
	co2.plot(ax = ax, transform = ccrs.PlateCarree(),
			cmap = "coolwarm", cbar_kwargs={"label" : "CO2 (ppm)",
											"shrink" : 0.7,
											"pad" : 0.1})
	ax.coastlines()
	ax.gridlines(draw_labels = True, dms = True, linestyle = ":",
					x_inline = False, y_inline = False)
	ax.set_title(f"Concentração de CO2 (GEOS-FP v-5.16): {dia}")
	#plt.savefig(f'co2_map_{date}.png', dpi=300)
	plt.show()
	plt.close(fig)

##### MENSAIS 

fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(12, 8), frameon = False,
						subplot_kw={"projection" : ccrs.PlateCarree()})
axes = axes.flatten()
meses = ["2021-02", "2021-05", "2021-07", "2021-10"]
for i, mes in enumerate(meses):
#dia = np.array("2021-02-18", dtype = "datetime64")
	co2 = floripa["CO2"].sel(time = mes, method = "nearest").mean(dim = "lev")
	co2 = co2 * 1000000
	im = co2.plot.pcolormesh(ax = axes[i], transform = ccrs.PlateCarree(),
					cmap = "coolwarm", add_colorbar = False, x = "lon", y = "lat",
					cbar_kwargs={"label" : "CO2 (ppm)"}) # "viridis_r" copper_r coolwarm magma inferno_r
	axes[i].coastlines()
	axes[i].gridlines(draw_labels = True, dms = True, linestyle = ":",
						x_inline = False, y_inline = False)
	axes[i].set_title(f"Concentração de CO2 (GEOS-FP v-5.16): {mes}")
fig.colorbar(im, ax = axes, orientation = "vertical",
			fraction = 0.03, pad = 0.1, label = "CO2 (ppm)")
plt.tight_layout(rect = [0, 0, 0.95, 1])
plt.suptitle("Concentração de CO2 (GEOS-FP v-5.16)", fontsize = 16, y = 1.02)
#plt.savefig('co2_maps.png')
plt.show()
plt.close(fig)

#sys.exit()

for i, mes in enumerate(meses):
	fig, ax = plt.subplots(figsize=(10, 8), frameon = False,
							subplot_kw={"projection": ccrs.PlateCarree()})
	co2 = floripa["CO2"].sel(time = dia, method = "nearest").mean(dim = ["time", "lev"])
	co2 = co2 * 1000000
	co2.plot.pcolormesh(ax = ax, transform = ccrs.PlateCarree(),
						cmap = "coolwarm", cbar_kwargs={"label" : "CO2 (ppm)",
														"shrink" : 0.7,
														"pad" : 0.1})
	ax.coastlines()
	ax.gridlines(draw_labels = True, dms = True, linestyle = ":",
					x_inline = False, y_inline = False)
	ax.set_title(f"Concentração de CO2 (GEOS-FP v-5.16): {mes}")
	#plt.savefig(f'co2_map_{date}.png', dpi=300)
	plt.show()
	plt.close(fig)




sys.exit()
data = "2021-02-18"
data = np.array(data, dtype = "datetime64")
plt.figure(figsize = (12, 6), frameon = False)#, layout = "tight")
ax = plt.axes(projection = ccrs.PlateCarree())
shp = list(shpreader.Reader("/home/sifapsc/scripts/matheus/dados_dengue/shapefiles/BR_UF_2022.shp").geometries())
ax.add_geometries(shp, ccrs.PlateCarree(), edgecolor = "gray", facecolor = "none", linewidth = 0.3)
ax.coastlines(resolution = "10m", color = "black", linewidth = 0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor = "black", linewidth = 0.5)
#plt.show()
#sys.exit()
regiao = floripa["CO2"].sel(time = f"{data}").squeeze()
print(f"\n{green}REGIÃO:\n{reset}{regiao}\n")
#sys.exit()

maxi = regiao.max().item()
int_max = int(maxi) + 10
mini = regiao.min().item()
int_min = int(mini) - 10
print(f"Valor máximo da variável na região selecionada: {int_max}")
colors = ["#b4f0f0", "#96d2fa", "#78b9fa", "#3c95f5", "#1e6deb", "#1463d2", 
	      "#0fa00f", "#28be28", "#50f050", "#72f06e", "#b3faaa", "#fff9aa", 
	      "#ffe978", "#ffc13c", "#ffa200", "#ff6200", "#ff3300", "#ff1500", 
	      "#c00100", "#a50200", "#870000", "#653b32"]
cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#000000')
cmap.set_under('#ffffff')
data_min = int_min # 0
data_max = int_max
interval = 1
levels = np.arange(data_min, data_max + interval, interval)
"""
mesh = ax.pcolormesh(floripa["CO2"], robust = True)
plt.colorbar(mesh)

figure = floripa.plot.pcolormesh(robust = True,
								norm = cls.Normalize(vmin = 0, vmax = int_max),
								cmap = cmap, add_colorbar = False,
								levels = levels, add_labels = False)

figure = floripa["CO2"].plot(robust = True, add_colorbar = False,
								levels = levels, add_labels = False)
"""
figure = regiao.plot.pcolormesh(robust = True,
								norm = cls.Normalize(vmin = 0, vmax = int_max),
								cmap = cmap, add_colorbar = False,
								levels = levels, add_labels = False)
plt.colorbar(figure, pad = 0.05, fraction = 5, extend = "max", ticks = np.arange(int_min, int_max, 50),
				orientation = "vertical", label = "CO2 (GEOS-FP)")


gl = ax.gridlines(crs = ccrs.PlateCarree(), color = "white", alpha = 1.0, linestyle = "--",
					linewidth = 0.25, xlocs = np.arange(-180, 180, 5),
					ylocs = np.arange(-90, 90, 5), draw_labels = True)
gl.top_labels = False
gl.right_labels = False
plt.title(f"Concentração de CO2 (GEOS-FP)\nPeríodo observado: {data}", fontsize = 14, ha = "center")
plt.figtext(0.55, 0.05, "Fonte: NASA Center for Climate Simulation", ha = "center", fontsize = 10)
#plt.savefig(f"/media/produtos/merge/monthly/2024/prec_mensal_merge_{ano}{mes}.jpg",
#			transparent = True, dpi = 300, bbox_inches = "tight", pad_inches = 0.02)

plt.show()

'''
sys.exit()

####
#ds = xr.open_dataset('/media/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMED_MEAN_2024.nc')
ds1 = xr.open_dataset(f"{path_sam}/TMIN/{ano}/{file_name1}")
ds2 = xr.open_dataset(f"{path_sam}/TMED/{ano}/{file_name2}")
ds3 = xr.open_dataset(f"{path_sam}/TMAX/{ano}/{file_name3}")

print('Arquivo original\nTMIN:\n{ds1}\n')
print('***************************************\n')
# VISUALIZAR dimensões do aquivo (Latitude, Longitude e Time)
print('Coordenadas em Latitude:', ds1.lat, '\n')
print('***************************************\n')
print('Coordenadas em Longitude:', ds1.lon, '\n')
print('***************************************\n')
print('Datas:', ds1.time, '\n')
print('***************************************\n')
# Variável de interesse
print('Data variable:', ds1.tmin, '\n')
print('***************************************\n')

print('Arquivo original\nTMED:\n{ds2}\n')
print('***************************************\n')
# VISUALIZAR dimensões do aquivo (Latitude, Longitude e Time)
print('Coordenadas em Latitude:', ds2.lat, '\n')
print('***************************************\n')
print('Coordenadas em Longitude:', ds2.lon, '\n')
print('***************************************\n')
print('Datas:', ds2.time, '\n')
print('***************************************\n')
# Variável de interesse
print('Data variable:', ds2.tmed, '\n')
print('***************************************\n')

print('Arquivo original\nTMAX:\n{ds3}\n')
print('***************************************\n')
# VISUALIZAR dimensões do aquivo (Latitude, Longitude e Time)
print('Coordenadas em Latitude:', ds3.lat, '\n')
print('***************************************\n')
print('Coordenadas em Longitude:', ds3.lon, '\n')
print('***************************************\n')
print('Datas:', ds3.time, '\n')
print('***************************************\n')
# Variável de interesse
print('Data variable:', ds3.tmax, '\n')
print('***************************************\n')

# Definir a extensão da região que você deseja plotar
lat_min = -34.00
lat_max = -21.75
lon_min = -58.25
lon_max = -47.50
# Definir data (ano-mês)
#data = "2024-06"
data = sys.argv[1] #data = "2024-06"

# Selecionar os dados de temperatura para a região e o dia específico
data_region1 = ds1.sel(time = f'{data}', lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).tmin.squeeze()
data_region2 = ds2.sel(time = f'{data}', lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).tmed.squeeze()
data_region3 = ds3.sel(time = f'{data}', lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).tmax.squeeze()

# Encontrar o valor máximo da temperatura máxima e mínimo da temperatura mínima na região selecionada
max_tmax = data_region3.max().item()
int_max = int(max_tmax)
min_tmin = data_region1.min().item()
int_min = int(min_tmin)
print(f'Valor máximo da temperatura na região selecionada: {round(max_tmax, 2)} °C')
print(f'Valor mínimo da temperatura na região selecionada: {round(min_tmin, 2)} °C')
# Plotar temperatura de um dia específico

def gerar_mapa(str_var):
	"""
	Função relativa à síntese de mapas temáticos de temperatura utilizando SAMeT.
	entrada:
	- arquivo = data_region1, data_region2 ou data_region3;
	- str_var = string da variável de interesse (tmin, tmed ou tmax).
	retorno:
	- mapa temático com a variável de interesse.
	"""
	plt.figure(figsize=(8, 6))#, layout = "tight", frameon = False)
	ax = plt.axes(projection=ccrs.PlateCarree())
	shp = list(shpreader.Reader(f"{path_shp}/BR_UF_2019.shp").geometries())
	# Criar uma paleta de cores personalizada
	colors = ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#fee090", 
		  "#fdae61", "#f46d43", "#d73027", "#a50026"]
	cmap = matplotlib.colors.ListedColormap(colors)
	cmap.set_over('#800026')
	cmap.set_under('#040273')#07101C')
	# Definir o intervalo de contorno
	data_min = int_min
	data_max = int_max
	interval = 1
	levels = np.linspace(data_min, data_max, num=256)
	#levels = np.arange(data_min, data_max, (int_max-int_min)/10)
	# Plotar o dado 2D da região selecionada
	match str_var:
		case "tmin":
			figure = data_region1.plot.pcolormesh(robust=True, norm=cls.Normalize(vmin=int_min, vmax=int_max),
				                         cmap=cmap, add_colorbar=False, levels=levels, add_labels=False)
		case "tmed":
			figure = data_region2.plot.pcolormesh(robust=True, norm=cls.Normalize(vmin=int_min, vmax=int_max),
				                         cmap=cmap, add_colorbar=False, levels=levels, add_labels=False)
		case "tmax":
			figure = data_region3.plot.pcolormesh(robust=True, norm=cls.Normalize(vmin=int_min, vmax=int_max),
				                         cmap=cmap, add_colorbar=False, levels=levels, add_labels=False)
		case _:
			print(f"\nVariável não encontrada!\n{str_var}\nVariável não encontrada!\n")
	ax.add_geometries(shp, ccrs.PlateCarree(), edgecolor='gray', facecolor='none', linewidth=0.3)
	ax.coastlines(resolution='10m', color='black', linewidth=0.8)
	ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
	gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--',
			linewidth=0.25, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
	gl.top_labels = False
	gl.right_labels = False
	plt.colorbar(figure, pad=0.05, fraction=0.05, extend='both', label='Temperatura Mensal (°C)',
		ticks=np.arange(int_min, int_max+1, (int_max-int_min)/10), orientation='vertical')
	match str_var:
		case "tmin":
			plt.title(f'Temperatura Mínima Mensal (°C)\nSul do Brasil, Período observado: {mes}/{ano}', fontsize=14, ha='center')
		case "tmed":
			plt.title(f'Temperatura Média Mensal (°C)\nSul do Brasil, Período observado: {mes}/{ano}', fontsize=14, ha='center')
		case "tmax":
			plt.title(f'Temperatura Máxima Mensal (°C)\nSul do Brasil, Período observado: {mes}/{ano}', fontsize=14, ha='center')
		case _:
			print(f"\nVariável não encontrada!\n{str_var}\nVariável não encontrada!\n")
	# Adicionar a fonte no rodapé
	plt.figtext(0.55, 0.05, 'Fonte: SAMeT - CPTEC', ha='center', fontsize=10)
	# Salvar a figura no formato ".jpg" com dpi=300.
	plt.savefig(f"{path_pro}/{ano}/{str_var}_mensal_samet_{ano}{mes}.png", transparent=True, dpi=300, bbox_inches="tight", pad_inches=0.02)
	print(f'\nFigura gerada:\n{path_pro}/{ano}/{str_var}_mensal_samet_{ano}{mes}.png\n')
	plt.show()

gerar_mapa("tmin")
gerar_mapa("tmed")
gerar_mapa("tmax")
'''
