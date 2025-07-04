### Importando Bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
import numpy as np
import pymannkendall as mk
from scipy.stats import shapiro, normaltest
import statsmodels.api as sm
import unicodedata
import sys

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

### Encaminhamento aos Diretórios
caminho_dados = "/home/sifapsc/scripts/matheus/help_disserta/erasmo/"
caminho_correlacao = "/home/sifapsc/scripts/matheus/help_disserta/erasmo/"
print(f"\nOS DADOS UTILIZADOS ESTÃO ALOCADOS NOS SEGUINTES CAMINHOS:\n\n{caminho_dados}\n\n")
### Renomeação variáveis pelos arquivos
dados = "dados_erasmo.csv"
enos = "https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/detrend.nino34.ascii.txt"

### Abrindo Arquivo
haff = pd.read_csv(f"{caminho_dados}{dados}", low_memory = False)
enos = pd.read_csv(f"{enos}", delim_whitespace = True)

### Pré-processamento
haff = haff.rename(columns = {"Intervalo":"data", "prec_MN_82331":"prec_MN", "perc_ ITA_82336":"prec_ITA",
							"rad_MN_331":"rad_MN", "rad_ITA_336":"rad_ITA",
							"tsm_331":"tsm_MN", "tsm_336":"tsm_ITA"})
haff["data"] = pd.to_datetime(haff["data"])
haff = haff[["data", 'haff', 'prec_MN', 'prec_ITA', 'rad_MN', 'rad_ITA']]#, 'EL', 'LA']]
			#'tsm_MN', 'tsm_ITA', 'EL', 'LA']]
colunas = haff.columns
haff[colunas] = haff[colunas].replace(",",".", regex = True)
haff = haff.apply(pd.to_numeric, errors = "coerce")
print(enos.columns)
enos["data"] = pd.to_datetime(enos["YR"].astype(str) + enos["MON"].astype(str).str.zfill(2),
								format = "%Y%m", errors = "coerce")
haff["data"] = pd.to_datetime(haff["data"])
enos = enos[["data", "ANOM"]]
haff = haff.merge(enos, on = "data", how = "inner")
haff.set_index("data", inplace = True)
haff = haff.rename(columns = {"ANOM":"ENOS"})
colunas = haff.columns
haff.reset_index(inplace = True)
print(f"\n{green}Dados Haff:\n{reset}{haff}\n")
print(f"\n{green}Dados Haff (colunas):\n{reset}{colunas}\n")
print(f"\n{green}Dados Haff (básico):\n{reset}{haff.describe()}\n")
print(f"\n{green}Dados Haff (variáveis):\n{reset}{haff.dtypes}\n")
print(f"\n{green}Dados ENOS:\n{reset}{enos}\n")
#sys.exit()
# Avaliar tendência (MannKandall - tirar sazonalidade)
haff["mes"] = haff["data"].dt.month
media_mes = haff.groupby("mes")[colunas].mean().round(2)
media_mes.reset_index(inplace = True)
print(f"\n{green}media_mes\n{reset}{media_mes}\n{green}media_mes.index\n{reset}{media_mes.index}")
componente_sazonal = haff.merge(media_mes, left_on = "mes", how = "left", suffixes = ("", "_media"), right_index = True)
sem_sazonal = pd.DataFrame(index = haff.index)
meses  = componente_sazonal["mes"]
componente_sazonal.drop(columns = "mes", inplace = True)
print(f"{green}componente_sazonal\n{reset}{componente_sazonal}")
for coluna in colunas:
	if coluna in componente_sazonal.columns:
		media_coluna = f"{coluna}_media"
		if media_coluna in componente_sazonal.columns:
			sem_sazonal[coluna] = haff[coluna] - componente_sazonal[media_coluna]
		else:
			print(f"{red}Coluna {media_coluna} não encontrada no componente sazonal!{reset}")
	else:
		print(f"{red}Coluna {coluna} não encontrada no csv!{reset}")

sem_sazonal["mes"] = meses
#sem_sazonal.dropna(inplace = True)
sem_sazonal.drop(columns = "mes", inplace = True)
print(f"\n{green}sem_sazonal\n{reset}{sem_sazonal}\n")
print(f"\n{green}sem_sazonal.columns\n{reset}{sem_sazonal.columns}\n")
for c in colunas:
	tendencia = mk.original_test(sem_sazonal[c])
	if tendencia.trend == "decreasing":
		print(f"\n{red}{c}\n{tendencia.trend}{reset}\n")
	if tendencia.trend == "no trend":
		print(f"\n{cyan}{c}\n{tendencia.trend}{reset}\n")
	elif tendencia.trend == "increasing":
		print(f"\n{green}{c}\n{tendencia.trend}{reset}\n")

#sys.exit()
haff.drop(columns = "mes", inplace = True)
haff["EL"] = haff["ENOS"].where(haff["ENOS"] >= 0.5)
haff["LA"] = haff["ENOS"].where(haff["ENOS"] <= -0.5)
haff.set_index("data", inplace = True)
print(f"\n{green}Dados Haff:\n{reset}{haff}\n")
#sys.exit()

# Variabilidade
##### Correlação
### Análise (série Temporal Mensal)
colunas = haff.columns
variaveis = haff[colunas]
_METODOS = ["pearson", "spearman"]
for _METODO in _METODOS:
	correlacao_variaveis = variaveis.corr(method = f"{_METODO}")
	print("="*80)
	print(f"Método de {_METODO.title()} \n", correlacao_variaveis)
	print("="*80)
	fig, ax = plt.subplots(figsize = (10, 6), layout = "constrained", frameon = False)
	filtro = np.triu(np.ones_like(correlacao_variaveis, dtype = bool), k = 1)
	sns.heatmap(correlacao_variaveis, annot = True, cmap = "Spectral", linewidth = 0.5,
				vmin = -1, vmax = 1, mask = filtro)
	ax.set_yticklabels(ax.get_yticklabels(), rotation = "horizontal")
	fig.suptitle(f"MATRIZ DE CORRELAÇÃO* entre OCORRẼNCIA DE HAFF, PRECIPITAÇÃO, RADIAÇÃO, TSM, ElNiño/LaNiña.\nMUNICÍPIOS DE MANAUS/AM e ITACOATIARA/AM\n*(Método de {_METODO.title()}; Série Temporal; Médias Mensais).", weight = "bold", size = "medium")
	plt.savefig(f"{caminho_correlacao}correlacao_haff_{_METODO}_serie_mensal.pdf",
					format = "pdf", dpi = 300,  bbox_inches = "tight", pad_inches = 0.0)
	plt.show()

### Análise (série Após 2021 Mensal)
haff_pos21 = haff[haff.index.year >= 2021]
variaveis = haff_pos21[colunas]
print(f"\n{green}Dados Haff (>2021; mensal):\n{reset}{haff_pos21}\n")
for _METODO in _METODOS:
	correlacao_variaveis = variaveis.corr(method = f"{_METODO}")
	print("="*80)
	print(f"Método de {_METODO.title()} \n", correlacao_variaveis)
	print("="*80)
	fig, ax = plt.subplots(figsize = (10, 6), layout = "constrained", frameon = False)
	filtro = np.triu(np.ones_like(correlacao_variaveis, dtype = bool), k = 1)
	sns.heatmap(correlacao_variaveis, annot = True, cmap = "Spectral", linewidth = 0.5,
				vmin = -1, vmax = 1, mask = filtro)
	ax.set_yticklabels(ax.get_yticklabels(), rotation = "horizontal")
	fig.suptitle(f"MATRIZ DE CORRELAÇÃO* entre OCORRẼNCIA DE HAFF, PRECIPITAÇÃO, RADIAÇÃO, TSM, ElNiño/LaNiña.\nMUNICÍPIOS DE MANAUS/AM e ITACOATIARA/AM\n*(Método de {_METODO.title()}; Série Após 2021; Médias Mensais).", weight = "bold", size = "medium")
	plt.savefig(f"{caminho_correlacao}correlacao_haff_{_METODO}_apos21_mensal.pdf",
					format = "pdf", dpi = 300,  bbox_inches = "tight", pad_inches = 0.0)
	plt.show()

### Análise (série Após 2021 Anual)
haff_pos21anual = haff_pos21.groupby(haff_pos21.index.year).mean()
variaveis = haff_pos21anual[colunas]
print(f"\n{green}Dados Haff (>2021; anual):\n{reset}{haff_pos21anual}\n")
for _METODO in _METODOS:
	correlacao_variaveis = variaveis.corr(method = f"{_METODO}")
	print("="*80)
	print(f"Método de {_METODO.title()} \n", correlacao_variaveis)
	print("="*80)
	fig, ax = plt.subplots(figsize = (10, 6), layout = "constrained", frameon = False)
	filtro = np.triu(np.ones_like(correlacao_variaveis, dtype = bool), k = 1)
	sns.heatmap(correlacao_variaveis, annot = True, cmap = "Spectral", linewidth = 0.5,
				vmin = -1, vmax = 1, mask = filtro)
	ax.set_yticklabels(ax.get_yticklabels(), rotation = "horizontal")
	fig.suptitle(f"MATRIZ DE CORRELAÇÃO* entre OCORRẼNCIA DE HAFF, PRECIPITAÇÃO, RADIAÇÃO, TSM, ElNiño/LaNiña.\nMUNICÍPIOS DE MANAUS/AM e ITACOATIARA/AM\n*(Método de {_METODO.title()}; Série Após 2021; Médias Anuais).", weight = "bold", size = "medium")
	plt.savefig(f"{caminho_correlacao}correlacao_haff_{_METODO}_apos21_anual.pdf",
					format = "pdf", dpi = 300,  bbox_inches = "tight", pad_inches = 0.0)
	plt.show()

### Análise (série Após 2021 Anual)
haff_pos21anual = haff_pos21.groupby(haff_pos21.index.year).mean()
haff_pos21anual.dropna(inplace = True)
variaveis = haff_pos21anual[colunas]
print(f"\n{green}Dados Haff (>2021; anual sem NaN):\n{reset}{haff_pos21anual}\n")
for _METODO in _METODOS:
	correlacao_variaveis = variaveis.corr(method = f"{_METODO}")
	print("="*80)
	print(f"Método de {_METODO.title()} \n", correlacao_variaveis)
	print("="*80)
	fig, ax = plt.subplots(figsize = (10, 6), layout = "constrained", frameon = False)
	filtro = np.triu(np.ones_like(correlacao_variaveis, dtype = bool), k = 1)
	sns.heatmap(correlacao_variaveis, annot = True, cmap = "Spectral", linewidth = 0.5,
				vmin = -1, vmax = 1, mask = filtro)
	ax.set_yticklabels(ax.get_yticklabels(), rotation = "horizontal")
	fig.suptitle(f"MATRIZ DE CORRELAÇÃO* entre OCORRẼNCIA DE HAFF, PRECIPITAÇÃO, RADIAÇÃO, TSM, ElNiño/LaNiña.\nMUNICÍPIOS DE MANAUS/AM e ITACOATIARA/AM\n*(Método de {_METODO.title()}; Série Após 2021; Médias Anuais (sem NaN)).", weight = "bold", size = "medium")
	plt.savefig(f"{caminho_correlacao}correlacao_haff_{_METODO}_apos21_anual_semnan.pdf",
					format = "pdf", dpi = 300,  bbox_inches = "tight", pad_inches = 0.0)
	plt.show()

haff[["haff","prec_MN","rad_MN"]].plot()
plt.show()

