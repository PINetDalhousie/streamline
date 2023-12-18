#!/bin/bash

##############################################################################################################
# This script is for experimenting with different number of spark local clusters (1/2/3 worker instances 
# in the same node) for the network traffic analysis application for varying number of concurrent users
#  (20,40,60,80,100 producers). Each experiment will run for 5 rounds.

# command to run the script: 
# use-cases/reproducibility/networkTrafficAnalysis/scripts/clusterExperiment.sh
##############################################################################################################

# Hard-coded expeiement parameters
arrNumClusters=(1 2 3)
nRounds=$(seq 1 5)
nProducers=(20 40 60 80 100)

# Toy experiment parameters
# arrNumClusters=(1 2 3)
# nRounds=$(seq 1 1)
# nProducers=(80)

for node in "${arrNumClusters[@]}";do
    for producer in ${nProducers[@]};do
        for round in $nRounds;do
            # Changing number of producer instances in producerConfiguration.yaml
            producerStr="producerInstances: $producer"

            sed -i "4s/.*/  $producerStr/" use-cases/reproducibility/networkTrafficAnalysis/yamlConfig/producerConfiguration.yaml

            # Changing number of spark local clusters in spark-env.sh
            sparkClusterStr="export SPARK_WORKER_INSTANCES=$node"
            sed -i "2s/.*/$sparkClusterStr/" spark/spark-3.2.1/conf/spark-env.sh

            # Run the CPU and memory monitor script
            sudo python3 cpu-mem-monitor.py ${node}node-${producer}producer-round${round} &
            echo 'CPU and memory monitor script started'

            # Run the simulation with the specified number of spark local clusters
            sudo python3 main.py use-cases/reproducibility/networkTrafficAnalysis/input-cluster.graphml\
            --time 300 --spark-cluster 1

            # Kill the CPU and memory monitor script
            sudo pkill -9 python3
            echo 'CPU and memory monitor script killed'

            # Run the logParse script to calculate the average end-to-end latency per packet(in ms)
            sudo touch logs/output/latencyAvg.txt
            sudo chmod 666 logs/output/latencyAvg.txt
            sudo python3 use-cases/reproducibility/networkTrafficAnalysis/scripts/logParse.py logs/output/prod logs/output/cons/cons-node3-instance1.log $producer\
             spark >> logs/output/latencyAvg.txt
            echo 'logParse script finished.'

            # Run the sparkLogParse script to calculate the average spark execution time(ms)
            sudo python3 use-cases/reproducibility/networkTrafficAnalysis/scripts/sparkLogParse.py logs/output/spark1.log >> logs/output/latencyAvg.txt
            echo 'sparkLogParse script finished.'

            # Log store to the designated directory
            sudo mkdir -p use-cases/reproducibility/networkTrafficAnalysis/logs/${node}node/${producer}producer/round${round}
            sudo cp -r logs/* use-cases/reproducibility/networkTrafficAnalysis/logs/${node}node/${producer}producer/round${round}/
            echo 'Logs stored.'
            # Remove the cpu-memory logs from the logs directory
            sudo rm -rf logs/cpu-mem

            #  Store the configuration files and spark logs
            sudo mkdir -p use-cases/reproducibility/networkTrafficAnalysis/logs/${node}node/${producer}producer/round${round}/sparkLogs
            sudo cp -r spark/spark-3.2.1/logs/*  use-cases/reproducibility/networkTrafficAnalysis/logs/${node}node/${producer}producer/round${round}/sparkLogs 
            sudo cp spark/spark-3.2.1/conf/spark-env.sh use-cases/reproducibility/networkTrafficAnalysis/logs/${node}node/${producer}producer/round${round}/sparkLogs

            echo "$node nodes $producer producers round$round experiment finished."
            echo "------------------------------------------"
            echo -e "\n\n"
        done
        echo "Experiment with $producer producers finished."
        echo "------------------------------------------"
        echo -e "\n\n"
    done
    echo "Experiment with $node spark workers finished."
    echo "------------------------------------------"
    echo -e "\n\n"
done

