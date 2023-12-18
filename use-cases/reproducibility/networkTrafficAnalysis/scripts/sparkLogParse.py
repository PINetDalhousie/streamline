#!/usr/bin/python3
# command to run this script: sudo python3 sparkLogParse.py <spark log file path>

import re
import sys

logDir = sys.argv[1]

def calcQueryPlanning(logDir):
    execTimes = []
    with open(logDir, 'r') as fp:
            lines = fp.readlines()
            searchWord = '\'durationMs\': '
            #'\'durationMs\': '
            for row in lines:
                if searchWord in row:
                    # print(row)
                    # print("\n")
                    durationString = row.split(searchWord)[1].split('}')[0]
                    
                    if 'queryPlanning' in durationString:
                        print(durationString)
                        addBatchTime = int(durationString.split('\'addBatch\': ')[1].split(',')[0])
                        getBatchTime = int(durationString.split('\'getBatch\': ')[1].split(',')[0])
                        latestOffsetTime = int(durationString.split('\'latestOffset\': ')[1].split(',')[0])
                        queryPlanningTime = int(durationString.split('\'queryPlanning\': ')[1].split(',')[0])
                        triggerExecutionTime = int(durationString.split('\'triggerExecution\': ')[1].split(',')[0])
                        walCommitTime = int(durationString.split('\'walCommit\': ')[1].split(',')[0])

                        totalTime = addBatchTime+getBatchTime+latestOffsetTime+queryPlanningTime+triggerExecutionTime+walCommitTime
                        execTime = triggerExecutionTime - walCommitTime
                        execTimes.append(execTime)

    print('Execution times in ms: ')
    print(*execTimes)

    totalExecTime = 0
    for index,eTime in enumerate(execTimes):
        if index != 0:
            totalExecTime += eTime

    avgExexTime = totalExecTime/(len(execTimes)-1)
    print('average time after reaching steady state(in ms):  '+str(avgExexTime))

def calcTriggerExec(logDir):
    execTimes = []
    with open(logDir, 'r') as fp:
            lines = fp.readlines()
            searchWord = '\'durationMs\': '
            #'\'durationMs\': '
            for row in lines:
                if searchWord in row:
                    # print(row)
                    # print("\n")
                    durationString = row.split(searchWord)[1].split('}')[0]
                    
                    if 'triggerExecution' in durationString:
                        print(durationString)
                        triggerExecutionTime = int(durationString.split('\'triggerExecution\': ')[1].split(',')[0])
                        execTimes.append(triggerExecutionTime)

    print('Execution times in ms: ')
    print(*execTimes)
    print('Trigger execution count: '+str(len(execTimes)))

    totalExecTime = 0
    for index,eTime in enumerate(execTimes):
        if index != 0:
            totalExecTime += eTime

    avgExexTime = totalExecTime/(len(execTimes))
    print('average spark execution time after reaching steady state(in ms):  '+str(avgExexTime))

# calculating trigger execution for all logs
calcTriggerExec(logDir)

# calculating trigger execution only for the logs that have query planning, wal commit in it
# calcQueryPlanning