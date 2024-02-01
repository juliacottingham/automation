import sys
check_mode=1
try: 
    import matplotlib as mlt 
    if check_mode: 
        mlt.use('TkAgg')
    else: 
        mlt.use('Agg')
    import matplotlib.pyplot as plt 
    import numpy as np
    import numpy.ma as ma
    import pandas as pd 
    import datetime as dt
except: 
    print('Please activate pmt_env.')
    sys.exit()

plt.ioff()

condition=0

def plotting_function(time_arr, temp_time_arr, data_arr, temp_arr, legend_item, ylabel, title, xlim): 
	fig, ax =plt.subplots()
	plt.plot(dt_array, data_arr)
	plt.legend([legend_item], loc=2)
	plt.title(title)
	ax2=ax.twinx()
	ax2.plot(temp_time_arr, temp_arr, color='orange')
	plt.legend(['Temperature'], loc=1)
	ax.set_ylabel(ylabel)
	ax2.set_ylabel('Temperature degrees Celsius')
	ax.set_xlim(xlim)
#path=sys.argv[1]

path='/data/disk01/home/julia/autocontrol/output_files/azimuth3_long_term_run10/processed_data'
file='occupancy.npy'

my_table=pd.read_excel('/data/disk01/home/julia/autocontrol/temperature/temp3.xls', skiprows=28, usecols=[0, 1, 2, 3])

init_col=np.array([*my_table.keys()])
final_col=np.array(["No.", "Time", "Temp", "Humidity"])
mapping_dict=dict(zip(init_col, final_col))

#my_table=my_table.rename(columns={0: "No.", 1: "Time", 2: "Temperature", 3: "Humidity"}) 

my_table=my_table.rename(columns=mapping_dict) 

#start_idx=int(my_table["No."][my_table["Time"]=="2023-05-26 11:26:18"]) -1
#end_idx=int(my_table["No."][my_table["Time"]=="2023-05-26 16:05:18"]) -1
start_idx=0
end_idx=len(my_table["No."])

plt.figure() 

plt.plot(my_table["Time"][start_idx:end_idx], my_table["Temp"][start_idx:end_idx])
plt.title("Temperature over Time") 
plt.ylabel("Temperature in Celsius")
plt.xlabel("Time")
plt.show(block=False)
condition=0

#file=sys.argv[2]
#check_mode=int(sys.argv[3])
file_2='fit_param.npy'
#file_2=sys.argv[4]

times=np.load(path+ '/' + file)[:, 0]
array=np.load(path + '/' + file)[:, 1:].astype(float)
array2=np.load(path + '/' + file_2)

led_v_array=np.load(path + '/led_v.npy')

dt_array=[]
for t in range(len(times)): 
    dt_array.append(dt.datetime.strptime(times[t], '%a %b %d %I:%M:%S %p EDT %Y'))
time2=[]
temp=my_table["Temp"][start_idx:end_idx]

for t in np.arange(start_idx, end_idx): 
    time=my_table["Time"][t]
    time2.append(dt.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))

xlim=[dt_array[0], dt_array[-1]]

popt_num=int((array2.shape[1]-1)/2)
sig_popt=array2[:, (-popt_num):]
array2=array2[sig_popt[:, 5]<0.1]
led_v_array=led_v_array[sig_popt[:, 5]<0.1]
dt_array=np.array(dt_array)
sig_popt=sig_popt[sig_popt[:, 5]<0.1]
dt_array2=dt_array[array2[:, 0].astype(int)-1]
#plotting_function(dt_array, time2, led_v_array[:, 1], temp, 'LED Charge', 'Average LED Charge (pC)', 'Average LED Charge (pC)', xlim) 

#plotting_function(dt_array, time2, led_v_array[:, 2], temp, 'LED Charge', 'Median LED Charge (pC)')

def plotting_function2(time, arr1, arr2, y_error, legend_arr, title, ylabel_arr): 
	
	fig, ax = plt.subplots()
	plt.plot(time, arr1)
	ax.legend([legend_arr[0]], loc=1)
	ax.set_ylabel(ylabel_arr[0])
	ax2=ax.twinx()
	ax2.errorbar(time, arr2, yerr=y_error, color='orange')
	ax2.set_ylabel(ylabel_arr[1])
	ax2.legend([legend_arr[1]], loc=2)
	plt.title(title)
	return fig, ax, ax2

plotting_function2(dt_array2, led_v_array[:, 1], array2[:, 5], sig_popt[:, 5], ['LED Charge', 'Avg PE'], 'Average LED Charge (pC)', ['Average LED Charge (pC)', 'Average PE'])

plotting_function2(dt_array2, led_v_array[:, 2], array2[:, 5], sig_popt[:, 5], ['LED Charge', 'Avg PE'], 'Median LED Charge (pC)', ['Median LED Charge (pC)', 'Average PE'])

plotting_function2(dt_array2, led_v_array[:, 3], array2[:, 5], sig_popt[:, 5], ['LED Charge', 'Avg PE'], 'Standard Deviation LED Charge (pC)', ['Standard Deviation LED Charge (pC)', 'Average PE'])
fig, ax, ax2 = plotting_function2(dt_array2, led_v_array[:, 4], array2[:, 5], sig_popt[:, 5], ['LED Voltage', 'Avg PE'], 'Average LED Peak Voltage (V)', ['Average LED Voltage (V)', 'Average PE'])
ax.invert_yaxis()

plotting_function2(dt_array2, led_v_array[:, 5], array2[:, 5], sig_popt[:, 5], ['LED Pulse Duration', 'Avg PE'], 'Average LED Pulse Duration (ns)', ['Average LED Pulse Duration (ns)', 'Average PE'])
plotting_function2(dt_array2, led_v_array[:, 6], array2[:, 5], sig_popt[:, 5], ['LED Pulse Duration', 'Avg PE'], 'Median LED Pulse Duration (ns)', ['Median LED Pulse Duration (ns)', 'Average PE'])
plotting_function2(dt_array2, led_v_array[:, 7], array2[:, 5], sig_popt[:, 5], ['LED Pulse Duration', 'Avg PE'], 'Standard Deviation of LED Pulse Duration (ns)', ['Standard Deiviation of LED Pulse Duration (ns)', 'Average PE'])






"""
plt.figure()
plt.plot(dt_array, led_v_array[:, 1])
plt.title('Average LED Charge (pC)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 2])
plt.title('Median LED Charge (pC)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
fig, ax2= plt.subplots()
plt.plot(dt_array, led_v_array[:, 3])
plt.title('Standard Deviation of  LED Charge (pC)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 4])
plt.title('Average LED Peak (V)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 5])
plt.title('Average LED Duration (ns)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 6])
plt.title('Median LED Duration (ns)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 7])
plt.title('Standard Deviation of LED Duration (ns)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
"""
plt.show(block=False)
