#############################################################
## Roteiro para estruturar e interpolar banco de dados     ##
## Demanda: Thiago Pereira Alves                           ##
## Autor: Matheus Ferreira de Souza                        ##
## Data: 24/06/2025                                        ##
#############################################################

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

### Importando Bibliotecas
import pandas as pd

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


