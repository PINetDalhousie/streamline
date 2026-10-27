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
			# logging.info('Produced message ID: %s; Value: %s', str(kPointerKey[0]), logMsgStatus)
		except Exception as e:
			logging.info('Message not produced. ID: %s; Error: %s', str(kPointerKey[0]), e)


def readXmlFileMessage(file):
	lines = file.readlines()
	readFile = ' '
	for line in lines:
		readFile += line
	logging.info("Read xml file is : %s", readFile)
	return readFile

def processXmlMessage(message):
	processedMessage = ' '
	randomNum = str(random.randint(1,999))
	# Randomize values in XML message
	processedMessage = re.sub('[0-9]+', randomNum, message)	
	encodedMessage = processedMessage.encode()	
	return encodedMessage

def processFileMessage(file):
	message = file.read().encode()
	return message

def readMessageFromFile(filePath):
	file = open(filePath, 'r')
	_, fileExt = os.path.splitext(filePath)

	if(fileExt.lower() == '.xml'):
		message = readXmlFileMessage(file)
	#elif(fileExt.lower == '.svg'):
	#	message = processSvgFile(file)
	else:
		message = processFileMessage(file)

	return message

try:
	node = sys.argv[1]
	prodInstanceID = sys.argv[2]
	nodeID = node[1:]
	
	acks = 0
	messageFilePath="use-cases/reliability/message-loss/dataDir/500B-load.txt"
	logDir = "logs/output"
	logging.basicConfig(filename=logDir+"/prod/"+"prod-node"+nodeID+\
								"-instance"+str(prodInstanceID)+".log",
								format='%(asctime)s %(levelname)s:%(message)s',
								level=logging.INFO) 

	seed(1)
	msgID = 0
	logging.info("node: "+nodeID)
    
	bootstrapServers="10.0.0.1:9092,10.0.0.2:9092,10.0.0.3:9092"
	producer = KafkaProducer(bootstrap_servers=bootstrapServers, acks=acks)

	#Use a queue and a separate thread to log messages that were not produced properly
	q = Queue(maxsize=0)
	prodMsgThread = Thread(target=processProdMsg, args=(q,))
	prodMsgThread.start()

	while msgID < 350000:
		message = readMessageFromFile(messageFilePath)	
		newMsgID = str(msgID).zfill(6)
		bMsgID = bytes(newMsgID, 'utf-8')
		newNodeID = nodeID.zfill(2)
		bNodeID = bytes(newNodeID, 'utf-8')
		bMsg = bNodeID + bMsgID + bytearray(message)
		topicName = 'topicA'

		prodStatus = producer.send(topicName, bMsg)
		logging.info('Topic-name: %s; Message ID: %s; Message: %s',\
					topicName, newMsgID, message)

		msgInfo = {}
		msgInfo[newMsgID] = prodStatus
		q.put(msgInfo)

		msgID += 1

except Exception as e:
	logging.error(e)
	sys.exit(1)