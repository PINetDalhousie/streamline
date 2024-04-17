# Maritime monitoring
This application uses AIS data to determine the types of ships heading to each destination in a give timeframe, as well as the number and names of such ships.

Our aim is to use AIS data to get insights that can be useful for maritime monitoring. We wanted to see if Kafka and Flink can be used to get such insights, especially in real-time. Hence, we developed this application.

We start out by feeding real-time AIS data from a JSON file to a Kafka topic. Next, we have the application read this data from the Kafka topic using Apache Flink. Using this data, the application determines the types of ships heading towards each destination in every minute, along with the names and numbers of such ships. Finally, the application then gets the results of this query, changes it into our required JSON format, and feeds this result to a Kafka topic. Specifying Kafka-data store connector configurations, query result can also be inserted from Kafka topic to external datastore table. We test our data-store connection and data ingestion using MySQL.

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
    filtered_table = table.filter("type == 5").select("timestamp, destination, shiptype, shiptype_text, mmsi")

    result = filtered_table.window(Tumble.over("1.minute").on("timestamp").alias("w")) \
        .group_by("w, destination, shiptype") \
        .select("w.start as start, w.end as end, destination, shiptype, count(mmsi) as numberOfShips, collect(mmsi) as shipIDs")

  
## Operations
    Selection
    Projection
    Windowed aggregation
    Stream to table conversion
    User-defined function

  
## Input details
1. data.json : contains input data
2. yamlConfig directory [Check configuration parameters here](/documentation/config-parameters.pdf)
   - broker.yaml : contains broker(s) configuration
   - topicConfiguration.yaml : contains topic(s) configuration
   - producerConfiguration.yaml : contains producer(s) configuration
   - consumerConfiguration.yaml : contains consumer(s) configuration
   - spe.yaml : contains strea processing (Flink) application configuration
3. maritime.py: Flink application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations specified as YAML configurations

## Running
```sudo python3 main.py use-cases/app-testing/maritime-monitoring/flink-maritime-monitoring input.graphml```