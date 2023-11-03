#!/bin/bash

direction=$1 #backward
station=$2 #releases2
startdate=$3 #20220704
enddate=$4 #20220705

input=gfs_083.2

dates=(); d=$startdate; until [ $d = $enddate ]; do dates+=($d);
	  d=$(date -d "$d + 1 days" +'%Y%m%d'); done
echo "${dates[*]}"

for date in "${dates[@]}"; do 
	python3 /home/muditha/0_Research/FLEXPART/flexpart_10-4_docker/source_files/run_flexpart_simulation.py --station $station --date $date --input $input --direction $direction; done
