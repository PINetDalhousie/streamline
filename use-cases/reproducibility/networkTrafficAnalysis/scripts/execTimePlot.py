#!/bin/usr/python3

# command to run: 
# sudo python3 use-cases/reproducibility/networkTrafficAnalysis/scripts/execTimePlot.py

# =================== journal paper experiment results (considering Spark trigger execution time)===================
import matplotlib.pyplot as plt
import numpy as np

nConcurrentUsers = [20, 40, 60, 80, 100]
# data
origAvgExecTimeWorker1 = np.array([2, 3, 3.25, 3.5, 3.6])
origAvgExecTimeWorker2 = np.array([0.5, 0.7, 0.8, 1, 1.9])
origAvgExecTimeWorker3 = np.array([0.4, 0.5, 0.7, 0.9, 1.7])

s2gAvgExecTimeWorker1 = np.array([3750.18, 5225.75, 5793.75, 5995.32, 7100.25])
s2gAvgExecTimeWorker2 = np.array([2549.19, 3272.77, 3971.19, 4827.34, 6378.64])
s2gAvgExecTimeWorker3 = np.array([2398.92, 2960.01, 3282.86, 4282.38, 5802.92])

# Normalize the data
s2gAvgExecTimeWorker1 /= s2gAvgExecTimeWorker1[0]
s2gAvgExecTimeWorker2 /= s2gAvgExecTimeWorker2[0]
s2gAvgExecTimeWorker3 /= s2gAvgExecTimeWorker3[0]

origAvgExecTimeWorker1 /= origAvgExecTimeWorker1[0]
origAvgExecTimeWorker2 /= origAvgExecTimeWorker2[0]
origAvgExecTimeWorker3 /= origAvgExecTimeWorker3[0]

# Create a plot
plt.plot(nConcurrentUsers, s2gAvgExecTimeWorker1, 's', linestyle='solid', label='stream2gym (one worker)')
plt.plot(nConcurrentUsers, origAvgExecTimeWorker1, 'v', linestyle='dashed', label='Ocampo et al. (one worker)')
plt.plot(nConcurrentUsers, s2gAvgExecTimeWorker2, 's', linestyle='solid', label='stream2gym (two Workers)')
plt.plot(nConcurrentUsers, origAvgExecTimeWorker2, 'v', linestyle='dashed', label='Ocampo et al. (two Workers)')
plt.plot(nConcurrentUsers, s2gAvgExecTimeWorker3, 's', linestyle='solid', label='stream2gym (three workers)')
plt.plot(nConcurrentUsers, origAvgExecTimeWorker3, 'v', linestyle='dashed', label='Ocampo et al. (three workers)')

plt.xlabel('Concurrent users', fontsize=22, fontweight='bold')
plt.ylabel('Normalized runtime (x1)', fontsize=22, fontweight='bold')

#plt.title('Distributed streaming processing execution time',fontsize=20)
plt.legend(loc="upper left", frameon=True, fontsize=10)
# plt.legend(loc="lower right", frameon=True, fontsize=10)

ax = plt.gca()

ax.set_xticks(np.arange(0, 101, step=20))
ax.xaxis.set_tick_params(labelsize=18)
#ax.set_yticks(np.arange(1.0, 2.1, step=0.25))
ax.yaxis.set_tick_params(labelsize=18)

plt.xlim((20, 102))

plt.savefig("use-cases/reproducibility/networkTrafficAnalysis/plots/reprod-network-monitoring.pdf",format='pdf', bbox_inches="tight")


# =================== journal paper experiment results (considering subtraction of Spark total time & topic duplicate time)===================
'''
import matplotlib.pyplot as plt
import numpy as np

nConcurrentUsers = [20, 40, 60, 80, 100]
topicDuplicateAvgLatency = np.array([917.91, 981.51, 1207.7, 1330.95, 1555.14])
# data
origAvgExecTimeWorker1 = np.array([2, 3, 3.25, 3.5, 4.5])
origAvgExecTimeWorker2 = np.array([0.5, 0.7, 0.8, 1, 1.9])
origAvgExecTimeWorker3 = np.array([0.4, 0.5, 0.7, 0.9, 1.7])

# Spark end to end average latency
s2gSparkAvgLatencyWorker1 = np.array([8613.97, 9792.58, 10174.46, 10310.50, 10518.31])
s2gSparkAvgLatencyWorker2 = np.array([6014.33, 6875.84, 7405.45, 7409.13, 7721.86])
s2gSparkAvgLatencyWorker3 = np.array([6106.84, 6699.88, 6572.52, 7021.98, 7061.31])

# Measure Spark average execution time
s2gAvgExecTimeWorker1 = s2gSparkAvgLatencyWorker1 - topicDuplicateAvgLatency
s2gAvgExecTimeWorker2 = s2gSparkAvgLatencyWorker2 - topicDuplicateAvgLatency
s2gAvgExecTimeWorker3 = s2gSparkAvgLatencyWorker3 - topicDuplicateAvgLatency

# Normalize the data
s2gAvgExecTimeWorker1 /= s2gAvgExecTimeWorker1[0]
s2gAvgExecTimeWorker2 /= s2gAvgExecTimeWorker2[0]
s2gAvgExecTimeWorker3 /= s2gAvgExecTimeWorker3[0]

origAvgExecTimeWorker1 /= origAvgExecTimeWorker1[0]
origAvgExecTimeWorker2 /= origAvgExecTimeWorker2[0]
origAvgExecTimeWorker3 /= origAvgExecTimeWorker3[0]

# Create a plot
plt.plot(nConcurrentUsers, s2gAvgExecTimeWorker1, 's', linestyle='solid', label='stream2gym (one worker)')
plt.plot(nConcurrentUsers, origAvgExecTimeWorker1, 'v', linestyle='dashed', label='Ocampo et al. (one worker)')
plt.plot(nConcurrentUsers, s2gAvgExecTimeWorker2, 's', linestyle='solid', label='stream2gym (two Workers)')
plt.plot(nConcurrentUsers, origAvgExecTimeWorker2, 'v', linestyle='dashed', label='Ocampo et al. (two Workers)')
plt.plot(nConcurrentUsers, s2gAvgExecTimeWorker3, 's', linestyle='solid', label='stream2gym (three workers)')
plt.plot(nConcurrentUsers, origAvgExecTimeWorker3, 'v', linestyle='dashed', label='Ocampo et al. (three workers)')

plt.xlabel('Concurrent users', fontsize=22, fontweight='bold')
plt.ylabel('Normalized runtime (x1)', fontsize=22, fontweight='bold')

#plt.title('Distributed streaming processing execution time',fontsize=20)
plt.legend(loc="upper left", frameon=True, fontsize=10)
# plt.legend(loc="lower right", frameon=True, fontsize=10)

ax = plt.gca()

ax.set_xticks(np.arange(0, 101, step=20))
ax.xaxis.set_tick_params(labelsize=18)
#ax.set_yticks(np.arange(1.0, 2.1, step=0.25))
ax.yaxis.set_tick_params(labelsize=18)

plt.xlim((20, 102))

plt.savefig("use-cases/reproducibility/networkTrafficAnalysis/plots/reprod-network-monitoring.pdf",format='pdf', bbox_inches="tight")
'''

# =================== stream2gym ICDCS 2023 experiment results===================
# import matplotlib.pyplot as plt
# fig = plt.figure()

# nConcurrentUsers = [20, 40, 60, 80, 100]
# avgExecTimeRound1 = [1585.595, 2074.278, 2420.265, 2587.151, 2432.62]
# plt.plot(nConcurrentUsers,avgExecTimeRound1,color='blue',linestyle='dotted')


# plt.xlabel('Concurrent users', fontsize=16)
# plt.ylabel('Average execution time(ms)', fontsize=16)
# plt.title('Distributed streaming processing execution time',fontsize=20)
# plt.legend()
# plt.show()

