# This script experiments with varying message-rate the military coordination application
# command to run the script: sudo bash evaluation/accuracy-analysis/military-coordination/scripts/msgRateExp.sh
#!/bin/bash

# User input for message rate
read -p "Enter message rate (in comma separated integers): " input
array=(${input//,/ })

# iterate over each message-rate
for mRate in "${array[@]}";do
    # Changing message-rate in producer
    sed -i "87s/.*/	mRate = $mRate/" evaluation/accuracy-analysis/military-coordination/military-data-producer.py

    # Run the CPU and memory monitor script
    sudo python3 cpu-mem-monitor.py mRate-$mRate &
    echo 'CPU and memory monitor script started'

    # Run the actual simulation
    sudo python3 main.py evaluation/accuracy-analysis/military-coordination/input.graphml --time 300

    # Kill the CPU and memory monitor script
    sudo pkill -9 python3
    echo 'CPU and memory monitor script killed'

    # Run the bandwidth plot script
    sudo python3 plot-scripts/bandwidthPlotScript.py --number-of-switches 2 --switch-ports S1-P1,S1-P2,S1-P3,S1-P4,S2-P1,S2-P2,S2-P3,S2-P4 --port-type access-port --message-rate $mRate --ntopics 2 --replication 4 --log-dir logs/output
    echo 'bandwidth plot script finished.'

    # Run the CPU and memory plot script
    sudo python3 plot-scripts/cpuMemPlotScript.py --test mRate-$mRate
    echo 'CPU and memory plot script finished'

    # Log store to the designated directory
    cp -r logs/* evaluation/accuracy-analysis/military-coordination/logs/mRate-$mRate
    echo 'Logs stored.'
    sudo rm -rf logs/cpu-mem/*

    echo "Experiment with $mRate message-rate finished."
done

# Changing message-rate in producer to original value
sed -i "87s/.*/	mRate = 30/" evaluation/accuracy-analysis/military-coordination/military-data-producer.py
echo 'Simulation finished'