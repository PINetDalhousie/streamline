from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, DataTypes, EnvironmentSettings, CsvTableSource
from pyflink.table.window import Tumble
from pyflink.table.expressions import lit, col
from pyflink.table.udf import udf
from pyflink.table import DataTypes
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.time import Duration
from pyflink.table import expressions as expr
import pandas as pd 

# Environment setup
env = StreamExecutionEnvironment.get_execution_environment()
env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
settings = EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
t_env = StreamTableEnvironment.create(env, environment_settings=settings)

# Kafka Configuration 
kafka_props = {
    'bootstrap.servers': '10.0.0.1:9092,10.0.0.2:9092', 
    'group.id': 'ride-analysis-group' 
}

def kafka_csv_source(topic, props, schema, col_names, data_types):
    return CsvTableSource(
                col_names,
                data_types,
                topic,
                props,
                "csv" 
            )

# Schema definition
taxiFaresSchema = DataTypes.ROW([
    DataTypes.FIELD("rideId", DataTypes.BIGINT()), 
    DataTypes.FIELD("taxiId", DataTypes.BIGINT()),
    DataTypes.FIELD("driverId", DataTypes.BIGINT()),
    DataTypes.FIELD("startTime", DataTypes.TIMESTAMP_LTZ(3)),
    DataTypes.FIELD("paymentType", DataTypes.STRING()),
    DataTypes.FIELD("tip", DataTypes.FLOAT()),
    DataTypes.FIELD("tolls", DataTypes.FLOAT()),
    DataTypes.FIELD("totalFare", DataTypes.FLOAT())
])

taxiRidesSchema = DataTypes.ROW([
    DataTypes.FIELD("rideId", DataTypes.BIGINT()),
    DataTypes.FIELD("isStart", DataTypes.STRING()),
    DataTypes.FIELD("endTime", DataTypes.TIMESTAMP_LTZ(3)),
    DataTypes.FIELD("startTime", DataTypes.TIMESTAMP_LTZ(3)),
    DataTypes.FIELD("startLon", DataTypes.FLOAT()),
    DataTypes.FIELD("startLat", DataTypes.FLOAT()),
    DataTypes.FIELD("endLon", DataTypes.FLOAT()),
    DataTypes.FIELD("endLat", DataTypes.FLOAT()),
    DataTypes.FIELD("passengerCnt", DataTypes.SMALLINT()),
    DataTypes.FIELD("taxiId", DataTypes.BIGINT()),
    DataTypes.FIELD("driverId", DataTypes.BIGINT())
])

# Register Kafka sources
taxi_rides_columns = ["rideId", "isStart", "endTime", "startTime", "startLon", "startLat", "endLon", "endLat", "passengerCnt", "taxiId", "driverId"]
taxi_rides_data_types = [DataTypes.BIGINT(), DataTypes.STRING(), DataTypes.TIMESTAMP_LTZ(3), DataTypes.TIMESTAMP_LTZ(3), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.INT(), DataTypes.BIGINT(), DataTypes.BIGINT()]
t_env.register_table_source("taxirides", kafka_csv_source('taxirides', kafka_props, taxiRidesSchema, taxi_rides_columns, taxi_rides_data_types))

taxi_fares_columns = ["rideId", "taxiId", "driverId", "startTime", "paymentType", "tip", "tolls", "totalFare"]
taxi_fares_data_types = [DataTypes.BIGINT(), DataTypes.BIGINT(), DataTypes.BIGINT(), DataTypes.TIMESTAMP_LTZ(3), DataTypes.STRING(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.FLOAT()]
t_env.register_table_source("taxifares", kafka_csv_source('taxifares', kafka_props, taxiFaresSchema, taxi_fares_columns, taxi_fares_data_types)) 

# Filtering and Data Cleaning
rides = t_env.from_data_stream(t_env.scan("taxirides")) \
        .filter(col('startLon').between(-74.05, -73.7) & 
                col('startLat').between(40.5, 41.0) &
                col('endLon').between(-74.05, -73.7) & 
                col('endLat').between(40.5, 41.0) &
                col('isStart') == 'END')

fares = t_env.from_data_stream(t_env.scan("taxifares")) 

# Watermarking
rides_wm = rides.assign_timestamps_and_watermarks(
                WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_minutes(30))
                .with_timestamp_assigner(lambda row, ts: row['endTime']))

fares_wm = fares.assign_timestamps_and_watermarks(
                WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_minutes(30))
                .with_timestamp_assigner(lambda row, ts: row['startTime']))  

# Neighborhood Feature Engineering 
nbhds_df = pd.read_json("use-cases/app-testing/ride-selection/flink-ride-selection/nbhd.jsonl", lines=True) 
broadcast_nbhds = t_env.from_pandas(nbhds_df).collect() 
broadcast_var = {row['name']: row['coord'] for row in broadcast_nbhds}
manhattan_bbox = [[-74.0489866963,40.681530375],[-73.8265135518,40.681530375],[-73.8265135518,40.9548628598],[-74.0489866963,40.9548628598],[-74.0489866963,40.681530375]]

def isPointInPath(x, y, poly):
    """check if point x, y is in poly
    poly -- a list of tuples [(x, y), (x, y), ...]"""
    num = len(poly)
    i = 0
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                                  (poly[j][1] - poly[i][1])):
            c = not c
        j = i
    return c

@udf(result_type=DataTypes.STRING())
def find_nbhd(lon, lat):
    if not isPointInPath(lon, lat, manhattan_bbox): 
        return "Other"  # For points outside Manhattan

    for name, poly in broadcast_var.value.items(): 
        if isPointInPath(lon, lat, poly):
            return name  

    return "Other"  # If the point doesn't belong to any defined neighborhood

rides_wm = rides_wm.select(rides_wm['*'], 
                           find_nbhd(rides_wm['startLon'], rides_wm['startLat']).alias('startNbhd'), 
                           find_nbhd(rides_wm['endLon'], rides_wm['endLat']).alias('stopNbhd'))

# Interval join
joined = fares_wm.interval_join(rides_wm) \
                  .where(col('rideId_fares') == col('rideId') &
                         col('endTime') > col('startTime') &
                         col('endTime') <= col('startTime') + lit(2).hours)  \
                  .select(col('rideId'), col('endTime'), col('tip'), col('stopNbhd')) 

# Aggregation
aggregated = joined.window(Tumble.over(lit(30).minutes()).on(col('endTime')).alias('w')) \
                   .group_by(col('w'), col('stopNbhd')) \
                   .select(col('stopNbhd'), expr.avg('tip').alias('avg_tip'))

# Output Sink Configuration
output_dir = 'logs/output'
aggregated.execute_insert('output_csv')  # Configure sink for output_csv table
t_env.execute("Flink Taxi Ride Analysis")