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
	topicName = 'topic-1'

	logDir = "logs/output"
	logging.basicConfig(filename=logDir+"/cons/"+"cons-node"+nodeID+\
		"-instance"+str(consInstance)+".log",\
		format='%(asctime)s %(levelname)s:%(message)s',\
		level=logging.INFO)
	logging.info("CUSTOM consumer")
	logging.info("node to initiate consumer: "+nodeID)

	bootstrapServers="10.0.0.1:9092"  			
	logging.info("**Configuring KafkaConsumer** topicName=" + topicName + " bootstrap_servers=" + str(bootstrapServers))
	consumer = KafkaConsumer(topicName,\
		bootstrap_servers=bootstrapServers,\
		auto_offset_reset='earliest',\
		enable_auto_commit=True)	

	# Poll the data
	logging.info('Connect to broker looking for topic %s.', topicName)
	messages = {}
	while True:
		startTime = time.time()		
		for msg in consumer:
			try:
				msgContent = str(msg.value, 'utf-8')
				logging.info('Message: %s', msgContent)           			
				# prodID = msgContent[:2]
				# msgID = msgContent[2:8]
				# mainMsg = msgContent[8:]
				# topic = msg.topic
				# offset = str(msg.offset)    

				# key = prodID+"-"+msgID+"-"+topic
				# if key in messages:
				# 	logging.warn('ProdID %s MSG %s Topic %s already read. Not logging.', prodID, msgID, topic)				         
				# else:
				# 	messages[key] = offset
				# 	logging.info('Prod ID: %s; Message ID: %s; Topic: %s; Offset: %s; Size: %s; Message: %s', prodID, msgID, topic, offset, str(len(msgContent)), mainMsg)           			
			except Exception as e:
				# logging.error(e + " from messageID %s", msgID)
				logging.error(e)				
		stopTime = time.time()

except Exception as e:
	logging.error(e)	
finally:
	consumer.close()
	logging.info('Disconnect from broker')
	sys.exit(1)