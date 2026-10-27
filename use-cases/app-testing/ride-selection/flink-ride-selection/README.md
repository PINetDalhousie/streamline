# Ride Selection

In this application, we present a use-case where the taxi driver can yield higher tips using real-time ride selection. We use original data from New York City Taxi and Limyousine Commission \([TLC dataset](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)\) and customize it according to our need. These data contains both geographical and financial information of the ride. Taxi ride data are ingested to the event streaming application. In the Flink applicaiton, stream processing engine consume that data and process it in near real-time. To do that, at first, we clean the data. Then, we introduce stream-stream joining with watermarking between geospatial and financial streams. Later, we then take the leverage of geographic coordinates of Manhattan neighbourhoods only (for simplicity)  to find out the relevant rides. Finally, we take a window of thirty minutes to aggregate the average tip in Manhattan locality. The application will inform the taxi driver which area the driver should choose to get a higher tip.

## Architecture

### Application Chain
![image](https://user-images.githubusercontent.com/6629591/182680217-92a61549-0b9c-4e18-afc9-e5cf32d3b8e9.png)


### Topology
![image](https://user-images.githubusercontent.com/6629591/179554520-5b9c84a3-f479-4df4-8405-bc749feaeaa9.png)



## Queries  
  
    joined = fares_wm.interval_join(rides_wm) \
                  .where(col('rideId_fares') == col('rideId') &
                         col('endTime') > col('startTime') &
                         col('endTime') <= col('startTime') + lit(2).hours)  \
                  .select(col('rideId'), col('endTime'), col('tip'), col('stopNbhd')) 
  
    aggregated = joined.window(Tumble.over(lit(30).minutes()).on(col('endTime')).alias('w')) \
                   .group_by(col('w'), col('stopNbhd')) \
                   .select(col('stopNbhd'), expr.avg('tip').alias('avg_tip'))
  
    fares_wm = fares.assign_timestamps_and_watermarks(
                WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_minutes(30))
                .with_timestamp_assigner(lambda row, ts: row['startTime'])) 
  
## Operations
  
  Selection
  
  Watermarking
  
  Interval join
    
  Windowed grouped aggegation
  
## Input details
1. About data
   - nycTaxiRidesdata.csv: mostly geographical details of the ride
   - nycTaxiFaresdata.csv : ride financial information
2. yamlConfig directory [Check configuration parameters here](/documentation/config-parameters.pdf)
   - broker.yaml : contains broker(s) configuration
   - topicConfiguration.yaml : contains topic(s) configuration
   - producerConfiguration.yaml : contains producer(s) configuration
   - consumerConfiguration.yaml : contains consumer(s) configuration
   - spe.yaml : contains strea processing (Flink) application configuration
3. rideSelection.py: Flink application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations specified as YAML configurations
 5. nbhd.jsonl: contains all Manhattan neighborhoods coordinates one per line.
 
## Running
   
 ```sudo python3 main.py use-cases/app-testing/ride-selection/flink-ride-selection/input.graphml```
