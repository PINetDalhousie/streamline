# Maritime monitoring
This application uses AIS data to determine the types of ships heading to each destination in a give timeframe, as well as the number and names of such ships.

Our aim is to use AIS data to get insights that can be useful for maritime monitoring. We wanted to see if Kafka and Spark Structured Streaming can be used to get such insights, especially in real-time. Hence, we developed this application.

We start out by feeding real-time AIS data from a JSON file to a Kafka topic. Next, we have the application read this data from the Kafka topic using Spark Structured Streaming. Using this data, the application determines the types of ships heading towards each destination in every minute, along with the names and numbers of such ships. Finally, the application then gets the results of this query, changes it into our required JSON format, and feeds this result to a Kafka topic. Specifying Kafka-data store connector configurations, query result can also be inserted from Kafka topic to external datastore table. We test our data-store connection and data ingestion using MySQL.

## Dataset
Our dataset is a collection of records obtained by collecting live AIS data. This is live data broadcast from ships.

The ships send messages of various types, e.g., message type 3 contains latitutde and longitude information, message type 5 contains ship names, destinations etc.

For our application, we used messages of type 5, which contained information including ship types, ship names, and destinations.

To know more about the dataset, you can explore this excellent resource on AIS data which contains data under Norwegian license for public data (NLOD) made available by the Geological Survey of Norway (NGU): https://www.kystverket.no/en/navigation-and-monitoring/ais/access-to-ais-data/

We obtained the JSON file with the following command

nc 153.44.253.27 5631 | gpsdecode >> data.json

We let this command run for 3 minutes. After that, we opened data.json and deleted the last line as it was an incomplete json record.

## Architecture

### Application Chain
![image](https://user-images.githubusercontent.com/6629591/183961868-de56360c-9dd3-4ccf-96ce-9d7145cdec28.png)

### Topology
![image](https://user-images.githubusercontent.com/6629591/184164640-4bc89443-258c-430a-a14b-317001d3a818.png)



## Queries  
    vessel = vessel.filter( col("type") == 5).select("timestamp", "destination", "shiptype","shiptype_text", "mmsi")

    query = vessel.groupBy(window("timestamp", "1 minute"), "destination", "shiptype")\
            .agg(approx_count_distinct("mmsi").alias("numberOfShips"),\
            collect_set("mmsi").alias("shipIDs"))

  
## Operations
    Selection
    Projection
    Windowed aggregation
    Foreach implementation

  
## Input details
1. data.json : contains input data
2. topicConfiguration.yaml :
   - contains topic configurations
     - specify topic name ('topicName')
     - specify broker ID to initiate this topic ('topicBroker')
     - number of partition(s) in this topic ('topicPartition')
     - number of replica(s) in this topic ('topicReplica')
3. maritime.py : Spark SS application
<!-- 4. maritime-mysql-bulk-sink.properties: contains detailed MySQL configurations and topic name where MySQL will connect to. -->
<!-- 5. Kafka-MySQL-user manual.pdf: Configurations manual for setting up Kafka-MySQL connection. -->
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations 
     - topicConfig : path to the topic configuration file
     - zookeeper : 1 = hostnode contains a zookeeper instance
     - broker : 1 = hostnode contains a zookeeper instance
     - producerType: producer type can be SFST/MFMT/ELTT/CUSTOM; SFST denotes from Single File to Single Topic. ELTT is defined when Each line To Topic i.e. each line of the file is produced to the topic as a single message. For SFST/MFMT/ELTT, a standard producer will work be default.Provided that the user has his own producer, he can use it by specifying CUSTOM in the producerType and give the relative path as input in producerType attribute as a pair of producerType,producerFilePath.
     - producerConfig: specified in producerConfiguration.yaml
          for SFST/ELTT, user needs to specify filePath, name of the topic to produce, number of files and number of producer instances in this node. For CUSTOM producer type, only producer script path and number of producer instances on this node are the two required parameters to specify.
     - consumerType: consumer type can be STANDARD/CUSTOM; To use standard consumer, specify 'STANDARD'. Provided that the user has his own consumer, he can use it by specifying CUSTOM in the consumerType and give the relative path as input in producerType attribute as a pair like CUSTOM,producerFilePath
     - consumerConfig: each consumer configuration is specified in ''consumerConfiguration<HostID>.yaml' file. In the YAML file, 
         - for STNDARD consumer, specify the topic name where the consumer will consumer from and number of consumer instances in this node.
         - for CUSTOM consumer, specify the consumer script path and number of consumer instances in this node.
     - sparkConfig: sparkConfig will contain the spark application path and output sink. Output sink can be kafka topic/a file directory.
     - storeConfig: contains the file path of the data store configuration.

## Running
```sudo python3 main.py use-cases/app-testing/maritime-monitoring/input.graphml```