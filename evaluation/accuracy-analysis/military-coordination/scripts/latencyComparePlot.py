import matplotlib.pyplot as plt
import numpy as np
import os

fig = plt.figure()
ax = fig.add_axes([0.14,0.16,0.8,0.8])

x = [100, 200, 300]
testbedLatency = []
simLatency = []

# parsing testbed data to access the latency values
testbedDir = "../logs/testbed-logs/"
for item in x:
    # parsing the testbed data
    dirs = os.listdir(testbedDir + str(item)+"ms")
    for dir in dirs:
        latencyData = open(testbedDir + str(item)+"ms" + "/" + dir + "/latencyAvg.txt", "r")
        avgLatencyLst = []
        for line in latencyData:
            if "Average latency: " in line:
                # print('Average latency for '+ str(item) + "ms " + str(dir) + " is " + line.split("Average latency: ")[1])
                avgLatency = line.split("Average latency: ")[1].split(" ")[0]
                avgLatencyLst.append(float(avgLatency))
        latencyData.close()
    # print average latency
    testbedLatency.append(np.mean(avgLatencyLst))

for index,item in enumerate(testbedLatency):
    print("Testbed experiment average latency for " + str(x[index]) + "ms link delay experiment: " + str(item) + " seconds")

print("=====================================================================================================")
# parsing testbed data to access the latency values
simDir = "../logs/simulation-logs/"
for item in x:
    # parsing the testbed data
    dirs = os.listdir(simDir + str(item)+"ms")
    for dir in dirs:
        latencyData = open(simDir + str(item)+"ms" + "/" + dir + "/output/latencyAvg.txt", "r")
        avgLatencyLst = []
        for line in latencyData:
            if "Average latency: " in line:
                # print('Average latency for '+ str(item) + "ms " + str(dir) + " is " + line.split("Average latency: ")[1])
                avgLatency = line.split("Average latency: ")[1].split(" ")[0]
                avgLatencyLst.append(float(avgLatency))
        latencyData.close()
    # print average latency
    simLatency.append(np.mean(avgLatencyLst))

for index,item in enumerate(simLatency):
    print("Simulation experiment average latency for " + str(x[index]) + "ms link delay experiment: " + str(item) + " seconds")


plt.plot(x, simLatency, label='stream2gym', marker='^', linewidth=4.0, markersize=10.0)
plt.plot(x, testbedLatency, label='Hardware', marker='o', linewidth=4.0, linestyle='dotted', color='red', markersize=10.0)

plt.xlabel("Link delay (ms)", labelpad=9, fontweight='bold', fontsize=22)
plt.ylabel("End-to-end latency (s)", labelpad=10, fontweight='bold', fontsize=22)

plt.legend(loc="upper left", frameon=False, fontsize=18)

plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

ax = plt.gca()
ax.xaxis.set_ticks(np.arange(0, 301, 100))
ax.yaxis.set_ticks(np.arange(0, 16, 3))
ax.set_ylim([3, 15])
ax.set_xlim([100, 300])

#plt.show()
plt.savefig('../plots/military-coordination-accuracy.pdf')
