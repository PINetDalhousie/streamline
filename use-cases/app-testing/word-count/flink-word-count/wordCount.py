import logging
import sys
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import Encoder
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaRecordSerializationSchema
from pyflink.common import SimpleStringSchema

log_file_path = "logs/output/flink.log"
IN_TOPIC = "inTopic" #Same as in spark
OUT_TOPIC = "outTopic"
logging.basicConfig(filename=log_file_path, level=logging.INFO, \
        format="%(asctime)s INFO: %(message)s")# Note after entering word count. Lowest log level is Warning
logging.info("input: "+IN_TOPIC)
logging.info("output: "+ OUT_TOPIC)

def word_count():
    env = StreamExecutionEnvironment.get_execution_environment()
    logging.warning("created environment")
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

    logging.warning("connected to kafka source at:"+kafka_node)	
    logging.warning("Group ID is 'group_id'")
    ds = env.from_source(
	source = kafka_source,
	watermark_strategy = WatermarkStrategy.for_monotonous_timestamps(),
	source_name = "kafka_source"
    ) 
    logging.warning("Source name is 'kafka_source'")
    def split(line):
        yield from line.split()

    # compute word count
    ds = ds.flat_map(split) \
        .map(lambda i: (i, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda i: i[0]) \
        .reduce(lambda i, j: (i[0], i[1] + j[1])) \
        .map(lambda i: f'{i[0]}: {i[1]}', output_type = Types.STRING())
    logging.warning("computing wordcount")
    # define the sink
    serializer = KafkaRecordSerializationSchema.builder().set_topic(OUT_TOPIC).set_value_serialization_schema(SimpleStringSchema()).build()
	
    
    sink = KafkaSink.builder() \
	  .set_bootstrap_servers(kafka_node) \
	  .set_record_serializer(serializer) \
          .build()
    ds.sink_to(sink)
    logging.warning("Connected to kafka sink at: "+kafka_node)
    logging.warning("executing")
    logging.warning("Output to broker at: "+ kafka_node)
    # submit for execution
    env.execute()
if __name__ == '__main__':
    word_count()
    logging.info("successfully completed")
