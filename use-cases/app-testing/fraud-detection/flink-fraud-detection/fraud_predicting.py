from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, CsvTableSource, CsvTableSink, DataTypes
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer 
from pyflink.ml.lib.feature import VectorAssembler  

import pickle
import sys
import logging

try:
        flinkOutputTo = 'fraudOutput'
        flinkInputFrom = "fraudInput"
        trainedModel = "use-cases/app-testing/fraud-detection/flink-fraud-detection/trainedmodel"

        logging.basicConfig(filename="logs/output/fraudSpark.log",\
        format='%(asctime)s %(levelname)s:%(message)s',\
        level=logging.INFO)
        logging.info("input: "+flinkInputFrom)
        logging.info("output: "+flinkOutputTo)

        # Kafka Configuration 
        kafka_props = {
                'bootstrap.servers': '10.0.0.1:9092', 
                'group.id': 'fraud-predicting-group' 
        }

        # Environment setup
        env = StreamExecutionEnvironment.get_execution_environment()
        settings = EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
        t_env = StreamTableEnvironment.create(env, environment_settings=settings)

        def kafka_csv_source(topic, props, schema, col_names, data_types):
                return CsvTableSource(
                        col_names,
                        data_types,
                        topic,
                        props,
                        "csv" 
                )

        # Schema definition
        fraudCSVSchema = DataTypes.ROW([
                DataTypes.FIELD("step", DataTypes.INT()), 
                DataTypes.FIELD("type", DataTypes.INT()),
                DataTypes.FIELD("amount", DataTypes.FLOAT()),
                DataTypes.FIELD("nameOrig", DataTypes.STRING()),
                DataTypes.FIELD("oldbalanceOrg", DataTypes.FLOAT()),
                DataTypes.FIELD("newbalanceOrig", DataTypes.FLOAT()),
                DataTypes.FIELD("nameDest", DataTypes.STRING()),
                DataTypes.FIELD("oldbalanceDest", DataTypes.FLOAT()),
                DataTypes.FIELD("newbalanceDest", DataTypes.FLOAT()),
                DataTypes.FIELD("isFraud", DataTypes.INT()),
                DataTypes.FIELD("isFlaggedFraud", DataTypes.INT()),
        ])

        # Register Kafka sources
        fraud_csv_columns = ["step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud", "isFlaggedFraud"]
        fraud_csv_data_types = [DataTypes.INT(), DataTypes.INT(),DataTypes.FLOAT(), DataTypes.STRING(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.STRING(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.INT(), DataTypes.INT()]
        t_env.register_table_source("fraudInput", kafka_csv_source(flinkInputFrom, kafka_props, fraudCSVSchema, fraud_csv_columns, fraud_csv_data_types))

        df = t_env.from_data_stream("fraudInput") 

        # Data Transformations 
        df = df.map(lambda row: transform_and_clean_row(row)) \
        .filter(lambda row: row is not None)  

        def load_model(model_path):
                with open(model_path, 'rb') as f:
                        return pickle.load(f)

        loaded_model = load_model(trainedModel) 

        # Prediction
        def predict_fraud(row):
                features = assembler.transform(Vectors.dense(row['features'])).get(0) 
                row['prediction'] = model.predict(features)  
                return row

        df = df.map(predict_fraud)

        # CSV Output Sink
        df.execute_insert(flinkOutputTo)  

        # Execute
        t_env.execute("Flink Fraud Prediction")

except Exception as e:
	logging.error(e)
	sys.exit(1)
