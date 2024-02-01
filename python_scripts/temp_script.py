import matplotlib as mlt
mlt.use('TkAgg')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd 
my_table=pd.read_excel('/home/labwork/autocontrol/temperature/temp1.xls', skiprows=28, usecols=[0, 1, 2, 3])

init_col=np.array([*my_table.keys()])
final_col=np.array(["No.", "Time", "Temp", "Humidity"])
mapping_dict=dict(zip(init_col, final_col))

#my_table=my_table.rename(columns={0: "No.", 1: "Time", 2: "Temperature", 3: "Humidity"}) 

my_table=my_table.rename(columns=mapping_dict) 

start_idx=int(my_table["No."][my_table["Time"]=="2023-05-26 16:26:18"]) -1
end_idx=int(my_table["No."][my_table["Time"]=="2023-05-27 03:05:18"]) -1

plt.figure() 

plt.plot(my_table["Time"][start_idx:end_idx], my_table["Temp"][start_idx:end_idx])
plt.title("Temperature over Time") 
plt.ylabel("Temperature in Celsius")
plt.xlabel("Time")
plt.show(block=False)
