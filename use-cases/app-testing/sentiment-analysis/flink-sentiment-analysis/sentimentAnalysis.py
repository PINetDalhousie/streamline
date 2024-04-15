import re
import json
import logging
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from textblob import TextBlob

# Initialize logging
logging.basicConfig(level=logging.INFO)

IN_TOPIC = "topic-0"
OUT_TOPIC = "topic-1"
KAFKA_SERVER = "10.0.0.2:9092"

# Function to preprocess the data
def preprocess(line):
    line = line.lower()
    line = re.sub(r'http\S+', '', line)
    line = re.sub(r'@\w+', '', line)
    line = line.replace('#', '').replace('RT', '').replace(':', '')
    return line

# Functions for sentiment analysis
def polarity_detection(text):
    return TextBlob(text).sentiment.polarity

def subjectivity_detection(text):
    return TextBlob(text).sentiment.subjectivity

# Define the processing function
class SentimentAnalysisFunction(MapFunction):
    def map(self, value):
        value = preprocess(value)
        polarity = polarity_detection(value)
        subjectivity = subjectivity_detection(value)
        return json.dumps({
            'text': value,
            'polarity': polarity,
            'subjectivity': subjectivity
        })

if __name__ == "__main__":
    logging.info("Starting Flink Sentiment Analysis Application")

    # Initialize the Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()

    # Define Kafka source
    kafka_consumer = FlinkKafkaConsumer(
        topics=IN_TOPIC,
        properties={"bootstrap.servers": KAFKA_SERVER},
        deserialization_schema=SimpleStringSchema()
    )
    logging.info("Kafka consumer set up")

    # Define Kafka sink
    kafka_producer = FlinkKafkaProducer(
        topic=OUT_TOPIC,
        serialization_schema=SimpleStringSchema(),
        producer_config={"bootstrap.servers": KAFKA_SERVER}
    )
    logging.info("Kafka producer set up")

    # DataStream
    data_stream = env.add_source(kafka_consumer)
    result_stream = data_stream.map(SentimentAnalysisFunction(), output_type=Types.STRING())

    # Send results to Kafka
    result_stream.add_sink(kafka_producer)

    # Execute the Flink application  
    logging.info("Executing the Flink application")
    env.execute("Flink Sentiment Analysis")