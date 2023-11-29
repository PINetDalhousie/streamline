# command: sudo python3 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/combinedThroughput-by-varying-BW-only.py --log-dir use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs --scenario-list 6,4,5
#!/usr/bin/python3

import os
import logging

import argparse

import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import numpy as np

interval = 5
inputBarDraw = 0

font = FontProperties()
font.set_family('serif')
font.set_name('Liberation Serif')
font.set_size(12)

matplotlib.rcParams['pdf.fonttype'] = 42   # for ACM submission
matplotlib.rcParams['ps.fonttype'] = 42
    
def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf()    
    
def processMessageInput():
    mSizeParams = args.mSizeString.split(',')
    msgSize = 0
    if mSizeParams[0] == 'fixed':
        msgSize = int(mSizeParams[1])
    elif mSizeParams[0] == 'gaussian':
        msgSize = int(gauss(float(mSizeParams[1]), float(mSizeParams[2])))

    if msgSize < 1:
        msgSize = 1
    
    return msgSize

#to get bandwidth list for a specific port in a specific switch
def getStatsValue(switch,portNumber, portFlag):
    count=0
    dataList = []
    bandwidth =  [0]
    txFlag = 0
    maxBandwidth = -1.0
    
    with open(logDirectory+'bandwidth-log'+str(switch)+'.txt') as f:
        
        for line in f:
            if portNumber >= 10:
                spaces = " "
            else:
                spaces = "  "
            if "port"+spaces+str(portNumber)+":" in line: 
                
                if portFlag == 'tx pkts':
                    line = f.readline()
                    
                elif portFlag == 'tx bytes':
                    line = f.readline()
                    txFlag = 1           
                if txFlag == 1:
                    newPortFlag = "bytes"
                    data = line.split(newPortFlag+"=")
                else:
                    data = line.split(portFlag+"=")

                data = data[1].split(",")
                dataList.append(int(data[0]))
                if count>0: 
                    individualBandwidth = (dataList[count]-dataList[count-1])/interval
                    bandwidth.append(individualBandwidth)
                    if individualBandwidth > maxBandwidth:
                        maxBandwidth = individualBandwidth
                count+=1

    return bandwidth,count, maxBandwidth
         
# aggregated plot for all switches
def aggregatedPlot(portFlag,x,y, yLeaderLess, yLabel, msgSize, countX, 
		label, color, ls, lw):      
    plt.plot(x,y, label = label, color=color, linestyle=ls, linewidth=lw)
    
    plt.xlabel('Time (s)', fontsize=22, fontweight='bold', labelpad=10)
    plt.ylabel(yLabel, fontsize=22, fontweight='bold', labelpad=10)
    
    plt.xlim([0,400])
    # plt.ylim([0, 10])
    
    plt.xticks(np.arange(0,401, step=100))
    # plt.yticks(np.arange(0,10.1, step=2))
    
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(labelsize=18, pad=5)
    ax.yaxis.set_tick_params(labelsize=18, pad=5)

    plt.legend(frameon=True, loc='lower right', fontsize=12, borderpad=0.5, labelspacing=0.5)
    

#checking input vs output to measure control traffic overhead
def overheadCheckPlot(portFlag, msgSize,scenario, label, color, ls, lw, cap):    
    allBandwidth = []
    countX = 0
    
    portParams = args.switchPorts.split(',')
    for ports in portParams:
        portId, switchId = parseInput(ports)
    
        bandwidth, occurrence, maxBandwidth = getStatsValue(switchId,portId, portFlag)
        
        if countX == 0:
            countX = occurrence
        
        if len(bandwidth)<countX:
            for k in range(countX-len(bandwidth)):
                bandwidth.append(0)                    #filling with 0's to match up the length
            
        allBandwidth.append(bandwidth)

    bandwidthSum = []
    bandwidthSumLeaderLess = []

    for i in range(countX):
        valWithLeader = 0
        for j in range(args.switches):
            valWithLeader = valWithLeader+allBandwidth[j][i]

        bandwidthSum.append(valWithLeader)        
    timeList = list(range(0,countX*interval,interval))
    
    #Discard warm-up phase data for rMQ
    if scenario == 0:
        #print(len(timeList))
        timeList = timeList[30:]
        timeList = [x-120 for x in timeList]
        #print(len(timeList))
        bandwidthSum = bandwidthSum[30:]
        #print(len(bandwidthSum))
    	    
    if portFlag=="rx pkts" or portFlag=="tx pkts":
        aggregatedPlot(portFlag,timeList, bandwidthSum, bandwidthSumLeaderLess, "Throughput (pkts/s)", msgSize, countX, label, ls, lw)
    else:
        newBandwidthSum = [x / 1000000 for x in bandwidthSum]
        
        #Discard outliers
        #print(len(newBandwidthSum))
        newBandwidthSum = [x for x in newBandwidthSum if x < cap]
        #print(newBandwidthSum)
        #print(len(newBandwidthSum))
        timeList = timeList[:len(newBandwidthSum)]

        newBandwidthSumLeaderLess = [x / 1000000 for x in bandwidthSumLeaderLess]
        aggregatedPlot(portFlag,timeList, newBandwidthSum, newBandwidthSumLeaderLess, "Throughput (Mbytes/s)", msgSize, countX, label, color, ls, lw)    
    
    # if portFlag=="bytes" and scenario==2:
    #     #Change legend order
    #     # handles, labels = plt.gca().get_legend_handles_labels()
    #     # order = [0,2,1]
    #     # plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order], frameon=False, loc='upper left', fontsize=18)

    
    #     # plt.savefig("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/plots/combinedThroughput.pdf", format='pdf', bbox_inches="tight")
    #     plt.savefig("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/plots/combinedThroughput", bbox_inches="tight")
    # else:    
    #     plt.savefig(logDirctory+args.portType+" aggregated "+portFlag+"("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)",bbox_inches="tight")         

#for aggregated plot of all host entry ports
def plotAggregatedBandwidth(scenario, label, color, ls, lw, cap):   
    msgSize = processMessageInput()
    overheadCheckPlot("bytes", msgSize, scenario, label, color, ls, lw, cap)
       
#parsing the sigle port        
def parseInput(portSwitchId):
    portParams = portSwitchId.split('-')
    switchId = portParams[0].split('S')[1]
    portId = portParams[1].split('P')[1]

    return int(portId), int(switchId)
    
# if __name__ == '__main__': 
parser = argparse.ArgumentParser(description='Script for plotting individual port log.')
parser.add_argument('--number-of-switches', dest='switches', type=int, default=10,
                help='Number of switches')
parser.add_argument('--switch-ports', dest='switchPorts', type=str, default='S1-P1,S2-P1,S3-P1,S4-P1,S5-P1,S6-P1,S7-P1,S8-P1,S9-P1,S10-P1', help='Plot bandwidth vs time in a port wise and aggregated manner')
parser.add_argument('--port-type', dest='portType', default="access-port", type=str, help='Plot bandwidth for access/trunc ports')
parser.add_argument('--message-size', dest='mSizeString', type=str, default='fixed,10', help='Message size distribution (fixed, gaussian)')
parser.add_argument('--message-rate', dest='mRate', type=float, default=1000.0, help='Message rate in msgs/second')
parser.add_argument('--ntopics', dest='nTopics', type=int, default=2, help='Number of topics')
parser.add_argument('--replication', dest='replication', type=int, default=10, help='Replication factor')
parser.add_argument('--nzk', dest='nZk', type=int, default=0, help='Kafka/Kraft')
parser.add_argument('--log-dir', dest='logDir', type=str, default='use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/scenario-1', help='Producer log directory')
parser.add_argument('--scenario-list', dest='scenarioStr', type=str, help='Comma separated list of scenarios')

args = parser.parse_args()

logDirectory = args.logDir
scenarioStr = args.scenarioStr
scenarioList = scenarioStr.split(',')
linkBWList = [10, 20, 1000]


clearExistingPlot()
colorLst = ['r','g','b', 'y','k','m']
for index, item in enumerate(scenarioList):
    logDirectory = args.logDir + "/scenario-"+str(item) + "/bandwidth/"
    # ls can be solid or dashed 
    plotAggregatedBandwidth(scenario=linkBWList[index], label=str(linkBWList[index])+" Mbps", color=colorLst[index], ls='solid', lw=3.0, cap=100.0)      #for aggregated plot    


filePath= args.logDir.replace('logs','plots')+"/"+ "newCombinedThroughput"
plt.savefig(filePath+".pdf", format='pdf', bbox_inches="tight")