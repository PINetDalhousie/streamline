
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_axes([0.14,0.16,0.8,0.8])

x = [1000, 2000, 3000, 4000]
agg_throughput_sim = [6.4, 10.4, 12, 13.6]
# agg_throughput_testbed = []

plt.plot(x, agg_throughput_sim, label='stream2gym', marker='^', linewidth=4.0, markersize=10.0)
# plt.plot(x, agg_throughput_testbed, label='Hardware', marker='o', linewidth=4.0, linestyle='dotted', color='red', markersize=10.0)

plt.xlabel("Message rate (msg/s)", labelpad=9, fontweight='bold', fontsize=22)
plt.ylabel("Tx throughput (Mbps)", labelpad=10, fontweight='bold', fontsize=22)

plt.legend(loc="upper left", frameon=False, fontsize=18)

plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

ax = plt.gca()
ax.xaxis.set_ticks(np.arange(1000, 4001, 1000))
ax.yaxis.set_ticks(np.arange(0, 16, 3))
ax.set_ylim([0, 16])
ax.set_xlim([1000, 4000])

#plt.show()
plt.savefig('evaluation/accuracy-analysis/military-coordination/plots/throughput-accuracy.pdf')