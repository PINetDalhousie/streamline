from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, DataTypes, CsvTableSource, CsvTableSink, expressions as expr
from pyflink.ml.lib.classification import LinearSVC 
from pyflink.ml.lib.feature import VectorAssembler 
from pyflink.ml.core.linalg import Vectors, DenseVector

# Schema definition
schema = DataTypes.ROW([
    DataTypes.FIELD("step", DataTypes.INT()),
    DataTypes.FIELD("type", DataTypes.STRING()),
    DataTypes.FIELD("amount", DataTypes.DOUBLE()),
    DataTypes.FIELD("nameOrig", DataTypes.STRING()),
    DataTypes.FIELD("oldbalanceOrg", DataTypes.DOUBLE()),
    DataTypes.FIELD("newbalanceOrig", DataTypes.DOUBLE()),
    DataTypes.FIELD("nameDest", DataTypes.STRING()),
    DataTypes.FIELD("oldbalanceDest", DataTypes.DOUBLE()),
    DataTypes.FIELD("newbalanceDest", DataTypes.DOUBLE()),
    DataTypes.FIELD("isFraud", DataTypes.INT()),
    DataTypes.FIELD("isFlaggedFraud", DataTypes.INT())
])

flinkOutputTo = 'use-cases/app-testing/fraud-detection/flink-fraud-detection/trainedmodel'

# CSV source setup
source_descriptor = CsvTableSource(
     csv_file_path="use-cases/app-testing/fraud-detection/flink-fraud-detection/training.csv",
     csv_field_delimiter=",",                                
     csv_format_options={'ignore_first_line': False},
     field_types=schema.get_field_types(),
     field_names=schema.get_field_names()
)

t_env.register_table_source("fraud_data", source_descriptor)
df = t_env.from_data_stream("fraud_data")

# Drop columns
df = df.drop("isFlaggedFraud", "step")
columnsToSanitize = ["isFraud","amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]

# Cast columns to double
for column in columnsToSanitize:
    df = df.select(df[column].cast(DataTypes.DOUBLE()))

# Filter for frauds and not frauds
fraud = df.filter(df.isFraud == 1)
not_fraud = df.filter(df.isFraud == 0)

# Downsample not frauds
not_fraud = not_fraud.sample(False, 0.01, seed = 123)

# Union frauds and not frauds
df = not_fraud.union(fraud)

# Feature Engineering
assembler = VectorAssembler(inputCols = ['amount','oldbalanceOrg', 'newbalanceOrig'\
        , 'oldbalanceDest', 'newbalanceDest'], outputCol = 'features')
df = assembler.transform(df)

# Modeling with FlinkML
model = LinearSVC()

def transform_for_training(row):
    return row['isFraud'], Vectors.dense(row['features']) 

training_data = df.map(transform_for_training)
model.fit(training_data) 
model.save(flinkOutputTo)

