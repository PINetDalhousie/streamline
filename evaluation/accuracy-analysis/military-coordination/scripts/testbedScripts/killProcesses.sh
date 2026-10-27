#!/bin/bash
#################################################################
# Script name       : killProcesses.sh
# Description       : Script to kill all processes in the testbed nodes (TB1, TB2, GPU5, GPU6)
# Command to run    : ./killProcesses.sh
#################################################################

# kill producer & consumer processes
sudo pkill -9 -f military-data-producer.py; sudo pkill -9 -f military-consumerSingle.py
echo "Killed producer & consumer processes"

# Kill existing processes (Bk & ZK)
sudo pkill -9 -f server-TB1.properties; 
sudo pkill -9 -f server-TB2.properties; 
sudo pkill -9 -f server-GPU5.properties; 
sudo pkill -9 -f server-GPU6.properties; 
sudo pkill -9 -f zookeeper
echo "Killed existing processes (Bk & ZK)"

exit 0