import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as cls
#from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader # Import shapefiles
import pandas as pd
import numpy as np
import sys
from sys import exit
import os

#os.system('clear')

#Shapefile
path_shp = "/home/sifapsc/shapefiles/"
shp = list(shpreader.Reader(f"{path_shp}/BR_UF_2024.shp").geometries())
#Abrindo os arquivos netCDF4
path = "/home/sifapsc/scripts/scripts_everton/dados_poluentes/"
path_figuras = "/home/sifapsc/scripts/scripts_everton/figuras_poluentes"
file_coluna = "medias_coluna.nc"
file_levels = "medias_levels.nc"
nc_coluna = xr.open_dataset(f"{path}{file_coluna}")
nc_levels = xr.open_dataset(f"{path}{file_levels}")


#Recortando latitude e longitude
lat_i = -25
lat_f = -30
lon_i = -47.5
lon_f = -54.5
nc_coluna = nc_coluna.sel(lat = slice(lat_i, lat_f), lon = slice(lon_f, lon_i))
nc_levels = nc_levels.sel(lat = slice(lat_i, lat_f), lon = slice(lon_f, lon_i))

#Definindo os ticks de latitude e longitude para plotar nos gráficos
nc_latitude = nc_coluna['lat']
nc_longitude = nc_coluna['lon']
latitude_ticks = np.arange(nc_latitude.min(), nc_latitude.max() + 1.5, 1.5)
longitude_ticks = np.arange(nc_longitude.min(), nc_longitude.max() + 1.5, 1.5)
#Lista com os meses para legenda dos gráficos
meses = ["JANEIRO", 'FEVEREIRO', 'MARCO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'];
#Dicionários de nomes e unidades para inserir nas figuras
mapeamento_variaveis = {
    'pm2p5': "Material Particulado 2.5",
    'pm10': "Material Particulado 10", 
    'tcco': "Monóxido de Carbono (Coluna Total)",
    'tcno2': "Dióxido de Nitrogênio (Coluna Total)",
    'tcso2': "Dióxido de Enxofre (Coluna Total)",
    'co': "Monóxido de Carbono (1000 hPa)",
    'go3': "Ozônio (850 hPa)",
    'so2': "Dióxido de Enxofre (1000 hPa)"
}
mapeamento_unidades = {
    'pm2p5': "kg/m³",
    'pm10': "kg/m³", 
    'tcco': "kg/m²",
    'tcno2': "kg/m²",
    'tcso2': "kg/m²",
    'co': "kg/kg",
    'go3': "kg/kg", 
    'so2': "kg/kg"
}

#Função de geração dos mapas
def gera_mapa_cams(X, Y = None): #X = variável, Y = Nível em hPa
	fig, ax = plt.subplots(4, 3, figsize=(10, 10), subplot_kw = {'projection': ccrs.PlateCarree()});
	nome_completo = mapeamento_variaveis.get(X, f"Variável {X}")
	unidade = mapeamento_unidades.get(X, f"Unidade {X}") 
	fig.suptitle(f'Climatologia de {nome_completo}', fontsize=16)
	fig.supxlabel('Longitude (°)')
	fig.supylabel('Latitude (°)')
	#nc = nc_coluna
	if Y is None:
		nc = nc_coluna
	else:
		nc = nc_levels.sel(lev = Y*100)

	#Valores máximo e mínimo de cada variável para a escala de cores
	minimo = nc[X].min(keep_attrs=False)
	#minimo = 0
	maximo = nc[X].max(keep_attrs=False)
	
	
	norm = cls.Normalize(minimo, maximo)
	levels = np.linspace(minimo, maximo, 20)
	cmap = cls.LinearSegmentedColormap.from_list("", ["darkturquoise", "greenyellow", "yellow", "red"])
	#cmap = plt.get_cmap("RdYlBu_r")
	#cmap = plt.get_cmap("inferno")

	k = 0
	for i in range(0, 4):
		for j in range(0, 3):
			k = k + 1
			mes = f"2024-{str(k).zfill(2)}-01"
			mes = pd.to_datetime(mes, format = '%Y-%m-%d')
			poluente = nc.sel(time = mes)[X]
			imagem = poluente.plot.contourf(ax = ax[i][j], add_colorbar=False, add_labels=False, cmap = cmap, levels = levels, norm = norm, vmin = minimo, vmax = maximo)
			#imagem = poluente.plot.pcolormesh(ax = ax[i][j], add_colorbar=False, add_labels=False, cmap = cmap, norm = norm, vmin = minimo, vmax = maximo)
			ax[i][j].set_title(meses[k-1])
			ax[i][0].set_yticks(latitude_ticks)
			ax[i][0].tick_params(axis='y', labelsize=8)
			ax[-1][j].set_xticks(longitude_ticks)
			ax[-1][j].tick_params(axis='x', labelsize=8)
			ax[i][j].add_feature(cartopy.feature.BORDERS, edgecolor = "black", linewidth = 0.5)
			ax[i][j].add_geometries(shp, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.3)
			ax[i][j].coastlines(resolution = '10m', color = 'black', linewidth = 0.8)
	cbar = fig.colorbar(imagem, ax=ax.ravel().tolist(), orientation='vertical', label= f"{nome_completo} {unidade}", ticks = levels)
	#cbar = fig.colorbar(imagem, ax=ax.ravel().tolist(), orientation='vertical', label= f"{nome_completo} {unidade}")
	# Formatar com 2 algarismos significativos em notação científica
	cbar.formatter = ScalarFormatter(useMathText=True)
	cbar.formatter.set_scientific(True)
	cbar.formatter.set_powerlimits((-2, 2))  # Limites para usar notação científica
	cbar.update_ticks()
	#fig.savefig(f"otimizado_zeros_{nome_completo}.png")
	print(f"Exibindo o mapa de {X}.png")
	plt.show()

gera_mapa_cams('pm2p5')
gera_mapa_cams('pm10')
gera_mapa_cams('tcco')
gera_mapa_cams('tcno2')
gera_mapa_cams('tcso2')
gera_mapa_cams('co', 1000)
gera_mapa_cams('go3', 850)
gera_mapa_cams('so2', 1000)
