#!/usr/bin/python3

from kafka import KafkaConsumer

from random import seed, random

import sys
import time

import logging

try:
	seed(2)
	nodeName = sys.argv[1]
	consInstance = sys.argv[2]
	nodeID = nodeName[1:]

	logDir = "logs/output"
	logging.basicConfig(filename=logDir+"/cons/"+"cons-node"+nodeID+\
		"-instance"+str(consInstance)+".log",\
		format='%(asctime)s %(levelname)s:%(message)s',\
		level=logging.INFO)
	logging.info("Individual consumer single")
	logging.info("node to initiate consumer: "+nodeID)

	consumers = []
	bootstrapServers="10.0.0.1:9092,10.0.0.2:9092,10.0.0.3:9092"

	topicName = 'topicA'
	logging.info("topicName "+topicName)				

	consumer = KafkaConsumer(bootstrap_servers=bootstrapServers,\
						  auto_offset_reset='earliest')	
	consumer.subscribe(pattern=topicName)

	# Poll the data
	logging.info('Connect to broker looking for topic %s.', topicName)
	messages = {}
	while True:
		startTime = time.time()		
		for msg in consumer:
			try:
				msgContent = str(msg.value, 'utf-8')
				prodID = msgContent[:2]
				msgID = msgContent[2:8]
				topic = msg.topic
				offset = str(msg.offset)    

				key = prodID+"-"+msgID+"-"+topic
				if key in messages:
					logging.warn('ProdID %s MSG %s Topic %s already read. Not logging.', prodID, msgID, topic)				         
				else:
					messages[key] = offset
					logging.info('Prod ID: %s; Message ID: %s; Topic: %s; Offset: %s; Size: %s; Message: %s', prodID, msgID, topic, offset, str(len(msgContent)), msgContent[8:])  			
			except Exception as e:
				logging.error(e + " from messageID %s", msgID)				
		stopTime = time.time()

except Exception as e:
	logging.error(e)	
finally:
	consumer.close()
	logging.info('Disconnect from broker')
	sys.exit(1)