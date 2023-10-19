# command to run this script: bash use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/varyMsgRate.sh <link-BW>

#!/bin/bash

#take comma seprated message-rate inputs
read -p "Enter message-rate values separated by commas: " input
array=(${input//,/ })

# loop over each message-rate and run the simulation
for value in "${array[@]}";do
    # echo "$value"
    python3 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/inputProcessing.py --link-bw $1 --msg-rate $value
    sudo python3 main.py use-cases/varying-networking-conditions/varying-link-bw/military-coordination/input.graphml --time 300
    sudo python3 plot-scripts/bandwidthPlotScript.py --number-of-switches 10 --switch-ports S1-P1,S1-P2,S1-P3,S1-P4,S1-P5,S1-P6,S1-P7,S1-P8,S1-P9,S1-P10 --port-type access-port --message-rate $value --ntopics 2 --replication 10 --log-dir logs/output
    cp -r logs/output/* use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/$1"Mbps"/scenario-$value"msgPs"
    echo "Logs created for $value msg/s message-rate"
done
echo "varying message-rate with $1 Mbps link bandwidth experiment done."