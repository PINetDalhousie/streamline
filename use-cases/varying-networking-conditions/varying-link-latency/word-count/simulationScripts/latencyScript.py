# to run this script: sudo spark/pyspark/bin/spark-submit use-cases/varying-networking-conditions/varying-link-latency/word-count/simulationScripts/latencyScript.py <logDir>

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

# producerLog = logDir + '/prod-node1-instance1.log'
# consumerLog = logDir + '/cons-node4-instance1.log'


producerDF = spark.read.option('inferSchema', True).option('header', True).text(producerLog)
consumerDF = spark.read.option('inferSchema', True).option('header', True).text(consumerLog)

# Processing to get the data in our desired format
split_result = split("value", "INFO:")
producerDF = producerDF.select(split_result.getItem(0).alias('timestamp'), split_result.getItem(1).alias('value'))

split_result = split("value", "INFO:")
consumerDF = consumerDF.select(split_result.getItem(0).alias('timestamp'), split_result.getItem(1).alias('value'))

# Getting the rows mentioning the file number
producerDF.createOrReplaceTempView('producer')

producerDF = spark.sql("SELECT * FROM producer WHERE value LIKE '%File has been sent%'")

consumerDF.createOrReplaceTempView('consumer')

# consumerDF = spark.sql("SELECT * FROM consumer WHERE value LIKE '%rrrr%'")
consumerDF = spark.sql("SELECT * FROM consumer WHERE value RLIKE 'Topic:\\s*(.*?)\\s*File:'")

# Getting the number of each file that was sent along with the timestamp

# split_result = split("value", "File:")
# producerDF = producerDF.select(col('timestamp').alias('send_time'), split_result.getItem(0).alias('send_message'), \
#         split_result.getItem(1).alias('file'))
producerDF = producerDF.select(
    col('timestamp').alias('send_time'),
    regexp_extract('value', r'Topic: (.*?);', 1).alias('topic'),
    regexp_extract('value', r'File: (\d+)', 1).alias('file')
)
# producerDF.show(5,truncate=False)

# split_result = split("value", "rrrr")
# split_result = split("value", " Topic:\\s*(.*?)\\s*File: ")
# consumerDF = consumerDF.select(col('timestamp').alias('receive_time'), split_result.getItem(0).alias('message'), \
#         split_result.getItem(1).alias('file'))

consumerDF = consumerDF.select(
    col('timestamp').alias('receive_time'),
    regexp_extract('value', r'FileID \d+; Message: (.*?) Topic:', 1).alias('message'),
    regexp_extract('value', r'Topic: (.*?) File:', 1).alias('topic'),
    regexp_extract('value', r'File: (\d+)', 1).alias('file')
)
# We get the first instance of each file in the consumer log

consumerDF.createOrReplaceTempView('cons')
consumerDF = spark.sql("SELECT file, FIRST(receive_time) AS receive_time, FIRST(message) AS receive_message \
        FROM cons GROUP BY file, topic")

# consumerDF.show(101,truncate=False)

# # Now we combine the two dataframes in preparation for calculating the latency
combinedDF = producerDF.join(consumerDF, producerDF.file == consumerDF.file)
# combinedDF.show(5,truncate=False)

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

# Displaying each dataframe
# print(producerDF.columns)
# producerDF.show(20, truncate = False)

# print(consumerDF.columns)
# consumerDF.show(20000, truncate = False)

# print(combinedDF.columns)
# print(combinedDF.printSchema())
# combinedDF.show(20000, truncate = False)

# print(resultDF.printSchema())
# print(resultDF.columns)
# resultDF.show(200, truncate = False)

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

# plt.axhline(y=averageLatency, color='r', linestyle='-')
# plt.xlabel('File ID')
# plt.ylabel('Latency in miliseconds')
# plt.title('Latency Per File')

# # plot X axis values at a interval
# plt.xticks(range(0,1005,100))
# plt.scatter(sortedFiles, sortedLatency)

# print(*files)
# print(*latency)
# plt.scatter(files, latency)

# plotLink = 'varying-H2-S-link-only-noSleep'
# plotLinkLatency = '100ms'
# #plt.show()
# plt.savefig(logDir+'/'+ plotLinkLatency +'-latency.png')

# clearExistingPlot()

# # Plot CDF of latency
# plotUtilizationCDF(logDir, sortedFiles, sortedLatency)

# time.sleep(5)

# #copying logs and latency plot from logs to latencyPlots directory

# # path to source directory
# src_dir = logDir
 
# # path to destination directory
# dest_dir = '/home/monzurul/Desktop/amnis-data-sync/use-cases/varying-networking-conditions/varying-link-latency/word-count/simulationResults/'+\
#                 plotLink+'/'+plotLinkLatency+'/'
# os.makedirs(dest_dir)
 
# #shutil.copytree(src_dir, dest_dir)

# shutil.copy(logDir+'/prod-1.log', dest_dir)
# shutil.copy(logDir+'/cons4.log', dest_dir)
# shutil.copy(logDir+'/'+ plotLinkLatency +'-latency.png', dest_dir)