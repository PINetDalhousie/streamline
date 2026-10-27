# Sentiment analysis

In this application, we use python's specialized NLP library 'Textblob' to analyse the subjectivity and objectivity of those tweets. We first connect to Twitter using developer API and store tweets on a specific topic. As part of the pre-processing, we clean the unnecessary details (e.g., links, usernames, hashtags, re-tweets). Data is ingested to Kafka topic and then to Flink for real-time analysis. We imply text classification rules on received data and finally get a score of subjectivity and polarity. Subjectivity will be in the floating range of [0.0,1.0] where 0.0 denotes as very subjective and 1.0 denotes very objective. Polarity varies within [0.0,-1.0]. 

### Textblob
This is a python library supports various operation for Natural language processing (NLP) - parts-of-speech tagging, sentiment analysis, parsing, classification, noun phrase extraction etc. It is built over two python modules – pattern and NLTK. For sentiment analysis, it uses pattern library mainly. For a given text, it matches each word of that text with a dictionary of adjectives and their manual-tagged values and computes average polarity and subjectivity. 

## Architecture

### Application Chain
![image](https://user-images.githubusercontent.com/6629591/179554976-efa59ad7-baa8-44ca-b9cf-560db7c48ade.png)

### Topology
![image](https://user-images.githubusercontent.com/6629591/179555037-35379a7e-6e4e-46dc-a5ae-7f7865e898e0.png)



## Queries  
  
  polarity_detection
  
  subjectivity_detection
  
## Operations
  
  Selection
  
  User-defined function
  
## Input details
1. data.txt : contains input data
2. yamlConfig directory [Check configuration parameters here](/documentation/config-parameters.pdf)
   - broker.yaml : contains broker(s) configuration
   - topicConfiguration.yaml : contains topic(s) configuration
   - producerConfiguration.yaml : contains producer(s) configuration
   - consumerConfiguration.yaml : contains consumer(s) configuration
   - spe.yaml : contains strea processing (Flink) application configuration
3. sentimentAnalysis.py: Flink application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations specified as YAML configurations
     
## Running
   
 ```sudo python3 main.py use-cases/app-testing/sentiment-analysis/flink-sentiment-analysis/input.graphml```
