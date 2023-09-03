## Flink Cluster
Note that this works on standalone mode only and not over mininet
Using a flink cluster increases paralellism and fault tolerance.

See the google doc for more information. 

### TO RUN: 
```
    "path to pyflink"/pyflink/bin/jobmanager.sh start-foreground
    "path to pyflink"/pyflink/bin/taskmanager.sh start-foreground 
    "path to pyflink"/pyflink/bin/taskmanager.sh start-foreground 
    "path to pyflink"/pyflink/bin/flink run -m localhost:8081 --python word_count_flink.py 
```


