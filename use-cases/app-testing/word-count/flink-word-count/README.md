# Word count

Word count is a standard benchmarking application for stream processing systems. It collects textual data from a stream of files, splits it into words, and stores word fre-quencies into another file. At the end of text split and fre-quency counting of words, results stored to a Kafka topic.

## Architecture

### Application Chain

![image](https://user-images.githubusercontent.com/6629591/185228018-2c9f9701-ff7e-42e0-9df2-d5042b49a8bb.png)


### Topology

![image](https://user-images.githubusercontent.com/6629591/185228142-f6256cf9-4e13-4e1c-a1b6-2c137382ea83.png)


## Queries  

      ds.flat_map(split) \
        .map(lambda i: (i, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda i: i[0]) \
        .reduce(lambda i, j: (i[0], i[1] + j[1])) \
        .map(lambda i: f'{i[0]}: {i[1]}', output_type = Types.STRING())
  
## Operations
  
  Selection
  
  Aggegation
  
## Input details 
1. dataDir: contains textual data files.
2. yamlConfig directory [Check configuration parameters here](/documentation/config-parameters.pdf)
   - <broker>.yaml : contains broker(s) configuration
   - <topicConfiguration>.yaml : contains topic(s) configuration
   - <producerConfiguration>.yaml : contains producer(s) configuration
   - <consumerConfiguration>.yaml : contains consumer(s) configuration
   - <spe>.yaml : contains strea processing (Flink) application configuration
3. wordCount.py: Flink application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations specified as YAML configurations
 
## Runnning 
 
 ```sudo python3 main.py use-cases/app-testing/word-count/flink-word-count/input.graphml``` 



