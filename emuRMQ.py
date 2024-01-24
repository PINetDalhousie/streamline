#!/usr/bin/python3

import os
import logging
import time

def runRMQConfigure(net, brokerPlace):
    netNodes = {}
    debug = True

    for node in net.hosts:
          netNodes[node.name] = node
    
    # Run RabbitMQ server on each node
    port = 5672
    print(brokerPlace)
    for node_id in brokerPlace:
        bID = "h"+str(node_id)

        h = netNodes[bID]
        
        print("Creating rMQ broker at node "+str(node_id))
        
        # Start RabbitMQ server        
        command = 'RABBITMQ_NODE_PORT=' + str(port) + ' RABBITMQ_NODENAME=rabbit@10.0.0.' + node_id + ' rabbitmq-server -detached'
        logging.info("Sending command to mininet node:\n" + command)
        out = h.cmd(command, shell=True)  
        logging.info("Output: " + out)    

        if node_id == "1":
            print("Skip cluster join for first node")
            time.sleep(20)
            logging.info("Diagnostics status")
            logging.info(h.cmd("rabbitmq-diagnostics status -n rabbit@10.0.0." + node_id , shell=True))
        else:
            time.sleep(20)
            # Join node to the cluster on rabbit@10.0.0.1 node
            print("Connecting 10.0.0."+ node_id + " to cluster")
            logging.info(h.cmd('rabbitmqctl stop_app' + ' -n rabbit@10.0.0.' + node_id, shell=True))
            logging.info(h.cmd('rabbitmqctl reset' + ' -n rabbit@10.0.0.' + node_id, shell=True))
            logging.info(h.cmd('rabbitmqctl join_cluster rabbit@10.0.0.1' + ' -n rabbit@10.0.0.' + node_id, shell=True))
            logging.info(h.cmd('rabbitmqctl start_app' + ' -n rabbit@10.0.0.' + node_id, shell=True))
        if debug:
            time.sleep(3)            
            cluster_status = h.cmd('rabbitmqctl cluster_status -n rabbit@10.0.0.' + node_id)
            logging.info(f"Cluster status of node {node_id}:\n" + cluster_status)

    sleep_duration = 30
    print(f"Sleeping for {sleep_duration}s to allow RabbitMQ servers to start")
    time.sleep(sleep_duration)

# Reset rabbitmq by killing old processes and removing old database data
def cleanRabbitState():
    print("Resetting RabbitMQ State...")
    # Kill Producer Processes
    os.system("sudo pkill -9 -f rabbit_producer_async.py")    
    # Kill Consumer Processes
    os.system("sudo pkill -9 -f rabbit_consumer_async.py")
    # Kill remaining rabbitmq processes
    os.system("sudo pkill -9 -f rabbitmq")
    # Kill remaining erlang processes
    os.system("sudo pkill -9 -f erlang")

    # Clean up the database for future simulation runs
    os.system("sudo rm -rf /var/lib/rabbitmq/mnesia")