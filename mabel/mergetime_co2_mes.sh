#!/bin/bash
#####################################################################
## Arquivo adaptado para juntar dados do                           ##
## NASA Center for Climate Simulation                              ##
## High Performance Computing for Science                          ##
## geos_fp >> FP (Forward Processing)                              ##
## Dados: AIRDENS, CO, CO2, DELP, PS, TAITIME                      ##
## Demanda: Mabel Simm Milan Bueno                                 ##
##                                                                 ##
## Como executar:					                               ## 
## ./mergetime_co2.sh <anoi><mesi> <anof><mesf>                    ##
##                                                                 ##
##   		 Autor: Mário Francisco Leal de Quadro - IFSC          ## 
##           Adaptado por: Matheus Ferreira de Souza               ##
##    		 Data: 26/06/2025                                      ##
#####################################################################
#
export LC_NUMERIC=en_US.UTF-8     ;# Comando para executar operacoes decimais
#
#
mt=(' ' 'JAN' 'FEB' 'MAR' 'APR' 'MAY' 'JUN' 'JUL' 'AUG' 'SEP' 'OCT' 'NOV' 'DEC')
mn=(' ' '01'  '02'  '03'  '04'  '05'  '06'  '07'  '08'  '09'  '10'  '11'  '12')
dt=(' ' '31'  '28'  '31'  '30'  '31'  '30'  '31'  '31'  '30'  '31'  '30'  '31')
#
########################################################
# Definir os caminhos (paths) do scrips                #
########################################################
path_cro=$HOME/cron
path_scr=$HOME/scripts/matheus/help_disserta/mabel
path_bin=/usr/bin
path_dat=/dados3/operacao/geos_fp
path_out=/dados4/operacao/geos_fp
path_cli=$path_out/clima
#path_gra=/opt/opengrads
#opengrads=/opt/Contents/opengrads
#
mkdir -p ${path_out}
mkdir -p ${path_cli}
#
########################################################
# Configuração de cores para saída no terminal         #
########################################################
#
bold="\033[1m"
red="\033[91m"
green="\033[92m"
yellow="\033[33m"
blue="\033[34m"
magenta="\033[35m"
cyan="\033[36m"
white="\033[37m"
reset="\033[0m"
#
#########################################################################
#  INICIO DO SCRIPT                                                     #
#  Define dados de Entrada (Reanálise)                                  #
#########################################################################
#
if [ -z $1 ] 
then
# cria variável data inicial do sistema (1o dia do Ano)
  datai=`date --date="0 days ago" +%Y`0101
  #exit
else
  datai=$1
fi
#
if [ -z $2 ] 
then
# cria variável data final do sistema
  dataf=`date --date="0 days ago" +%Y%m%d`
  #exit
else
  dataf=$2
fi
#
#########################################################################
#  Define o Numero de Meses para fazer a estatística                     #
#########################################################################
#
ai=`echo ${datai} | awk '{print substr($1,1,4)}'`
mi=`echo ${datai} | awk '{print substr($1,5,2)}'`
moni=${mt[`echo $mf | awk '{ print $1*1}'`]}
dateini=$moni$ai
#
af=`echo ${dataf} | awk '{print substr($1,1,4)}'`
mf=`echo ${dataf} | awk '{print substr($1,5,2)}'`
monf=${mt[`echo $mf | awk '{ print $1*1}'`]}
datefin=$monf$af
#
# Define o No de Meses do Período de dados
cont_meses=`echo "scale=0; ($af - $ai)*12 + ($mf-$mi+1) " | bc -l`
#
echo "Período, Nº Meses -> " $ai$mi a $af$mf , $cont_meses
#
#exit
#
########################################################
# Loop Monthly data               		       #
########################################################
for (( i = 0; i < $cont_meses; i++ ))
##for (( i = 1; i < 12; i++ ))
do
 data=`date -u --date="${ai}${mi}01 00 + ${i} month" +%Y%m`
 ano=`echo $data | awk '{ print substr($1,1,4)}'`
 mes=`echo $data | awk '{ print substr($1,5,2)}'`
 #mm=`printf "%02d\n" ${i}`
 #di=1
 #df=${dt[`echo ${i} | awk '{ print $1*1}'`]}
 #ls ${path_dat}/${ano}/${mes}/*/AS_geos.chm.*.nc4
 #exit
 echo "------------------------------------------------"
 echo " Ano  , Mes -> " ${ano} , ${mes}
 echo -e "\n${green}Data Início do Processo do AnoMes: ${reset}${ano}${mes}"
 date
 #exit
 mkdir -p ${path_out}/${ano}
 file_out=${path_out}/${ano}/AS_geos.chm.${ano}${mes}.nc4
 retorno=`test -e ${file_out} && echo 1 || echo 0`
 #
 if [ $retorno -eq 1 ]
 then
  echo "==================================================="
  echo "|         Arquivo já existe $data                 |"
  echo "==================================================="
 else
  echo "==================================================="
  echo "| Arquivo não existe $data. Inicia o mergetime     |"
  echo "==================================================="
  sleep .5
  cdo mergetime ${path_dat}/${ano}/${mes}/*/AS_geos.chm.*.nc4 ${file_out}
  echo -e "\n${green}Arquivo Gerado: ${reset}${file_out}" 
 fi
 echo -e "\n${green}Data Final do Processo do AnoMês: ${reset}${ano}${mes}"
 date
 #exit
done

exit



# Obtendo o ano, mês e dia atual
#ANO=$(date +%Y)
#MES=$(date +%m)
#HOJE=$(date +%d)
#ONTEM=$(date -d "yesterday" +%d)
#ANTEONTEM=$(date -d "2 days ago" +%d)

#ANO_ONTEM=$(date -d "yesterday" +%Y)
#ANO_ANTEONTEM=$(date -d "2 days ago" +%Y)
#MES_ONTEM=$(date -d "yesterday" +%m)
#MES_ANTEONTEM=$(date -d "2 days ago" +%m)

#ZULUS=(00 03 06 09 12 15 18 21)

#echo -e "\n${green}ANO: ${reset}$ANO"
#echo -e "${green}MÊS: ${reset}$MES"
#echo -e "${green}DIA ATUAL: ${reset}$HOJE"
#echo -e "${green}HORAS: ${reset}${ZULUS[@]}"

#CAMINHO_DADOS="/dados3/operacao/geos_fp/*/$MES/$DIA/"
#NOME_ARQUIVO="geos.chm.${ANO}${MES}${DIA}${ZULU}.nc4"
#CAMINHO_ARQUIVO="${CAMINHO_DADOS}${NOME_ARQUIVO}"
#CAMINHO_ARQUIVO_AS="${CAMINHO_DADOS}AS_geos.chm.${ANO}${MES}${DIA}${ZULU}.nc4"
