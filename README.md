# streamline

Tool for fast prototyping of distributed stream processing applications.

The tool was tested on Ubuntu jammy (22.04LTS). It is based on Python 3.8.10 and supports the following tools:
- Apache Kafka 2.13-4.0.0
- RabbitMQ 4.1.0
- Apache Spark 3.5.5
- Apache Flink 2.0.0
- MySQL 8.0.30

<!--- Preliminary versions 
- Apache Kafka 2.13-2.8.0
- RabbitMQ 3.9.13
- Apache Spark 3.2.1
- Apache Flink 1.17.1 -->

## Getting started

1. Clone the repository, then enter into it.

```git clone https://github.com/PINetDalhousie/streamline.git```

```cd streamline```

2. Install dependencies. Our tool depends on the following software:

  - pip3
  - Mininet 2.3.0
  - Networkx 2.5.1
  - Java 11
  - Xterm
  - Kafka-python 2.0.2
  - Matplotlib 3.3.4
  - Seaborn 0.12.1
  - PyYAML 5.3.1
  - Apache Flink 2.0.0
  - PySpark 3.5.5
  - Apache Spark 3.5.5 (optional dependency. Required to facilitate Spark cluster support)

  Most dependencies can be installed using `apt install` and `pip3 install`:
  
  <!-- $ sudo wget -P kafka https://archive.apache.org/dist/kafka/2.8.2/kafka_2.13-2.8.2.tgz && sudo tar -xvf kafka/kafka_2.13-2.8.2.tgz -C kafka/ && sudo cp -R kafka/kafka_2.13-2.8.2/* kafka/ && sudo rm kafka/kafka_2.13-2.8.2.tgz && sudo rm -rf kafka/kafka_2.13-2.8.2 -->
  ```bash
  $ sudo apt install python3-pip mininet default-jdk xterm netcat
  
  $ sudo pip3 install mininet networkx kafka-python matplotlib python-snappy lz4 seaborn pyyaml seaborn

  $ sudo python3 -m pip install --target pyflink apache-flink==2.0.0
  
  $ sudo pip3 install --target spark/pyspark pyspark==3.5.5
  ```
  <!-- $ sudo python3 -m pip install --target pyflink apache-flink==1.17.1 
  $ sudo pip3 install --target spark/pyspark pyspark==3.2.1 -->

  For RabbitMQ support, do the following:
  ```bash
  $ sudo apt install -y rabbitmq-server
  $ sudo python3 -m pip install pika --upgrade
  $ sudo cp config/*.conf /etc/rabbitmq/
  ```

  3. You are ready to go! Should be able to get help using:

  ```sudo python3 main.py -h```
  
  ## Sample command lines
  
  1) Navigate through the ```use-cases/``` directory to explore the diverse applications we tested using streamline.  Details of the applications including the exact data processing pipeline, topology, executed queries, and platform configurations can be found inside respective application directory. Example command to test a streaming data analytics application in a small network: 
  
  ```sudo python3 main.py use-cases/app-testing/document-analytics/input.graphml```
  
  2) Log  production, consumption history and metrics of interest (e.g., bandwidth consumption) automatically for STANDARD producer and consumer. Look over the logs in `logs/output/` directory once the simulation ends.
    
  3) Set a duration for the simulation (OBS.: this is the time the workload will run, not the total simulation time.)

  ```sudo python3 main.py use-cases/disconnection/military-coordination/input.graphml --time 300```

  4) Capture the traffic of all the hosts while testing your application.

  ```sudo python3 main.py use-cases/disconnection/military-coordination/input.graphml --capture-all```

  5) Run event streaming and stream processing engine jointly or individually. Default setup is running event streaming (Apache Kafka) and stream processing engine (Apache Spark) as a sequential pipeline.

  ```sudo python3 main.py use-cases/reproducibility/input.graphml --only-spark 1```

  6) Execute stream processing tasks using a cluster of workers, leveraging the power of Spark standalone cluster(currently, only Spark is supported). The following example demonstrates how to run an application with three worker instances: 

  ```sudo python3 main.py use-cases/reproducibility/networkTrafficAnalysis/input-cluster.graphml --time 300```
  
  7) Explore the streamline supported configuration parameters in ```documentation/config-parameters.pdf```. Setup parameters as you need and quickly test your prototype in a distributed emulated environment.
