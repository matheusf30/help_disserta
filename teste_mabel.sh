#!/bin/bash
#
#################################################################
#                                                               #
#   Script Automático para recuperar os dados do modelo         #
#   GEOS-FP do NCCS com observações a cada 03 horas             #
#                                                               #
#   no link: https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/das/
#                                                               #
#                                                               #
#    Autor: Mario Quadro - CTMEt/IFSC    Data: 21/02/2019       #
#        Matheus Ferreira de Souza - IFSC  Data: 16/05/2025     #
#################################################################
#
export LC_NUMERIC=en_US.UTF-8     ;# Comando para executar operacoes decimais
#
########################################################
# Definir os caminhos (paths) do scrips                #
########################################################
path_cro=$HOME/cron
path_dat=/media/dados/pesquisa/data_co2 ;# Path CLuster
path_bin=/usr/bin ;# Path CLuster
path_gra=/usr/share/opengrads/Contents  ;# Path Cluster
#
#path_dat=/Users/mquadro/data/data_gfs ;# Path Laptop Mario
#path_bin=/usr/local/bin ;# Path Laptop Mario
#path_gra=/Applications/OpenGrADS  ;# Path Laptop Mario
#
#
mkdir -p $path_dat
#
#
######################################################################
###		     SETANDO DADOS DE ENTRADA			   ###
######################################################################
#
if [ $1 ];then
   dati=$1
else
   echo "Syntax error: ./recupera_gfs.sh <data inicial>"
   echo "Exemplo     : ./recupera_gfs.sh AAAAMMDD"
   exit
fi
#
dati=$1

if [ $2 ];then
   datf=$2
else
   echo "Syntax error: ./recupera_gfs.sh <data inicial> <data finale>"
   echo "Exemplo     : ./recupera_gfs.sh AAAAMMDDHH AAAAMMDD"
   exit
fi
#
cd $path_dat
#
#
######################################################################
###		         LENDO A DATA INICIAL          		   ###
######################################################################
#
ai=`echo $dati | awk '{ print substr($1,1,4)}'`
mi=`echo $dati | awk '{ print substr($1,5,2)}'`
di=`echo $dati | awk '{ print substr($1,7,2)}'`
hi=0
#
af=`echo $datf | awk '{ print substr($1,1,4)}'`
mf=`echo $datf | awk '{ print substr($1,5,2)}'`
df=`echo $datf | awk '{ print substr($1,7,2)}'`
hf=21
#
echo "Data Inicial -> "$ai $mi $di $hi
echo "Data Final   -> "$af $mf $df $hf
#
#si=`date -j -v +0H -f "%Y%m%d%H" "$ai$mi$di$hi" +%s`;# Comando para Definir o Tempo i Mac
#sf=`date -j -v +0H -f "%Y%m%d%H" "$af$mf$df$hf" +%s`;# Comando para Definir o Tempo i Mac
#
si=`date -u --date="$ai$mi$di $hi" +%s`;# Comando para Definir o Tempo i Linux
sf=`date -u --date="$af$mf$df $hf" +%s`;# Comando para Definir o Tempo f linux
#
echo $si
echo $sf
#
cont_horas=`echo "scale=0; ($sf - $si)/(3600*3)" | bc -l` ;# Define o intervalo em horas
#
echo "Numero de horas -> "$cont_horas

#exit
#
#
#
########################################################
# Faz o Loop para baixar as imagens                    #
########################################################
for (( i = 0; i <= $cont_horas; i++ ))
do
 j=$((i*3))
 echo "Tempo -> "$i $j
     
 #data=`date -j -v +${j}H -f "%Y%m%d%H" "$ai$mi$di$hi" +%Y%m%d%H`'00';# mac
 data=`date -u --date="$ai$mi$di $hi + $j hours" +%Y%m%d%H`;# linux

 #
 ano=`echo $data | awk '{print substr($1,1,4)}'`
 mes=`echo $data | awk '{print substr($1,5,2)}'`
 dia=`echo $data | awk '{print substr($1,7,2)}'`
 hor=`echo $data | awk '{print substr($1,9,2)}'`

 echo "Data -> "$data $ano $mes $dia $hor $i 
 #
 # Pega os dados 1p00 e 0p50
 #
 rm -f GEOS.fp.asm.inst3_3d_chm_Nv.${ano}${mes}${dia}_${hor}00.V01.nc4
 wget https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/das/Y${ano}/M${mes}/D${dia}/GEOS.fp.asm.inst3_3d_chm_Nv.${ano}${mes}${dia}_${hor}00.V01.nc4
 cdo ..
 #exit
 ls $path_dat

#   ln -s gfsanl_${k}_${ano}${mes}${dia}_${hor}00_000.grb2 gfs.t00z.pgrb2.${res}.f000
   #
 exit
#
done
#

exit
