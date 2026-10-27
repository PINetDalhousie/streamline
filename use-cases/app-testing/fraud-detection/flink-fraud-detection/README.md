# Finanncial fraud detection

This application trains a machine learning model on a portion of our fraud detection dataset, then has the model make predictions on the portion of the dataset streamed from kafka.

We start off by creating two files. In the first file, we create a dataframe by loading a csv file containing a portion of our dataset. Then, after performing some preprocessing (such as removing unnecessary columns), we train a Linear SVM Model on the csv dataframe. We save this model in a directory. Then, in the other file, we load the trained model and have it make predictions on the streaming dataframe. The result of this prediction is stored in csv files on the device or in a kafka topic.

## Architecture

### Application Chain
![image](https://user-images.githubusercontent.com/6629591/184164122-a17cf4e4-6adf-4990-aca9-21a7d76ea110.png)

### Topology
![image](https://user-images.githubusercontent.com/6629591/184164321-bf5a49fb-a657-46d4-a4b3-88ed6c81172b.png)

## Queries

  df = df.map(lambda row: transform_and_clean_row(row)) \
        .filter(lambda row: row is not None)  


### Dataset

We used a fraud detection dataset from Kaggle https://www.kaggle.com/datasets/ealaxi/paysim1

We downloaded the csv file containing this dataset. After that, we manually split the csv file into 2 files. We did this as follows:

1 - From the original file, we copied the rows starting from the step value of 718 till the end of the file and pasted this part into a new csv file (testing.csv).

2 - We removed these copied rows from the original file, and we used the edited original file for the dataframe used for training our model(training.csv). 

### Machine Learning Model

We used pyflink.ml library for implementing the machine learning model.

We used Linear SVM. Amongst the other classification models we were considering, we got the impression that this one was not used often. As a result, we tried to test this model. As it made decent predictions, we decided to use this model.

A machine learning project typically involves steps like data preprocessing, feature extraction, model fitting and evaluating results. We need to perform a lot of transformations on the data in sequence. A pipeline allows us to maintain the data flow of all the relevant transformations that are required to reach the end result.

Transformers convert one dataframe into another either by updating the current values of a particular column (like converting categorical columns to numeric) or mapping it to some other values by using a defined logic.

An Estimator implements the fit() method on a dataframe and produces a model. For example, LinearSVC is an Estimator that trains a classification model when we call the fit() method.

To combine all feature data and separate 'label' data in a dataset, we use VectorAssembler.

### Inference
  
For the inference part, we just need to pass the unlabelled test data through the pipeline and it will predict accordingly to the trained model.
  
## Input details
1. About data
   - training.csv : for large file size, not added in this repository 
   - testing.csv : data to test the trained model
2. yamlConfig directory [Check configuration parameters here](/documentation/config-parameters.pdf)
   - broker.yaml : contains broker(s) configuration
   - topicConfiguration.yaml : contains topic(s) configuration
   - producerConfiguration.yaml : contains producer(s) configuration
   - consumerConfiguration.yaml : contains consumer(s) configuration
   - spe.yaml : contains strea processing (Flink) application configuration
3. Configuration
   - input_only_flink.graphml: at first, run this to train the model
   - input.graphml:
     - contains topology description
       - node details (switch, host)
       - edge details (bandwidth, latency, source port, destination port)
     - contains component(s) configurations specified as YAML configurations
4. Applications
   - fraud_detection.py : Flink application to train the model 
   - fraud_predicting.py : Flink application to detect financial frauds

5. trainedmodel: directory to store the trained model after running the fraud_detection.py script


## Running

As the training data is almost 307MB, didn't upload it as part of this project repository.

To train the model:
 ```sudo python3 main.py use-cases/app-testing/fraud-detection/flink-fraud-detection/input_only_flink.graphml --only-flink 1```

 To predict on testing data:
  ```sudo python3 main.py use-cases/app-testing/fraud-detection/flink-fraud-detection/input.graphml```
