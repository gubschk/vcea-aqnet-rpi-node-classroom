from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import socket
#Plotting variables and functions    
plt.style.use('fivethirtyeight')
x_vals = []
y_vals = []
index = count()
fieldnames = ["Time", "CO2"]
def animate(i):
    data = pd.read_csv('/run/aqnet/CO2-plot/CO2-plot.csv')
    time = data['Time']
    co2 = data['CO2']

    plt.cla()

    plt.plot(time, co2, label='AQ Sensor 2')
    plt.title(socket.gethostname() + ' CO2 data versus time')
    plt.xlabel('Time (s)')
    plt.ylabel('CO2 (ppm)')

    #plt.legend(loc='upper right')
    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()
