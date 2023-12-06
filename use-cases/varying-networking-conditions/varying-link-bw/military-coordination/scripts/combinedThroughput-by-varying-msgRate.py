# command: sudo python3 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/combinedThroughput-by-varying-msgRate.py --log-dir use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs --link-bw 20 --scenario-list 300,500,600
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

# plot input data rate in one horizontal line for all/individual host ports
def plotInputDataRate(msgSize, mRate, countX, switches):
    dataRate = msgSize * mRate * switches
    dataRateList = [dataRate] * countX
    return dataRateList

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

#drawing single plot for a single flag of each port for one switch           
def drawPlot(switchNo,portNo,portFlag,x,y,yLabel,occurrence): 
    global inputBarDraw
    # print("Switch no: "+str(switchNo))
    # print("Port no: "+str(portNo))
    if inputBarDraw == 0:
        msgSize = processMessageInput()
        dataRateList = plotInputDataRate(msgSize, args.mRate, occurrence, 1)
        dataRateList = [x / 1000000 for x in dataRateList]

#         plt.figure(figsize=(3,3))
        if portFlag != "rx pkts" or portFlag != "tx pkts":
            plt.plot(x,dataRateList,label = "input")
            inputBarDraw = 1
    plt.plot(x,y, label = "S-" +str(switchNo)+" P-"+str(portNo))
    plt.xlabel('Time (s)', fontproperties=font)
    if portFlag == "rx pkts" or portFlag == "tx pkts":
        plt.ylabel('Throughput (pkts/s)', fontproperties=font)
    else:
        plt.ylabel('Throughput (Mbytes/s)', fontproperties=font)


    plt.xticks(fontproperties=font)
    plt.yticks(fontproperties=font)

#     plt.ylim([0,3.5])           # to limit the Y-axis value

    if portFlag=="bytes":
        plt.title(args.portType+" rx bytes("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)")
    else:
        plt.title(args.portType+" " + portFlag+"("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)") 

    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')

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
    
    return newBandwidthSum, timeList

#for aggregated plot of all host entry ports
def plotAggregatedBandwidth(scenario, label, color, ls, lw, cap):   
    msgSize = processMessageInput()
    aggThroughputList, timeList = overheadCheckPlot("bytes", msgSize, scenario, label, color, ls, lw, cap)
    return aggThroughputList, timeList
       
#parsing the sigle port        
def parseInput(portSwitchId):
    portParams = portSwitchId.split('-')
    switchId = portParams[0].split('S')[1]
    portId = portParams[1].split('P')[1]

    return int(portId), int(switchId)

def drawIndividualBandwidth(portId, switchId, portFlag):
    bandwidth, occurrence, maxBandwidth = getStatsValue(switchId,portId, portFlag)        # Here portId=1 is the fixed entry port of hosts
    timeList = list(range(0,occurrence*interval,interval))
    if portFlag=="rx pkts" or portFlag=="tx pkts":
        drawPlot(switchId,portId,portFlag,timeList, bandwidth, "Bandwidth (pkts/sec)", occurrence)
    elif portFlag=="bytes":
        newBandwidth = [x / 1000000 for x in bandwidth]
        drawPlot(switchId,portId,portFlag,timeList, newBandwidth, "Received Bandwidth (Mbytes/s)", occurrence)
    else:    
        newBandwidth = [x / 1000000 for x in bandwidth]
        drawPlot(switchId,portId,portFlag,timeList, newBandwidth, "Transmitted Bandwidth (Mbytes/s)", occurrence)
        
    
    if portFlag=="bytes":
        plt.savefig(logDirectory+args.portType+" rx bytes("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication).png",bbox_inches="tight")
    else:    
        plt.savefig(logDirectory+args.portType+" "+portFlag+"("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication).png",bbox_inches="tight") 
        

def plotIndividualPortBandwidth():
    portParams = args.switchPorts.split(',')
    for ports in portParams:
        portId, switchId = parseInput(ports)
#         if switchId not in leaderReplicaList:                #to skip plotting the leader replicas
        # print("S"+str(switchId)+"-P"+str(portId))
        drawIndividualBandwidth(portId, switchId, "bytes")
    
    clearExistingPlot()
    
    for ports in portParams:
        portId, switchId = parseInput(ports)
        drawIndividualBandwidth(portId, switchId, "tx bytes")

    clearExistingPlot()
            
    for ports in portParams:
        portId, switchId = parseInput(ports)
        drawIndividualBandwidth(portId, switchId, "rx pkts")
        
    clearExistingPlot()
            
    for ports in portParams:
        portId, switchId = parseInput(ports)
        drawIndividualBandwidth(portId, switchId, "tx pkts")        
        
    clearExistingPlot()

# if __name__ == '__main__': 
parser = argparse.ArgumentParser(description='Script for plotting individual port log.')
parser.add_argument('--number-of-switches', dest='switches', type=int, default=10,
                help='Number of switches')
parser.add_argument('--switch-ports', dest='switchPorts', type=str, default='S1-P1,S2-P1,S3-P1,S4-P1,S5-P1,S6-P1,S7-P1,S8-P1,S9-P1,S10-P1', help='Plot bandwidth vs time in a port wise and aggregated manner')
parser.add_argument('--port-type', dest='portType', default="access-port", type=str, help='Plot bandwidth for access/trunc ports')
parser.add_argument('--message-size', dest='mSizeString', type=str, default='fixed,10', help='Message size distribution (fixed, gaussian)')
parser.add_argument('--message-rate', dest='mRate', type=float, default=30.0, help='Message rate in msgs/second')
parser.add_argument('--ntopics', dest='nTopics', type=int, default=2, help='Number of topics')
parser.add_argument('--replication', dest='replication', type=int, default=10, help='Replication factor')
parser.add_argument('--nzk', dest='nZk', type=int, default=0, help='Kafka/Kraft')
parser.add_argument('--log-dir', dest='logDir', type=str, default='use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/scenario-1', help='Producer log directory')
parser.add_argument('--scenario-list', dest='scenarioStr', type=str, help='Comma separated list of scenarios')
parser.add_argument('--link-bw', dest='linkBW', type=int, default=10, help='Comma separated list of scenarios')

args = parser.parse_args()

logDirectory = args.logDir
scenarioStr = args.scenarioStr
scenarioList = scenarioStr.split(',')

plotIndividualPortBandwidth()           #for individual entry port plots
print("Individual "+args.portType+" bandwidth consumption plot created")

clearExistingPlot()
colorLst = ['r','g','b', 'y','k','m']
for index, item in enumerate(scenarioList):
    logDirectory = args.logDir + "/" + str(args.linkBW) +"Mbps/scenario-"+item + "msgPs/bandwidth/"
    # ls can be solid or dashed 
    aggThroughputList, timeList = plotAggregatedBandwidth(scenario=int(item), label=item+" msg/s", color=colorLst[index], ls='solid', lw=3.0, cap=100.0)   # cap 9.0 can be used to discard outliers
    # store aggregated throughput data in a file
    with open(logDirectory+'aggregated-throughput.txt', 'w') as f:
        for i in range(len(aggThroughputList)):
            f.write(str(timeList[i]) + " " + str(aggThroughputList[i]) + "\n")

# plt.savefig("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/plots/10Mbps-combinedThroughput", bbox_inches="tight")
filePath= args.logDir.replace('logs','plots')+"/"+ str(args.linkBW)+"Mbps-combinedThroughput"
plt.savefig(filePath+".pdf", format='pdf', bbox_inches="tight")