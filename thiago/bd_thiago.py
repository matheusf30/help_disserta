#############################################################
## Roteiro para estruturar e interpolar banco de dados     ##
## Demanda: Thiago Pereira Alves                           ##
## Autor: Matheus Ferreira de Souza                        ##
## Data: 24/06/2025                                        ##
#############################################################

##### Padrão ANSI ###########################################
bold = "\033[1m"
red = "\033[91m"
green = "\033[92m"
yellow = "\033[33m"
blue = "\033[34m"
magenta = "\033[35m"
cyan = "\033[36m"
white = "\033[37m"
reset = "\033[0m"
############################################################

### Importando Bibliotecas
import pandas as pd
import math

### Encaminhamento aos Diretórios
caminho_dados = "/home/sifapsc/scripts/matheus/help_disserta/thiago/"
print(f"\nOS DADOS UTILIZADOS ESTÃO ALOCADOS NOS SEGUINTES CAMINHOS:\n\n{caminho_dados}\n\n")
### Renomeação variáveis pelos arquivos
#dados = "HAB_SC_1997_2024_TSM_SAL.xlsx"
dados = "HAB_SC_1997_2024_TSM_SAL.csv"

### Abrindo Arquivo
#dados = pd.read_excel(f"{caminho_dados}{dados}")
dados = pd.read_csv(f"{caminho_dados}{dados}")
print(f"\n{green}Dados do Thiago\n{reset}{dados}")

### Pré-processamento
colunas = dados.columns
colunas_troca = dados[["PONTO", "MD_LAT_GD", "MD_LON_GD", "Tag", "SAL"]]
colunas_num = dados[["MD_LAT_GD", "MD_LON_GD", "Tag", "SAL"]]
print(f"\n{green}Colunas\n{reset}{colunas}")
for coluna in colunas_troca:
	dados[coluna] = dados[coluna].str.replace(",", ".")#.astype(float)
	dados[coluna] = dados[coluna].str.strip()
dados["DATA"] = pd.to_datetime(dados["DATA"])
for numeral in colunas_num:
	dados[numeral] = pd.to_numeric(dados[numeral])
dados["latlon"] = list(zip(dados["MD_LAT_GD"], dados["MD_LON_GD"]))
print(f"\n{green}Pré-processamento dos Dados\n{reset}{dados}")
print(f"\n{green}Pré-processamento dos Dados\n{reset}{dados.info()}")
dict_ponto = dict(zip(dados["PONTO"], dados["latlon"]))
dict_ponto_nonan = {k:v for k, v in dict_ponto.items() if not (math.isnan(float(v[0])) or math.isnan(float(v[1])))}
#dict_ponto = dict_ponto is not None
print(f"\n{green}Dicionário de Pontos {red}(com NaN)\n{reset}{dict_ponto}")
print(f"\n{green}Dicionário de Pontos\n{reset}{dict_ponto_nonan}")

Iansã representa chuvas tempestiva em religiões de matriz africana. Considerando também que Florianópolis apresenta religião de matriz africana em alto adensamento. Principalmente no bairro de José Mendes, próximo ao Ifsc.
