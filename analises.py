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
_LOCAL = "IFSC"
caminho_dados = "/home/sifapsc/scripts/matheus/haff/"
print(f"\nOS DADOS UTILIZADOS ESTÃO ALOCADOS NOS SEGUINTES CAMINHOS:\n\n{caminho_dados}\n\n")
### Renomeação variáveis pelos arquivos
dados = "dado_erasmo.csv"
### Abrindo Arquivo
haff = pd.read_csv(f"{caminho_dados}{dados}", low_memory = False)

### Pré-processamento
haff = haff.rename(columns = {"Intervalo":"data", "prec_MN_82331":"prec_MN", "perc_ ITA_82336":"prec_ITA",
							"rad_MN_331":"rad_MN", "rad_ITA_336":"rad_ITA",
							"tsm_331":"tsr_MN", "tsm_336":"tsr_ITA"})
haff["data"] = pd.to_datetime(haff["data"])
haff.set_index("data", inplace = True)
colunas = haff.columns

haff[colunas] = haff[colunas].replace(",",".", regex = True)
haff = haff.apply(pd.to_numeric, errors = "coerce")
print(f"\n{green}Dados Haff:\n{reset}{haff}\n")
print(f"\n{green}Dados Haff (colunas):\n{reset}{colunas}\n")
print(f"\n{green}Dados Haff (básico):\n{reset}{haff.describe()}\n")
print(f"\n{green}Dados Haff (variáveis):\n{reset}{haff.dtypes}\n")

### Análise
# Correlação (selecionar anos)
# Avaliar tendência (MannKandall - tirar sazonalidade)
# Variabilidade

variaveis = haff[colunas]
_METODO = "pearson"
correlacao_variaveis = variaveis.corr(method = f"{_METODO}")
print("="*80)
print(f"Método de {_METODO.title()} \n", correlacao_variaveis)
print("="*80)
fig, ax = plt.subplots(figsize = (10, 6), layout = "constrained", frameon = False)
sns.heatmap(correlacao_variaveis, annot = True, cmap = "tab20c", linewidth = 0.5)
ax.set_yticklabels(ax.get_yticklabels(), rotation = "horizontal")
fig.suptitle(f"MATRIZ DE CORRELAÇÃO* entre \n [...] \n *(Método de {_METODO.title()}; [...]", weight = "bold", size = "medium")
#plt.savefig(f'{caminho_correlacao}correlacao_casos_{__CIDADE}_.pdf', format = "pdf", dpi = 1200,  bbox_inches = "tight", pad_inches = 0.0)
plt.show()

haff[["haff","prec_MN","rad_MN"]].plot()
plt.show()

