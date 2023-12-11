# command to run this script: bash use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/varyMsgRate.sh

#!/bin/bash

#take comma seprated link bandwidth inputs
read -p "Enter link bandwidth values separated by commas: " linkBwInput
linkBwInputArray=(${linkBwInput//,/ })

#take comma seprated message-rate inputs
read -p "Enter message-rate values separated by commas: " input
array=(${input//,/ })

# loop over each link-bandwidth and run the simulation
for linkBwValue in "${linkBwInputArray[@]}";do
    # loop over each message-rate and run the simulation
    for value in "${array[@]}";do
        echo "Start simulation for scenario: $linkBwValue Mbps, $value msg/s"
        # update link delay in input.graphml file
        python3 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/inputProcessing.py --link-bw $linkBwValue --msg-rate $value
        # run the simulation
        sudo python3 main.py use-cases/varying-networking-conditions/varying-link-bw/military-coordination/input.graphml --time 10
        # plot the results
        sudo python3 plot-scripts/bandwidthPlotScript.py --number-of-switches 10 --switch-ports S1-P1,S1-P2,S1-P3,S1-P4,S1-P5,S1-P6,S1-P7,S1-P8,S1-P9,S1-P10 --port-type access-port --message-rate $value --ntopics 2 --replication 10 --log-dir logs/output
        # create logs directory and copy the results    
        sudo mkdir -p use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/$linkBwValue"Mbps"/scenario-$value"msgPs" 
        sudo chmod -R 777 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/$linkBwValue"Mbps"/scenario-$value"msgPs"
        cp -r logs/output/* use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/$linkBwValue"Mbps"/scenario-$value"msgPs"
        echo "Logs created for $value msg/s message-rate"
    done
    echo "varying message-rate with $linkBwValue Mbps link bandwidth experiment done."
done