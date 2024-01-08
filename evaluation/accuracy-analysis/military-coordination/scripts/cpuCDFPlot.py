# example command: sudo python3 evaluation/accuracy-analysis/military-coordination/scripts/cpuCDFPlot.py --log-dir evaluation/accuracy-analysis/military-coordination/logs --host-list 30,1000,2000,3000,4000
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


def plotUtilizationCDF(utilz, logDir, counter, hostList, plotChoice='CPU'):
    colorLst = ['r','g','b', 'y','k']
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
    y = [i+" msg/s" for i in hostList]
    plt.legend(labels=y, loc="lower right", frameon=False, fontsize=16)
    
    # Add labels
    #plt.title('CDF of '+plotChoice+' utilization')
    plt.xlabel(plotChoice+' utilization(%)', labelpad=9, fontsize=20, fontweight='bold')
    plt.ylabel('CDF', labelpad=9, fontsize=20, fontweight='bold')
    
    ax = plt.gca()

    ax.set_xticks(np.arange(0, 101, step=20))
    ax.xaxis.set_tick_params(labelsize=16)
    #ax.set_yticks(np.arange(1.0, 2.1, step=0.25))
    ax.yaxis.set_tick_params(labelsize=16)
    
    plt.xlim((0, 101))
    
    plt.savefig("evaluation/accuracy-analysis/military-coordination/plots/"+"cdf-"+plotChoice+"-util.pdf", format='pdf', bbox_inches="tight")


# taking log-directory and comma separated list of hosts
parser = argparse.ArgumentParser(description='Script for visualizing peak CPU and peak memory utilisation.')
parser.add_argument('--log-dir', dest='logDir', type=str, help='Log directory of cpu and memory usage')
parser.add_argument('--host-list', dest='hostStr', type=str, help='Comma separated list of hostnodes')

args = parser.parse_args()
logDir = args.logDir
hostStr = args.hostStr
hostList = hostStr.split(',')

for index, item in enumerate(hostList):
    # measure CPU usage for all hosts
    with open(logDir+'/mRate-'+item+'/cpu-mem/'+'mRate-'+item+'-cpu.log') as cpuFP:
        cpuLst = [float(x) for x in cpuFP.read().split()]
        # print('CPU usage for '+item+' hostnodes: ')
        # print(cpuLst)

        plotUtilizationCDF(cpuLst, logDir, index, hostList, 'CPU')
        
        
        
        
        
        
        
        
        
        
        