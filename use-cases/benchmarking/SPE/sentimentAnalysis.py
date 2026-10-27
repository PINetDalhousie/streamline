from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import functions as F
from textblob import TextBlob
import time
import sys
import logging

# text classification
def polarity_detection(text):
    return TextBlob(text).sentiment.polarity
def subjectivity_detection(text):
    return TextBlob(text).sentiment.subjectivity
def text_classification(lines):
    # polarity detection
    polarity_detection_udf = udf(polarity_detection, StringType())
    lines = lines.withColumn("polarity", polarity_detection_udf("msg"))
    # subjectivity detection
    subjectivity_detection_udf = udf(subjectivity_detection, StringType())
    lines = lines.withColumn("subjectivity", subjectivity_detection_udf("msg"))
    return lines

if __name__ == "__main__":
    try:        
        kafkaNode = "10.0.0.1:9092"
        sparkInputFrom = "topic-0"
        sparkOutputTo = 'topic-1'

        logging.basicConfig(filename="logs/output/spark1.log",\
		                    format='%(asctime)s %(levelname)s:%(message)s',\
                            level=logging.INFO)
        logging.info("node: 1")
        logging.info("input topic: "+sparkInputFrom)
        logging.info("output topic: "+sparkOutputTo)

        # create Spark session
        spark = SparkSession.builder.appName("TwitterSentimentAnalysis").getOrCreate()
        spark.sparkContext.setLogLevel('ERROR')
        
        # Create DataFrame representing the stream of input lines from connection to host:port
        lines = spark\
            .readStream\
            .format('kafka')\
            .option('kafka.bootstrap.servers', kafkaNode) \
            .option("startingOffsets", "earliest")\
            .option("failOnDataLoss", False)\
            .option('subscribe', sparkInputFrom)\
            .load()\
            .selectExpr("CAST(value AS STRING)")
        logging.info("Schema of input stream: "+str(lines.printSchema))

        # Separating the data to get the message ID on one side and the message on the other
        split_result = split("value", " Msg: ")
        lines = lines.select(split_result.getItem(0).alias('msgIDString'), split_result.getItem(1).alias('msg'))
        # Extracting the message ID
        split_result = split("msgIDString", "Msg ID: ")
        lines = lines.select(split_result.getItem(1).alias('msgID'), 'msg')
        logging.info("Is Streaming: "+str(lines.isStreaming))
        logging.info("Schema of lines stream after splitting "+str(lines.printSchema))

        # text classification to define polarity and subjectivity
        lines = text_classification(lines)
        logging.info("Schema of words stream after text classification "+str(lines.printSchema))
        
        result = lines.select( concat( lit('MessageID: '), 'msgID', \
                            lit('Message: '), 'msg', \
                            lit(' Polarity: '), 'polarity', \
                            lit('  Subjectivity: '), 'subjectivity' ) \
                            .alias('value') )

        # Write data to the Kafka sink
        output = result.writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafkaNode) \
            .option("topic", sparkOutputTo) \
            .option("checkpointLocation", "logs/output/kafka-checkpoint") \
            .start()
        output.awaitTermination()

    except Exception as e:
        sys.exit(1)