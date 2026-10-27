# This file is going to be our maritime application. At this point, this file reads AIS data from a kafka topic,
# does some processing, then stores the result in a kafka topic with a particular json format.

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from kafka import KafkaProducer

import sys
import json
import logging

try:
    sparkInputFrom = "maritimeInput"
    sparkOutputTo = "maritimeOutput"

    nodeID = "1"
    host = "10.0.0."+nodeID
    kafkaNode = host + ":9092"

    logging.basicConfig(filename="logs/output/maritimeSpark.log",\
        format='%(asctime)s %(levelname)s:%(message)s',\
        level=logging.INFO)
    logging.info("node: "+nodeID)
    logging.info("input: "+sparkInputFrom)
    logging.info("output: "+sparkOutputTo)

    
    # Some basic spark setup
    spark = SparkSession.builder \
            .appName("Spark Structured Streaming for Maritime") \
            .getOrCreate()

    spark.sparkContext.setLogLevel('ERROR')

    # Now, we read in the AIS data from the kafka topic

    vessel = spark\
            .readStream\
            .format('kafka')\
            .option('kafka.bootstrap.servers', kafkaNode)\
            .option('subscribe', sparkInputFrom)\
            .option("startingOffsets", "earliest")\
            .option("failOnDataLoss", False)\
            .load()\
            .selectExpr("CAST(value AS STRING)")
    logging.info("Streaming: "+str(vessel.isStreaming))
    logging.info("Schema: "+str(vessel.printSchema))

    # Since the data we read is in json format, we extract all the fields and use them to make new columns

    vessel = vessel.select(json_tuple(col("value"),"class", "device", "repeat", "mmsi", "type", "lat", "lon",\
            "scaled", "status", "status_text", "turn", "speed", "accuracy", "course", "heading", "second", \
            "manuever", "raim", "radio", "reserved", "regional", "cs", "display", "dsc", "band", "msg22",\
            "imo", "ais_version", "callsign", "shipname", "shiptype", "shiptype_text", "to_bow", "to_stern", \
            "to_port", "to_starboard", "epfd", "epfd_text", "eta", "draught", "destination", "dte", \
            "aid_type", "aid_type_text", "name", "off_position", "virtual_aid"))\
            \
            .toDF("class", "device", "repeat", "mmsi", "type", "lat", "lon",\
            "scaled", "status", "status_text", "turn", "speed", "accuracy", "course", "heading", "second", \
            "manuever", "raim", "radio", "reserved", "regional", "cs", "display", "dsc", "band", "msg22",\
            "imo", "ais_version", "callsign", "shipname", "shiptype", "shiptype_text", "to_bow", "to_stern", \
            "to_port", "to_starboard", "epfd", "epfd_text", "eta", "draught", "destination", "dte", \
            "aid_type", "aid_type_text", "name", "off_position", "virtual_aid")

    vessel = vessel.withColumn("timestamp", current_timestamp())

    # Getting the columns with our required information. We use messages of type 5 as other messages types have null values in these columns
    vessel = vessel.filter( col("type") == 5).select("timestamp", "destination", "shiptype","shiptype_text", "mmsi")

    # This is our query
    # We get the types of ships at each destination each minute, along with the number and names of ships
    query = vessel\
        .withWatermark("timestamp", "1 second") \
        .groupBy(window("timestamp", "1 second"), "destination", "shiptype")\
        .agg(approx_count_distinct("mmsi").alias("numberOfShips"),\
        collect_set("mmsi").alias("shipIDs"))

    logging.info("Query Streaming: "+str(query.isStreaming))
    logging.info("Query Schema: "+str(query.printSchema))

    # to produce the message in Kafka topic
    # to produce the message in Kafka topic
    query = query.select( concat( \
        lit(' Start time: '), date_format('window.start', 'yyyy-MM-dd HH:mm:ss'),\
        lit(' End time: '), date_format('window.end', 'yyyy-MM-dd HH:mm:ss'),\
        lit(' Destination: '), 'destination',\
        lit(' Shiptype: '), 'shiptype',\
        lit(' Number of ships: '), 'numberOfShips',\
        lit(' Ship IDs: '), concat_ws(", ", 'shipIDs')\
        ).alias('value') )

    # Sending the dataframe to the kafka topic
    kafkaNode2 = "10.0.0.2:9092"
    output = query.writeStream \
        .format("kafka") \
        .outputMode("append")\
        .option("kafka.bootstrap.servers", kafkaNode2) \
        .option("topic", sparkOutputTo) \
        .option("checkpointLocation", "logs/output/maritimeMonitoring_checkpoint") \
        .start()\
        .awaitTermination()
    
except Exception as e:
	logging.error(e)
	sys.exit(1)