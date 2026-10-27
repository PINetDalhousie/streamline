from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common.functions import MapFunction
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf
from pyflink.table.window import Tumble
import json
import logging

# Set up logging
logging.basicConfig(filename="logs/output/maritimeFlink.log",\
    format='%(asctime)s %(levelname)s:%(message)s',\
    level=logging.INFO)

try: 
    # Set up the environment
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)

    # Set up the Kafka consumer
    properties = {"bootstrap.servers": "10.0.0.1:9092", "group.id": "test"}
    kafka_source = FlinkKafkaConsumer("maritimeInput", SimpleStringSchema(), properties)

    # Add the source to the environment
    ds = env.add_source(kafka_source)

    # Define a UDF to get the current timestamp
    @udf(result_type=DataTypes.TIMESTAMP(3))
    def current_timestamp():
        from datetime import datetime
        return datetime.now()

    # Convert the DataStream to a Table
    table = t_env.from_data_stream(ds, schema=DataTypes.ROW([
        DataTypes.FIELD("class", DataTypes.STRING()),
        DataTypes.FIELD("device", DataTypes.STRING()),
        DataTypes.FIELD("repeat", DataTypes.STRING()),
        DataTypes.FIELD("mmsi", DataTypes.STRING()),
        DataTypes.FIELD("type", DataTypes.STRING()),
        DataTypes.FIELD("lat", DataTypes.FLOAT()),
        DataTypes.FIELD("lon", DataTypes.FLOAT()),
        DataTypes.FIELD("scaled", DataTypes.BOOLEAN()),
        DataTypes.FIELD("status", DataTypes.STRING()),
        DataTypes.FIELD("status_text", DataTypes.STRING()),
        DataTypes.FIELD("turn", DataTypes.FLOAT()),
        DataTypes.FIELD("speed", DataTypes.FLOAT()),
        DataTypes.FIELD("accuracy", DataTypes.BOOLEAN()),
        DataTypes.FIELD("course", DataTypes.FLOAT()),
        DataTypes.FIELD("heading", DataTypes.INT()),
        DataTypes.FIELD("second", DataTypes.INT()),
        DataTypes.FIELD("manuever", DataTypes.INT()),
        DataTypes.FIELD("raim", DataTypes.BOOLEAN()),
        DataTypes.FIELD("radio", DataTypes.INT()),
        DataTypes.FIELD("reserved", DataTypes.BOOLEAN()),
        DataTypes.FIELD("regional", DataTypes.INT()),
        DataTypes.FIELD("cs", DataTypes.BOOLEAN()),
        DataTypes.FIELD("display", DataTypes.BOOLEAN()),
        DataTypes.FIELD("dsc", DataTypes.BOOLEAN()),
        DataTypes.FIELD("band", DataTypes.BOOLEAN()),
        DataTypes.FIELD("msg22", DataTypes.BOOLEAN()),
        DataTypes.FIELD("imo", DataTypes.INT()),
        DataTypes.FIELD("ais_version", DataTypes.INT()),
        DataTypes.FIELD("callsign", DataTypes.STRING()),
        DataTypes.FIELD("shipname", DataTypes.STRING()),
        DataTypes.FIELD("shiptype", DataTypes.INT()),
        DataTypes.FIELD("shiptype_text", DataTypes.STRING()),
        DataTypes.FIELD("to_bow", DataTypes.INT()),
        DataTypes.FIELD("to_stern", DataTypes.INT()),
        DataTypes.FIELD("to_port", DataTypes.INT()),
        DataTypes.FIELD("to_starboard", DataTypes.INT()),
        DataTypes.FIELD("epfd", DataTypes.INT()),
        DataTypes.FIELD("epfd_text", DataTypes.STRING()),
        DataTypes.FIELD("eta", DataTypes.STRING()),
        DataTypes.FIELD("draught", DataTypes.FLOAT()),
        DataTypes.FIELD("destination", DataTypes.STRING()),
        DataTypes.FIELD("dte", DataTypes.BOOLEAN()),
        DataTypes.FIELD("aid_type", DataTypes.INT()),
        DataTypes.FIELD("aid_type_text", DataTypes.STRING()),
        DataTypes.FIELD("name", DataTypes.STRING()),
        DataTypes.FIELD("off_position", DataTypes.BOOLEAN()),
        DataTypes.FIELD("virtual_aid", DataTypes.BOOLEAN())
    ]))

    # Register the UDF
    t_env.create_temporary_system_function("current_timestamp", current_timestamp)

    # Add a column with the current timestamp
    table = table.select("* , current_timestamp() as timestamp")

    # Filter the table
    filtered_table = table.filter("type == 5").select("timestamp, destination, shiptype, shiptype_text, mmsi")

    # Group by and aggregate
    result = filtered_table.window(Tumble.over("1.minute").on("timestamp").alias("w")) \
        .group_by("w, destination, shiptype") \
        .select("w.start as start, w.end as end, destination, shiptype, count(mmsi) as numberOfShips, collect(mmsi) as shipIDs")

    # Convert the result to a DataStream
    result_ds = t_env.to_append_stream(result, Types.ROW([Types.SQL_TIMESTAMP(), Types.SQL_TIMESTAMP(), Types.STRING(), Types.STRING(), Types.LONG(), Types.LIST(Types.STRING())]))

    # Define a function to convert the stream to JSON
    @udf(input_types=[Types.STRING(), Types.STRING(), Types.LONG(), Types.LIST(Types.STRING())], result_type=Types.STRING())
    def to_json(start, end, destination, shiptype, numberOfShips, shipIDs):
        return json.dumps({
            "start": start,
            "end": end,
            "destination": destination,
            "shiptype": shiptype,
            "numberOfShips": numberOfShips,
            "shipIDs": shipIDs
        })

    # Apply the function to the stream
    json_ds = result_ds.map(lambda row: to_json(*row))

    # Set up the Kafka producer
    kafka_sink = FlinkKafkaProducer("maritimeOutput", SimpleStringSchema(), properties)

    # Add the sink to the environment
    json_ds.add_sink(kafka_sink)

    # Execute the job
    env.execute("Maritime Flink Job")

except Exception as e:
    logging.error(f"Error occurred: {e}")