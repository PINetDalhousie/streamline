import argparse
import logging
import sys

from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy
from pyflink.datastream.connectors import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaRecordSerializationSchema
from pyflink.common import SimpleStringSchema
log_file_path = "kafka_flink.log"

logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(message)s")
def word_count(input_path, output_path):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    # write all the data to one file
    env.set_parallelism(1)
    kafka_topic = "inTopic" #Same as in spark
    
    kafka_source = KafkaSource.builder() \
	.set_value_only_deserializer(SimpleStringSchema()) \
	.set_bootstrap_servers("10.0.0.2:9092") \
	.set_topics(kafka_topic) \
	.set_group_id("group_id") \
	.build()
    logging.info("builded kafka source")	
    
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
    out_topic = "outTopic"
    # define the sink
    print("defining sink")
    if output_path is None:
        serializer = KafkaRecordSerializationSchema.builder().set_topic(out_topic).set_value_serialization_schema(SimpleStringSchema()).build()
	
        print("builded serialzer", flush=True)
        sink = KafkaSink.builder() \
	      .set_bootstrap_servers("10.0.0.2:9092") \
	      .set_record_serializer(serializer) \
              .build()
        print("builded sink",flush=True)
        ds.sink_to(sink)
    else:
        print("Printing result to stdout. Use --output to specify output path.")
        ds.print()
    print("executing")
    # submit for execution
    env.execute()
if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

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
