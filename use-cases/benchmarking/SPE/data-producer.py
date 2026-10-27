#!/usr/bin/python3

from kafka import KafkaProducer

from random import seed, randint, gauss
from queue import Queue
from threading import Thread

import time
import sys
import logging
import re
import random
import os

def processProdMsg(q):
	while True:
		msgStatus = q.get()
		kPointerKey = list(msgStatus.keys())
		kPointerValue = list(msgStatus.values())

		try:
			logMsgStatus = kPointerValue[0].get(timeout=5000)
			logging.info('Produced message ID: %s; Value: %s', str(kPointerKey[0]), logMsgStatus)
		except Exception as e:
			logging.info('Message not produced. ID: %s; Error: %s', str(kPointerKey[0]), e)

def processFileMessage(filePath):
	file = open(filePath, 'r')
	message = file.read().encode()
	return message

try:
	node = sys.argv[1]
	prodInstanceID = sys.argv[2]
	nodeID = node[1:]
	
	mRate = 30
	messageFilePath = 'use-cases/benchmarking/SPE/data.txt'
	logDir = "logs/output"

	logging.basicConfig(filename=logDir+"/prod/"+"prod-node"+nodeID+\
								"-instance"+str(prodInstanceID)+".log",
								format='%(asctime)s %(levelname)s:%(message)s',
								level=logging.INFO) 
 
	
	seed(1)
	msgID = 0
         
	logging.info("node: "+nodeID)
    
	bootstrapServers="10.0.0.1:9092"
	logging.info("**Configuring KafkaProducer** bootstrap_servers=" + str(bootstrapServers))

	producer = KafkaProducer(bootstrap_servers=bootstrapServers)

	# Read the message once and save in cache
	message = processFileMessage(messageFilePath)	
	logging.info("Messages generated from file")

	#Use a queue and a separate thread to log messages that were not produced properly
	q = Queue(maxsize=0)
	prodMsgThread = Thread(target=processProdMsg, args=(q,))
	prodMsgThread.start()

	while True:				
		# newMsgID = str(msgID).zfill(6)
		# bMsgID = bytes(newMsgID, 'utf-8')
		# newNodeID = nodeID.zfill(2)
		# bNodeID = bytes(newNodeID, 'utf-8')
		# bMsg = bNodeID + bMsgID + bytearray(message)

		newMsgID = str(msgID).zfill(6)
		msgIDString = " Msg ID: " + newMsgID 
		msgString = " Msg: "

		bMsg = bytes(msgIDString,'utf-8')+ bytes(msgString,'utf-8') + message
		topicName = 'topic-0'

		prodStatus = producer.send(topicName, bMsg)
		# logging.info('Topic-name: %s; Message ID: %s; Message: %s',\
		# 			topicName, newMsgID, message)

		msgInfo = {}
		msgInfo[newMsgID] = prodStatus
		q.put(msgInfo)

# 		logging.info('Topic: %s; Message ID: %s;', topicName, str(msgID).zfill(3))        
		msgID += 1
		time.sleep(1.0/(mRate))

except Exception as e:
	logging.error(e)
	sys.exit(1)