# to run this script: sudo spark/pyspark/bin/spark-submit use-cases/varying-networking-conditions/varying-link-bw/word-count/simulationScripts/latencyScript.py <logDir>

# This file calculates the latency of processing each file by a spark application, using information
# from producer and consumer logs

from turtle import color
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import builtins as p

import time
import sys
import shutil
import os

def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf() 

def plotUtilizationCDF(logDir, files, latency):
    colorLst = ['r','g','b', 'y','k']
    hist_kwargs = {"linewidth": 2,
                  "edgecolor" :'salmon',
                  "alpha": 0.4, 
                  "color":  "w",
                #   "label": "Histogram",
                  "cumulative": True}
    kde_kwargs = {'linewidth': 3,
                  'color': 'r',
                  "alpha": 0.7,
                #   'label':'Kernel Density Estimation Plot',
                  'cumulative': True}

    sns.distplot(latency, hist_kws=hist_kwargs, kde_kws=kde_kwargs)
#     plt.legend(labels=files,  title = "nHosts")
    
    # Add labels
    plt.title('CDF of file latency')
    plt.xlabel('Latency(ms)')
    plt.ylabel('CDF')
    
    plt.savefig(logDir+"/"+"CDF.png",format='png', bbox_inches="tight")

# Some basic spark set up
spark = SparkSession.builder.appName("Latency Script").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")


# Reading the producer and consumer log files into a dataframe each
logDir = sys.argv[1]
producerLog = logDir + '/prod/prod-node1-instance1.log'
consumerLog = logDir + '/cons/cons-node4-instance1.log'

producerDF = spark.read.option('inferSchema', True).option('header', True).text(producerLog)
consumerDF = spark.read.option('inferSchema', True).option('header', True).text(consumerLog)


# Processing to get the data in our desired format

split_result = split("value", "INFO:")
producerDF = producerDF.select(split_result.getItem(0).alias('timestamp'), split_result.getItem(1).alias('value'))

split_result = split("value", "INFO:")
consumerDF = consumerDF.select(split_result.getItem(0).alias('timestamp'), split_result.getItem(1).alias('value'))

# Getting the rows mentioning the file number
producerDF.createOrReplaceTempView('producer')

producerDF = spark.sql("SELECT * FROM producer WHERE value LIKE '%File:%'")

consumerDF.createOrReplaceTempView('consumer')

# consumerDF = spark.sql("SELECT * FROM consumer WHERE value LIKE '%rrrr%'")
consumerDF = spark.sql("SELECT * FROM consumer WHERE value LIKE '%File:%'")

# Getting the number of each file that was sent along with the timestamp

split_result = split("value", "File: ")
producerDF = producerDF.select(col('timestamp').alias('send_time'), split_result.getItem(0).alias('send_message'), \
        split_result.getItem(1).alias('file'))

# split_result = split("value", "rrrr")
split_result = split("value", "File: ")
consumerDF = consumerDF.select(col('timestamp').alias('receive_time'), split_result.getItem(0).alias('message'), \
        split_result.getItem(1).alias('file'))

# We get the first instance of each file in the consumer log

consumerDF.createOrReplaceTempView('cons')

consumerDF = spark.sql("SELECT file, FIRST(receive_time) AS receive_time, FIRST(message) AS receive_message \
        FROM cons GROUP BY file")

# # Now we combine the two dataframes in preparation for calculating the latency

combinedDF = producerDF.join(consumerDF, producerDF.file == consumerDF.file)
# combinedDF.show(101,truncate=False)


# Selecting the desired columns from the combined dataframe

combinedDF = combinedDF.select('cons.file', regexp_replace('send_time', ',', '.').alias('send_time'), \
        regexp_replace('receive_time', ',', '.').alias('receive_time'))


# Calculating the latency and adding it as a new column
# Note that the latency is in the form INTERVAL 'd hh:mm:ss.ms' DAY TO SECOND

# Where 
# d = day
# hh = hours
# mm = minutes
# ss = seconds
# ms = milliseconds

# resultDF = combinedDF.withColumn('latency', \
#         (to_timestamp('receive_time') - to_timestamp('send_time')).cast('string'))

combinedDF = combinedDF.select('file', to_timestamp( col('send_time') ).alias('send_time'), \
        to_timestamp( col('receive_time') ).alias('receive_time') )

# print(combinedDF.columns)
# print(combinedDF.printSchema())
# combinedDF.show(20, truncate = False)

# storing latency in miliseconds
resultDF = combinedDF.select('file',
            ((col('receive_time').cast('double') - col('send_time')\
                .cast('double'))*1000 ).cast('long').alias('latency')
            )

# We display the results

files = [data[0] for data in resultDF.select('file').collect()]
latency = [data[0] for data in resultDF.select('latency').collect()]

# print("files before sorting: ")
# print(*files)
# print("latency before sorting by filenumber: ")
# print(*latency)

# from list of strings to list of integers
res = [eval(i) for i in files]

# sorting both list in ascending order of the file number
# tuple1, tuple2 = zip(*sorted(zip(res, latency)))

tuples = zip(*sorted(zip(res, latency)))
sortedFiles, sortedLatency = [ list(tuple) for tuple in  tuples]
# print("files after sorting: ")
# print(*sortedFiles)

# print("latency after sorting by filenumber: ")
# print(*sortedLatency)
# showing average as a horizontal line
latencySum = p.sum(sortedLatency)
averageLatency = float(latencySum/len(sortedFiles))
print('Average latency: '+str(averageLatency)+' ms')

# showing average latency in the horizontal line
fig = plt.figure()
ax = fig.add_subplot(111)
ax.text(1.02,averageLatency, str(averageLatency),transform=ax.get_yaxis_transform())
ax.axhline(y=averageLatency, color='r', linestyle='-')


plt.xlabel('File ID')
plt.ylabel('Latency in miliseconds')
plt.title('Latency Per File')

# plot X axis values at a interval
plt.xticks(range(0,110,10))
plt.scatter(sortedFiles, sortedLatency)

# print(*files)
# print(*latency)
plt.scatter(files, latency)

plt.savefig(logDir+'/per-file-latency.png')