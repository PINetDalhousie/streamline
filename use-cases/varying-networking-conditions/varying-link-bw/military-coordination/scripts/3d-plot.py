# command: python3 use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/3d-plot.py
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.lines import Line2D

# ***************** User input *******************
link_bandwidth_input = input("Enter link bandwidth values separated by commas (default is 100,200,300,400): ")
message_rate_input = input("Enter message rate values separated by commas (default is 200,400,600,800,1000): ")

# Use default values if no input is provided
if link_bandwidth_input == "":
    link_bandwidth_input = "100,200,300,400"
if message_rate_input == "":
    message_rate_input = "200,400,600,800,1000"

# Convert the input strings to lists of integers
link_bandwidth = np.array([int(x) for x in link_bandwidth_input.split(",")])
message_rate = np.array([int(x) for x in message_rate_input.split(",")])

# Create X, Y and Z arrays
X = np.repeat(link_bandwidth[:, np.newaxis], len(message_rate), axis=1)
Y = np.tile(message_rate, (len(link_bandwidth), 1))
Z = [] # Aggregated throughput values (Mbps)


# # Log retrieval for 10, 20, 1000 Mbps link bandwidth values
# X = np.array([[10, 10, 10], [20, 20, 20], [1000, 1000, 1000]]) # Link bandwidth values (Mbps)
# Y = np.array([[30, 150, 300], [100, 300, 600], [300, 600, 900]]) # Message rate values 
# Z = [] # Aggregated throughput values (Mbps)

# ***************** Aggregated throughput log creation *******************
# Example command use-cases/varying-networking-conditions/varying-link-bw/military-coordination/scripts/combinedThroughput-by-varying-msgRate.py --log-dir use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs --link-bw 20 --scenario-list 300,500,600

# ***************** Aggregated throughput value extraction from logs *******************
for i, x_inner in enumerate(X):
    for y_value in Y[i]:
        # print("For X[{}][0] = {}, Y value is: {}".format(i, x_inner[0], y_value))
        with open('use-cases/varying-networking-conditions/varying-link-bw/military-coordination/logs/'+str(x_inner[0])+'Mbps/scenario-'+str(y_value)+'msgPs/bandwidth/aggregated-throughput.txt') as f:
                    # Read lines from the file
                    lines = f.readlines()
                    # Get the values after the space in each line
                    values = [float(line.split()[1]) for line in lines]
                    # print("Length of values: {}".format(len(values)))
                    # print("Max aggregated throughput value for X[{}][0] = {}, Y value = {} is: {}".format(i, x_inner[0], y_value, max(values)))
                    Z.append(values)
# Convert to Mbps
Z = [[value * 8 for value in inner_list] for inner_list in Z]
# print("Length of Z: {}".format(len(Z)))
# print(Z)

# # ***************** Shape matching *******************
# Ensure all inner lists in Z are of same length
Z_padded = []

# Find the minimum length of an inner list
min_length = min(len(inner_list) for inner_list in Z)  
for z_inner in Z:
    if len(z_inner) > min_length:
        # Truncate the list to the elements till min_length
        Z_padded.append(z_inner[:min_length])
    # elif len(z_inner) < min_length:
    #     # Pad the list with 0s to reach length min_length
    #     Z_padded.append(z_inner + [0]*(min_length - len(z_inner)))
    else:
        # If the list is already of length min_length, just append it as is
        Z_padded.append(z_inner)

Z = np.array(Z_padded)

# Flatten X and Y
X_flat = X.flatten()
Y_flat = Y.flatten()


# Repeat each element min_length times and reshape to (len(X_flat)*len(Y_flat), min_length)
X = np.repeat(X_flat, min_length).reshape(len(X_flat), min_length)
Y = np.repeat(Y_flat, min_length).reshape(len(Y_flat), min_length)
   

#******************** 3D plot generation *******************************        
fig = plt.figure() 
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap='viridis')
# wire_frame = ax.plot_wireframe(X, Y, Z)

ax.set_xlabel('Link bandwidth (Mbps)', labelpad=5, fontweight='bold', fontsize=10) 
ax.set_ylabel('Message rate (msg/s)', labelpad=5, fontweight='bold', fontsize=10) 
ax.set_zlabel('Aggregated Throughput (Mbps)', labelpad=5, fontweight='bold', fontsize=10) 
# ax.set_title('3D plot of three plots') 

# Rotate the plot
# ax.view_init(elev=30, azim=120)

# plt.show()
plt.savefig('use-cases/varying-networking-conditions/varying-link-bw/military-coordination/plots/3d-plot.pdf', format="pdf", dpi=300, bbox_inches='tight')