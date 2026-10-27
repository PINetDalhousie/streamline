#!/bin/bash

######################
# Command: evaluation/accuracy-analysis/military-coordination/scripts/testbedScripts/testbedLogParsing.sh
######################
#!/bin/bash

# take input for experiment name and round number
echo "Enter experiment name: "
read expName
echo "Enter round number: "
read nRound

# Collecting logs from testbed
sudo mkdir -p evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/cons 
sudo chmod o+w evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/cons
sudo mkdir -p evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/prod
sudo chmod o+w evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/prod

# collect consumer logs
scp  pinet-tb1:~/streamline/logs/output/cons/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/cons/
scp  pinet-tb2:~/streamline/logs/output/cons/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/cons/
scp  pinet-gpu5:~/streamline/logs/output/cons/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/cons/
scp  pinet-gpu6:~/streamline/logs/output/cons/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/cons/

# collect producer logs
scp  pinet-tb1:~/streamline/logs/output/prod/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/prod/
scp  pinet-tb2:~/streamline/logs/output/prod/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/prod/
scp  pinet-gpu5:~/streamline/logs/output/prod/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/prod/
scp  pinet-gpu6:~/streamline/logs/output/prod/* evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/prod/

# Latency plot generation
sudo touch evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/latencyAvg.txt
sudo chmod 666 evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/latencyAvg.txt
sudo python3 evaluation/accuracy-analysis/military-coordination/scripts/testbedScripts/modifiedLatencyPlotScript.py --log-dir evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound >> evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/$expName"ms"/"round-"$nRound/latencyAvg.txt


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Exta script
# server=('pinet-tb1' 'pinet-tb2')

# # clean up previous logs
# sudo rm /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt
# sudo touch /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt
# sudo chmod 666 /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt

# Initiate zookeeper and kafka
# ssh ${server[0]} sudo sh /users/grad/ifath/streamline/hostScript-TB1.sh enp1s0np1 1 1000 1 10.50.1.1 >> /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt &
# ssh ${server[1]} sudo sh /users/grad/ifath/streamline/hostScript-TB2.sh enp1s0np1np1 1 1000 2 10.50.1.2 >> /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt &
# sleep 200
# echo 'Zookeeper and Kafka initiated'

    
# # # Create 2 topics in host1
# ssh ${server[0]} sudo /users/grad/ifath/streamline/kafka/bin/kafka-topics.sh --create --topic topic-0 --bootstrap-server 10.50.1.1:9092 --replication-factor 2
# ssh ${server[0]} sudo /users/grad/ifath/streamline/kafka/bin/kafka-topics.sh --create --topic topic-1 --bootstrap-server 10.50.1.1:9092 --replication-factor 2
# echo 'Topics created'
# # # list all topics
# echo 'Topic description'
# ssh ${server[0]} sudo /users/grad/ifath/streamline/kafka/bin/kafka-topics.sh --describe --bootstrap-server 10.50.1.1:9092
# sleep 5

# # Initiate producers and consumers
# ssh ${server[0]} sudo sh /users/grad/ifath/streamline/simulationScript-TB1.sh enp1s0np1 1 1000 1 10.50.1.1 >> /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt
# ssh ${server[1]} sudo sh /users/grad/ifath/streamline/simulationScript-TB2.sh enp1s0np1np1 1 1000 2 10.50.1.2 >> /home/monzurul/Desktop/streamline/evaluation/accuracy-analysis/military-coordination/logs/testbed-logs/dump.txt
# echo 'Producers and consumers initiated'
# --------------------------------------------------------------------------------------------------------------