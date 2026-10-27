# Import matplotlib and numpy
import matplotlib.pyplot as plt
import numpy as np

# Define the experiment data
x_10 = [30, 150, 300] # Message rate for 10 Mbps
y_10 = [4, 10.4, 21.6] # Aggregated Rx throughput (Mbps) for 10 Mbps
x_20 = [100, 300, 500, 600] # Message rate for 20 Mbps
y_20 = [12.8, 32, 42.4, 44.8] # Aggregated Rx throughput (Mbps) for 20 Mbps
x_400 = [2000, 4000, 6000, 8000] # Message rate for 400 Mbps
y_400 = [64, 65.6, 66.4, 68] # Aggregated Rx throughput (Mbps) for 400 Mbps 

# Create a scatter plot
plt.scatter(x_10, y_10, color='blue', marker='o', label='10 Mbps') # Blue circles for 10 Mbps
plt.scatter(x_20, y_20, color='green', marker='^', label='20 Mbps') # Green triangles for 20 Mbps
plt.scatter(x_400, y_400, color='red', marker='s', label='400 Mbps') # Red squares for 400 Mbps

# Add labels and title
plt.xlabel('Message rate (msg/s)')
plt.ylabel('Aggregated Rx throughput (Mbps)')
plt.title('Scatter Plot of Aggregated Throughput and Message Rate')
plt.legend() # Add a legend to show the meaning of the colors and shapes

# Show the plot
# plt.show()

# Save the plot
plt.savefig("use-cases/varying-networking-conditions/varying-link-bw/military-coordination/plots/msgRate-throughput-scatterPlot", bbox_inches="tight")

