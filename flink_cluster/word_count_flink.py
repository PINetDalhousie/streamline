'''
Author: Callum MacNeil
There is additional documentation available in the form of a google doc.
The following code is taken from apache flink. There are 
examples that come with pip installing pyflink. 
Also using the offical pyflink documention for this example.

This example uses tumbling window. However, sliding window mode may be better for 
increasing parallelism. See https://nightlies.apache.org/flink/flink-docs-master/docs/dev/datastream/operators/windows/
'''

import argparse
import logging
import sys
import os
from typing import Iterable
from datetime import datetime
from pyflink.common import WatermarkStrategy, Encoder, Types, Configuration, Time, Duration
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode, ProcessWindowFunction
from pyflink.datastream.window import TumblingEventTimeWindows, TimeWindow
from pyflink.datastream.time_characteristic import TimeCharacteristic
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy
word_count_data = ["To be, or not to be,--that is the question:--",
                   "Whether 'tis nobler in the mind to suffer",
                   "The slings and arrows of outrageous fortune",
                   "Or to take arms against a sea of troubles,",
                   "And by opposing end them?--To die,--to sleep,--",
                   "No more; and by a sleep to say we end",
                   "The heartache, and the thousand natural shocks",
                   "That flesh is heir to,--'tis a consummation",
                   "Devoutly to be wish'd. To die,--to sleep;--",
                   "To sleep! perchance to dream:--ay, there's the rub;",
                   "For in that sleep of death what dreams may come,",
                   "When we have shuffled off this mortal coil,",
                   "Must give us pause: there's the respect",
                   "That makes calamity of so long life;",
                   "For who would bear the whips and scorns of time,",
                   "The oppressor's wrong, the proud man's contumely,",
                   "The pangs of despis'd love, the law's delay,",
                   "The insolence of office, and the spurns",
                   "That patient merit of the unworthy takes,",
                   "When he himself might his quietus make",
                   "With a bare bodkin? who would these fardels bear,",
                   "To grunt and sweat under a weary life,",
                   "But that the dread of something after death,--",
                   "The undiscover'd country, from whose bourn",
                   "No traveller returns,--puzzles the will,",
                   "And makes us rather bear those ills we have",
                   "Than fly to others that we know not of?",
                   "Thus conscience does make cowards of us all;",
                   "And thus the native hue of resolution",
                   "Is sicklied o'er with the pale cast of thought;",
                   "And enterprises of great pith and moment,",
                   "With this regard, their currents turn awry,",
                   "And lose the name of action.--Soft you now!",
                   "The fair Ophelia!--Nymph, in thy orisons",
                   "Be all my sins remember'd."]


# from /home/p4/.local/lib/python3.8/site-packages/pyflink/examples/tumbling_window.py
class FirstElementTimestampAssigner(TimestampAssigner):
   
    def extract_timestamp(self, value, record_timestamp) -> int:
        return int(value[1])

# from /home/p4/.local/lib/python3.8/site-packages/pyflink/examples/tumbling_window.py
class CountWindowProcessFunction(ProcessWindowFunction[tuple, tuple, str, TimeWindow]):
    def process(self,
                key: str,
                context: ProcessWindowFunction.Context[TimeWindow],
                elements: Iterable[tuple]) -> Iterable[tuple]:
        #return [(key, context.window().start, context.window().end, len([e for e in elements]))]
        return [(key, len([e for e in elements]))]
#from /home/p4/.local/lib/python3.8/site-packages/pyflink/examples/word_count.py
def word_count(input_path, output_path):
    logging.info("IN WORDCOUNT")
    logging.warning("WARNING LOG")
    env = StreamExecutionEnvironment.get_execution_environment()
    logging.info("ENV CREATED")
    logging.warning("WARNING LOG: ENV CREATED")
    env.set_parallelism(2) # SETTING PARALLELISM 2 == 2 task managers required. 
    # define the source NOT SET UP FOR WINDOWING
    if input_path is not None:
        ds = env.from_source(
            source=FileSource.for_record_stream_format(StreamFormat.text_line_format(),
                                                       "~/stream2gym/apache_flink_tutorial/input.txt")
                             .process_static_file_set().build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source"
        )
    else:
        print("Executing word_count example with default input data set.")
        print("Use --input to specify file input.")
        ds = env.from_collection(word_count_data, type_info=Types.STRING())
    def split(line):
        yield from line.split()

    ws = WatermarkStrategy \
        .for_monotonous_timestamps(). \
        with_timestamp_assigner(FirstElementTimestampAssigner())# Create timestamper using above class
    # compute word count 
    # Important that watermark is assinged before key_by
    ds = ds.flat_map(split) \
        .map(lambda i: (i, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .assign_timestamps_and_watermarks(ws) \
        .key_by(lambda i: i[0]) \
        .window(TumblingEventTimeWindows.of(Time.milliseconds(200))) \
        .process(CountWindowProcessFunction(), # 
                 Types.TUPLE([Types.STRING(), Types.INT()]))
    #After having watermarking and timestamp function, and process. The rest is the same as vanilla wordcount
    #Please see the original word_count for comparison.
    # define the sink
    if output_path is not None:
        ds.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path,
                encoder=Encoder.simple_string_encoder())
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("prefix")
                .with_part_suffix(".ext")
                .build())
            .with_rolling_policy(RollingPolicy.default_rolling_policy())
            .build()
        )
    else:
        print("Printing result to stdout. Use --output to specify output path.")
        ds.print()
    logging.warning("PYFLINK LOG OUTPUT2")
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
