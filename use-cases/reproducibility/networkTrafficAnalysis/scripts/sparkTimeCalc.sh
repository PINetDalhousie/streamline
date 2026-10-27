#!/bin/bash

##############################################################################################################
# This script is for parsing and calculating the average end-to-end latency per packet(in ms) and the average spark execution
# time(ms) for the network traffic analysis application for varying number of concurrent users (20,40,60,80,100)
# producers. 
# command to run the script:
# use-cases/reproducibility/networkTrafficAnalysis/scripts/sparkTimeCalc.sh
##############################################################################################################


# Define the array of nodes
nodes=("1node" "2node" "3node")  # Replace with your actual nodes

# Define the array of producers
producers=(20 40 60 80 100)
# Declare an array to hold the avg_exec_time values
declare -a avg_exec_time_values
# Declare an array to hold the avg_latency values
declare -a avg_latency_values

# Loop over each node
for node in "${nodes[@]}"; do
  # Loop over each producer
  for producer in "${producers[@]}"; do
    total_latency=0
    total_exec_time=0
    # Loop over each round
    for round in $(seq 1 5); do
      # Extract the latency value from the log file
      latency=$(grep 'Avg. total end-to-end latency per packet(in ms):' use-cases/reproducibility/networkTrafficAnalysis/logs/${node}/${producer}producer/round${round}/output/latencyAvg.txt | awk '{print $NF}')
      # Add the latency to the total
      total_latency=$(echo "$total_latency + $latency" | bc)

      # Extract the spark execution time from the log file
      exec_time=$(grep 'average spark execution time after reaching steady state(in ms):' use-cases/reproducibility/networkTrafficAnalysis/logs/${node}/${producer}producer/round${round}/output/latencyAvg.txt | awk '{print $NF}')
      # Add the execution time to the total
      total_exec_time=$(echo "$total_exec_time + $exec_time" | bc)
      
    done
    # Calculate the average latency
    avg_latency=$(echo "scale=2; $total_latency / 5" | bc)
    # echo "Average latency for $node with $producer producers: $avg_latency ms"
    # Append avg_latency to the array
    avg_latency_values+=("$avg_latency")

    # Calculate the average execution time
    avg_exec_time=$(echo "scale=2; $total_exec_time / 5" | bc)
    # echo "Average Spark executionlatency for $node with $producer producers: $avg_exec_time ms"
    # Append avg_exec_time to the array
    avg_exec_time_values+=("$avg_exec_time")
    # echo "------------------------------------------"
    # echo -e "\n"
  done
done

# print out all avg_latency values
echo "Average latency: ${avg_latency_values[@]}"
# print out all avg_exec_time values
echo "Average execution times: ${avg_exec_time_values[@]}"