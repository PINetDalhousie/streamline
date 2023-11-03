#!/bin/bash

##############################################################################################################
# This script runs the simulation for the military coordination application with varying link delay for specified number of rounds
# command to run the script: evaluation/accuracy-analysis/military-coordination/scripts/linkDelayExp.sh
##############################################################################################################

# Specified link delay
arrLinkDelay=(150 250)
nRounds=$(seq 1 5)

for linkDelay in "${arrLinkDelay[@]}";do
    for round in $nRounds;do
        # Changing link delay in emuNetwork.py
        linkDelayStr="linkDelay = "\"$linkDelay"ms\""
        # echo $linkDelayStr
        sed -i "42s/.*/\t\t\t$linkDelayStr/" emuNetwork.py

        # Run the CPU and memory monitor script
        sudo python3 cpu-mem-monitor.py $linkDelay"ms-round"$round &
        echo 'CPU and memory monitor script started'

        # Run the actual simulation
        sudo python3 main.py evaluation/accuracy-analysis/military-coordination/input.graphml --time 300

        # Kill the CPU and memory monitor script
        sudo pkill -9 python3
        echo 'CPU and memory monitor script killed'

        # Run the bandwidth plot script
        sudo python3 plot-scripts/bandwidthPlotScript.py --number-of-switches 1 --switch-ports S1-P1,S1-P2,S1-P3,S1-P4 --port-type access-port --ntopics 2 --replication 4 --log-dir logs/output
        echo 'bandwidth plot script finished.'

        # Run the latency plot script
        sudo touch logs/output/latencyAvg.txt
        sudo chmod 666 logs/output/latencyAvg.txt
        sudo python3 evaluation/accuracy-analysis/military-coordination/scripts/testbedScripts/modifiedLatencyPlotScript.py >> logs/output/latencyAvg.txt
        echo 'bandwidth plot script finished.'

        # Run the CPU and memory plot script
        sudo python3 plot-scripts/cpuMemPlotScript.py --test $linkDelay"ms-round"$round
        echo 'CPU and memory plot script finished'

        # Log store to the designated directory
        sudo mkdir -p evaluation/accuracy-analysis/military-coordination/logs/simulation-logs/$linkDelay"ms"/round$round
        sudo cp -r logs/* evaluation/accuracy-analysis/military-coordination/logs/simulation-logs/$linkDelay"ms"/round$round
        echo 'Logs stored.'
        sudo rm -rf logs/cpu-mem/*

        echo "link delay $linkDelay ms round$round finished."
    done
done

# Revert to original link delay
linkDelayStr="linkDelay = \"1ms\""
sed -i "42s/.*/\t\t\t$linkDelayStr/" emuNetwork.py