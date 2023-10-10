# command to run this script: sudo ~/.local/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 sparkApp1.py

import sys
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import *

try:
    # nodeName = sys.argv[1]
    # sparkOutputTo = sys.argv[2]

    sparkInputFrom = "inTopic"
    sparkOutputTo = "outTopic"
    nodeID = "2"

    logging.basicConfig(filename="logs/output/spark1.log",\
		format='%(asctime)s %(levelname)s:%(message)s',\
		level=logging.INFO)
    logging.info("node: "+nodeID)
    logging.info("input: "+sparkInputFrom)
    logging.info("output: "+sparkOutputTo)

    spark = SparkSession\
        .builder\
        .appName("StructuredNetworkWordCount"+nodeID)\
        .getOrCreate()

    spark.sparkContext.setLogLevel('ERROR')

    kafkaNode = "10.0.0.2:9092"
    logging.info("Connected at Broker: "+kafkaNode)

    # Create DataFrame representing the stream of input lines from connection to host:port
    lines = spark\
        .readStream\
        .format('kafka')\
        .option('kafka.bootstrap.servers', kafkaNode) \
        .option("startingOffsets", "earliest")\
        .option("failOnDataLoss", False)\
        .option('subscribe', sparkInputFrom)\
        .load().selectExpr("CAST(value AS STRING)")

    # # Separating the data to get the file number on one side and the words on the other
    # split_result = split("value", " File: ")
    # lines = lines.select(split_result.getItem(0).alias('value'), split_result.getItem(1).alias('file'))

    # # Separating the data to get the topic name on one side and the words on the other
    # split_result = split("value", " Topic: ")
    # lines = lines.select(split_result.getItem(0).alias('value'), split_result.getItem(1).alias('topic'), 'file')


    # # Splitting the sentences into one word per row along with the file it originated from
    # words = lines.select('topic', 'file',\
    #         explode(
    #             split(lines.value, ' ')
    #             ).alias('word')
    #         )
    
    # # # Getting the word frequency count per file
    # result = words.groupBy('topic', 'file', 'word')\
    #     .agg( approx_count_distinct('word').alias('frequency') ).orderBy('topic','file')

    # # # Formatting the result for storage into a kafka topic
    # result = result.select( concat( lit('Topic: '), 'topic', lit(' File: '),\
    #      'file', lit('  Word: '), 'word', lit('  Frequency: '), 'frequency' ).alias('value') )

    # logging.info(result.printSchema())

    #Use of Kafka topic as a sink
    output = lines.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaNode) \
    .option("topic", sparkOutputTo) \
    .option("checkpointLocation", "logs/output/wordcount_checkpoint_intermediate") \
    .start()
    output.awaitTermination()

except Exception as e:
	logging.error(e)
	sys.exit(1)