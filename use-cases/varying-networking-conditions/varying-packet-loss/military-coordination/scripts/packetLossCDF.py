# example command: sudo python3 use-cases/varying-networking-conditions/varying-packet-loss/military-coordination/scripts/packetLossCDF.py --log-dir use-cases/varying-networking-conditions/varying-packet-loss/military-coordination/logs --scenario-list 0,1,2,3,4,5
#!/bin/usr/python3

import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import statistics
import numpy as np

def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf() 


def plotUtilizationCDF(utilz, logDir, counter, hostList, plotChoice='Latency'):
    colorLst = ['r','g','b', 'y','k','m']
    hist_kwargs = {"linewidth": 2,
                  "edgecolor" :'salmon',
                  "alpha": 0.4, 
                  "color":  "w",
                #   "label": "Histogram",
                  "cumulative": True}
    kde_kwargs = {'linewidth': 3,
                  'color': colorLst[counter],
                  "alpha": 0.7,
                #   'label':'Kernel Density Estimation Plot',
                  'cumulative': True}

    #sns.distplot(utilz, hist_kws=hist_kwargs, kde_kws=kde_kwargs).set(xlim=(0,100))
    sns.ecdfplot(utilz, linewidth=3.0)
    y = [i+" % packet loss" for i in hostList]
    plt.legend(labels=y, loc="lower right", frameon=False, fontsize=16)
    
    # Add labels
    #plt.title('CDF of '+plotChoice+' utilization')
    plt.xlabel(plotChoice, labelpad=9, fontsize=20, fontweight='bold')
    plt.ylabel('CDF', labelpad=9, fontsize=20, fontweight='bold')
    
    ax = plt.gca()

    ax.set_xticks(np.arange(0, 201, step=50))
    ax.xaxis.set_tick_params(labelsize=16)
    #ax.set_yticks(np.arange(1.0, 2.1, step=0.25))
    ax.yaxis.set_tick_params(labelsize=16)
    
    plt.xlim((0, 201))
    
    logDirPlots = logDir.replace('logs','plots')
    plt.savefig(logDirPlots+"/packetLoss-latency-CDF", bbox_inches="tight")


# taking log-directory and comma separated list of hosts
parser = argparse.ArgumentParser(description='Script for visualizing peak CPU and peak memory utilisation.')
parser.add_argument('--log-dir', dest='logDir', type=str, help='Log directory of cpu and memory usage')
parser.add_argument('--scenario-list', dest='scenarioStr', type=str, help='Comma separated list of scenarios')

args = parser.parse_args()
logDir = args.logDir
scenarioStr = args.scenarioStr
scenarioList = scenarioStr.split(',')

latencyList = []

# measure latency usage for all scenarios
for index, item in enumerate(scenarioList):    
    with open(logDir+'/scenario-'+item+'/latency-log.txt') as latencyFP:
        for lineNum, line in enumerate(latencyFP,1):         #to get the line number
            if "Latency of this message: " in line:
                latencySplit = line.split("Latency of this message: 0:")
                latencyList.append(float(latencySplit[1][0:2])*60.0 + float(latencySplit[1][3:5]))
        # print('Latency for scenario-'+item+': ')
        # print(latencyList)

        plotUtilizationCDF(latencyList, logDir, index, scenarioList, 'End-to-end latency (s)')