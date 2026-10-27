## Command to run script: 
#first, need to be in pyflink directory.
# then enter command: sudo bin/flink run --target local --python ../use-cases/app-testing/word-count/flink-word-count/flink-word-count.py --jarfile ../dependency/jars/flink-sql-connector-kafka-1.17.1.jar

import argparse
import logging
import sys
sys.path.append(".")
sys.path.append("../")
#sys.path.append("../../../")
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import Encoder
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaRecordSerializationSchema
from pyflink.common import SimpleStringSchema
log_file_path = "../logs/output/flink.log"
IN_TOPIC = "inTopic" #Same as in spark
OUT_TOPIC = "outTopic"
logging.basicConfig(filename=log_file_path, level=logging.INFO, \
        format="%(asctime)s %(levelname)s: %(message)s")
logging.info("input: "+IN_TOPIC)
logging.info("output: "+ OUT_TOPIC)

def word_count(input_path, output_path):
    env = StreamExecutionEnvironment.get_execution_environment()
    logging.info("created environment")
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    # write all the data to one file
    env.set_parallelism(1)
    kafka_node = "10.0.0.2:9092"
    kafka_source = KafkaSource.builder() \
	.set_value_only_deserializer(SimpleStringSchema()) \
	.set_bootstrap_servers(kafka_node) \
	.set_topics(IN_TOPIC) \
	.set_group_id("group_id") \
	.build()

    logging.info("connected to kafka source at:", kafka_node)	
    
    ds = env.from_source(
	source = kafka_source,
	watermark_strategy = WatermarkStrategy.for_monotonous_timestamps(),
	source_name = "kafka_source"
    ) 

    def split(line):
        yield from line.split()

    # compute word count
    ds = ds.flat_map(split) \
        .map(lambda i: (i, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda i: i[0]) \
        .reduce(lambda i, j: (i[0], i[1] + j[1])) \
        .map(lambda i: f'{i[0]}: {i[1]}', output_type = Types.STRING())

    # define the sink
    serializer = KafkaRecordSerializationSchema.builder().set_topic(OUT_TOPIC).set_value_serialization_schema(SimpleStringSchema()).build()
	
    
    sink = KafkaSink.builder() \
	  .set_bootstrap_servers(kafka_node) \
	  .set_record_serializer(serializer) \
          .build()
    ds.sink_to(sink)
    logging.info("executing")
    logging.info("Output to broker at", kafka_node)
    # submit for execution
    env.execute()
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to process.')
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='Output file to write results to.')

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)


    word_count(known_args.input, known_args.output)
    logging.info("successfully completed")
