#!/bin/bash
###################################################
## Arquivo adaptado para baixar dados do         ##
## NASA Center for Climate Simulation            ##
## High Performance Computing for Science        ##
## Dados: AIRDENS, CO, CO2, DELP, PS, TAITIME    ##
## Adaptado por: Matheus Ferreira de Souza       ##
##               e Everton Weber Galliani        ##
## Data: 10/06/2025                              ##
###################################################

# Configuração de cores para saída no terminal
bold="\033[1m"
red="\033[91m"
green="\033[92m"
yellow="\033[33m"
blue="\033[34m"
magenta="\033[35m"
cyan="\033[36m"
white="\033[37m"
reset="\033[0m"

# Obtendo o ano, mês e dia atual
ANO=$(date +%Y)
MES=$(date +%m)
HOJE=$(date +%d)
ONTEM=$(date -d "yesterday" +%d)
ANTEONTEM=$(date -d "2 days ago" +%d)

ANO_ONTEM=$(date -d "yesterday" +%Y)
ANO_ANTEONTEM=$(date -d "2 days ago" +%Y)
MES_ONTEM=$(date -d "yesterday" +%m)
MES_ANTEONTEM=$(date -d "2 days ago" +%m)

ZULUS=(00 03 06 09 12 15 18 21)

echo -e "\n${green}ANO: ${reset}$ANO"
echo -e "${green}MÊS: ${reset}$MES"
echo -e "${green}DIA ATUAL: ${reset}$HOJE"
echo -e "${green}HORAS: ${reset}${ZULUS[@]}"

# Função para download de arquivos CO2
download_co2() {
    local ANO=$1
    local MES=$2
    local DIA=$3
    local ZULU=$4

    echo -e "\n${green}ANO: ${reset}$ANO"
    echo -e "${green}MÊS: ${reset}$MES"
    echo -e "${green}DIA: ${reset}$DIA"
    echo -e "${green}HORA: ${reset}$ZULU"

    # URL do NCCS e filtro cronológico
    URL_NASA="https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/das/"
    FILTRO_CRONO="Y$ANO/M$MES/D$DIA/"
    ARQUIVO="GEOS.fp.asm.inst3_3d_chm_Nv.${ANO}${MES}${DIA}_${ZULU}00.V01.nc4"
    URL_NCCS="${URL_NASA}${FILTRO_CRONO}${ARQUIVO}"

    CAMINHO_DADOS="/home/meteoro/DADOS/dados/operacao/geos_fp/$ANO/$MES/$DIA/"
    NOME_ARQUIVO="geos.chm.${ANO}${MES}${DIA}${ZULU}.nc4"
    CAMINHO_ARQUIVO="${CAMINHO_DADOS}${NOME_ARQUIVO}"
    CAMINHO_ARQUIVO_AS="${CAMINHO_DADOS}AS_geos.chm.${ANO}${MES}${DIA}${ZULU}.nc4"

    if [[ -e "$CAMINHO_ARQUIVO_AS" ]]; then
        TAMANHO_RECORTADO=$(stat --format=%s "$CAMINHO_ARQUIVO_AS")
        TAMANHO_RECORTADO_MB=$((TAMANHO_RECORTADO / 1000000))
        echo -e "\n${cyan}Tamanho do Arquivo: ${reset}${TAMANHO_RECORTADO_MB}MB"

        if [[ $TAMANHO_RECORTADO_MB -eq 67 ]]; then
            echo -e "${cyan}Arquivo existente: ${reset}$CAMINHO_ARQUIVO_AS"
            return
        else
            echo -e "${red}Arquivo incompleto, reiniciando download.${reset}"
            wget -O "$CAMINHO_ARQUIVO" "$URL_NCCS"
        fi
    else
        echo -e "${red}Arquivo nunca baixado, iniciando download.${reset}"
        mkdir -p "$CAMINHO_DADOS"
        wget -O "$CAMINHO_ARQUIVO" "$URL_NCCS"
    fi
}

# Função para realizar o corte da América do Sul usando cdo
cdo_sel_AS() {
    local ANO=$1
    local MES=$2
    local DIA=$3
    local ZULU=$4

    CAMINHO_DADOS="/dados3/operacao/geos_fp/$ANO/$MES/$DIA/"
    NOME_ARQUIVO="geos.chm.${ANO}${MES}${DIA}${ZULU}.nc4"
    CAMINHO_ARQUIVO="${CAMINHO_DADOS}${NOME_ARQUIVO}"
    CAMINHO_ARQUIVO_AS="${CAMINHO_DADOS}AS_geos.chm.${ANO}${MES}${DIA}${ZULU}.nc4"
    LAT_MAX=15
    LAT_MIN=-60
    LON_MAX=-30
    LON_MIN=-90

    cdo sellonlatbox,$LON_MIN,$LON_MAX,$LAT_MIN,$LAT_MAX "$CAMINHO_ARQUIVO" "$CAMINHO_ARQUIVO_AS"
    if [[ $? -eq 0 ]]; then
        echo -e "${green}Seleção realizada com sucesso para a América do Sul: ${reset}$CAMINHO_ARQUIVO_AS"
        rm -f "$CAMINHO_ARQUIVO"
        echo -e "${red}Remoção do arquivo original: ${reset}$CAMINHO_ARQUIVO"
    else
        echo -e "${red}Não foi possível realizar a seleção de área.${reset}"
    fi
}

# Automatizando o download e processamento para os últimos 3 dias e diferentes horas
for ZULU in "${ZULUS[@]}"; do
    # Hoje
    download_co2 "$ANO" "$MES" "$HOJE" "$ZULU"
    cdo_sel_AS "$ANO" "$MES" "$HOJE" "$ZULU"
    
    # Ontem
    download_co2 "$ANO_ONTEM" "$MES_ONTEM" "$ONTEM" "$ZULU"
    cdo_sel_AS "$ANO_ONTEM" "$MES_ONTEM" "$ONTEM" "$ZULU"
    
    # Anteontem
    download_co2 "$ANO_ANTEONTEM" "$MES_ANTEONTEM" "$ANTEONTEM" "$ZULU"
    cdo_sel_AS "$ANO_ANTEONTEM" "$MES_ANTEONTEM" "$ANTEONTEM" "$ZULU"
done
